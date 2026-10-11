import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="SentinelGate — AI Agent Action Security Gateway",
    version="2.0.0"
)

# Enable CORS for Streamlit and local frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "sentinelgate.db"

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actions (
            action_id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            requester_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            target TEXT NOT NULL,
            arguments TEXT NOT NULL,
            decision TEXT NOT NULL,
            reason TEXT NOT NULL,
            action_hash TEXT NOT NULL,
            decision_path TEXT NOT NULL,
            status TEXT NOT NULL, -- PENDING, APPROVED, REJECTED, EXECUTED, BLOCKED
            approver_id TEXT,
            created_at TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            action_id TEXT NOT NULL,
            details TEXT NOT NULL,
            prev_hash TEXT NOT NULL,
            current_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- Helper: Audit Chain & Tamper-Evident Logging ---
def log_audit_event(event_type: str, action_id: str, details: dict):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT current_hash FROM audit_log ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    prev_hash = row[0] if row else "0" * 64

    timestamp = datetime.now(timezone.utc).isoformat()
    details_json = json.dumps(details, sort_keys=True)
    raw_str = f"{prev_hash}|{timestamp}|{event_type}|{action_id}|{details_json}"
    current_hash = hashlib.sha256(raw_str.encode()).hexdigest()

    cursor.execute("""
        INSERT INTO audit_log (timestamp, event_type, action_id, details, prev_hash, current_hash)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (timestamp, event_type, action_id, details_json, prev_hash, current_hash))
    conn.commit()
    conn.close()

# --- Pydantic Models ---
class ActionEvaluateRequest(BaseModel):
    agent_id: str = Field(..., description="Unique identifier of the AI agent proposing the action")
    requester_id: str = Field(..., description="User or entity triggering the agent")
    action_type: str = Field(..., description="Type of action (e.g., update_record, create_ticket, delete_record)")
    target: str = Field(..., description="Target resource identifier")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Action arguments and payload")

class ApprovalRequest(BaseModel):
    approver_id: str = Field(..., description="Human approver ID (must not match requester)")
    reason: Optional[str] = Field(None, description="Optional notes or rejection justification")

class ExecutionRequest(BaseModel):
    executor_id: Optional[str] = Field("operator-01", description="Operator executing the approved action")

# --- Helper: Canonical SHA-256 Hashing ---
def compute_action_hash(action_type: str, target: str, arguments: Dict[str, Any]) -> str:
    canonical_data = {
        "action_type": action_type,
        "target": target,
        "arguments": arguments
    }
    raw_json = json.dumps(canonical_data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(raw_json.encode()).hexdigest()

# --- Comprehensive Policy Engine ---
VALID_AGENTS = {
    "agent-01": {"allowed_actions": ["update_record", "create_ticket", "delete_record", "transfer_funds"], "max_records": 10},
    "agent-02": {"allowed_actions": ["update_record", "transfer_funds"], "max_records": 1}
}
SUPPORTED_ACTIONS = ["update_record", "create_ticket", "delete_record", "transfer_funds"]

def evaluate_policy(agent_id: str, action_type: str, target: str, arguments: dict):
    # 1. Unknown Agent => BLOCK
    if agent_id not in VALID_AGENTS:
        return "BLOCK", f"Unknown or unauthorized agent ID '{agent_id}'", "deterministic_rules"
    
    # 2. Unknown Action Type / Destructive drops => BLOCK
    if action_type not in SUPPORTED_ACTIONS or "drop" in action_type.lower():
        return "BLOCK", f"Unrecognized or forbidden action type '{action_type}'", "deterministic_rules"

    agent_config = VALID_AGENTS[agent_id]

    # 3. Missing explicit agent permission => BLOCK
    if action_type not in agent_config["allowed_actions"]:
        return "BLOCK", f"Agent '{agent_id}' is not permitted to perform '{action_type}'", "deterministic_rules"

    # 4. Argument Security Checks (e.g. bulk modifications / dangerous payloads)
    if action_type == "update_record" and arguments.get("field") in ["password", "is_admin", "role"]:
        return "BLOCK", f"Forbidden security modification on protected field '{arguments.get('field')}'", "deterministic_rules"

    # 5. Destructive or High-Impact Operations => HOLD for Human Approval
    if action_type in ["delete_record", "transfer_funds"] or "database" in target.lower():
        return "HOLD", "High-impact or destructive action requires explicit human authorization", "deterministic_rules"

    # 6. Default permitted operation => ALLOW
    return "ALLOW", "Action successfully permitted by deterministic security policy", "deterministic_rules"

# --- API Endpoints ---
@app.get("/health")
def health_check():
    return {"status": "ok", "version": "2.0.0"}

@app.post("/actions/evaluate")
def evaluate_action(req: ActionEvaluateRequest):
    action_hash = compute_action_hash(req.action_type, req.target, req.arguments)
    action_id = f"act-{hashlib.md5(action_hash.encode()).hexdigest()[:8]}"

    decision, reason, decision_path = evaluate_policy(
        req.agent_id, req.action_type, req.target, req.arguments
    )

    initial_status = "PENDING" if decision == "HOLD" else ("APPROVED" if decision == "ALLOW" else "BLOCKED")
    created_at = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO actions 
        (action_id, agent_id, requester_id, action_type, target, arguments, decision, reason, action_hash, decision_path, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        action_id, req.agent_id, req.requester_id, req.action_type, req.target,
        json.dumps(req.arguments), decision, reason, action_hash, decision_path, initial_status, created_at
    ))
    conn.commit()
    conn.close()

    log_audit_event("EVALUATE", action_id, {
        "agent_id": req.agent_id,
        "requester_id": req.requester_id,
        "action_type": req.action_type,
        "target": req.target,
        "decision": decision,
        "reason": reason,
        "action_hash": action_hash
    })

    return {
        "action_id": action_id,
        "decision": decision,
        "reason": reason,
        "action_hash": action_hash,
        "decision_path": decision_path
    }

@app.get("/actions/pending")
def list_pending_actions():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM actions WHERE status = 'PENDING' ORDER BY created_at ASC")
    rows = cursor.fetchall()
    conn.close()
    
    # Parse JSON arguments back to dict for clean frontend rendering
    result = []
    for row in rows:
        d = dict(row)
        try:
            d["arguments"] = json.loads(d["arguments"])
        except Exception:
            pass
        result.append(d)
    return result

@app.post("/actions/{id}/approve")
def approve_action(id: str, req: ApprovalRequest):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM actions WHERE action_id = ?", (id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Action not found")

    if row["status"] != "PENDING":
        conn.close()
        raise HTTPException(status_code=400, detail=f"Action is in status '{row['status']}', cannot approve.")

    # Separation of Duties: Requester cannot approve their own action
    if row["requester_id"] == req.approver_id:
        log_audit_event("SELF_APPROVAL_REJECTED", id, {"approver_id": req.approver_id})
        conn.close()
        raise HTTPException(status_code=403, detail="Security violation: Requesters cannot approve their own actions.")

    cursor.execute("UPDATE actions SET status = 'APPROVED', approver_id = ? WHERE action_id = ?", (req.approver_id, id))
    conn.commit()
    conn.close()

    log_audit_event("APPROVE", id, {"approver_id": req.approver_id})
    return {"status": "success", "message": f"Action {id} approved successfully by {req.approver_id}"}

@app.post("/actions/{id}/reject")
def reject_action(id: str, req: ApprovalRequest):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM actions WHERE action_id = ?", (id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Action not found")

    cursor.execute("UPDATE actions SET status = 'REJECTED' WHERE action_id = ?", (id,))
    conn.commit()
    conn.close()

    log_audit_event("REJECT", id, {"rejecter_id": req.approver_id, "reason": req.reason})
    return {"status": "success", "message": f"Action {id} rejected."}

@app.post("/actions/{id}/execute")
def execute_action(id: str, req: Optional[ExecutionRequest] = None):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM actions WHERE action_id = ?", (id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Action not found")

    if row["status"] != "APPROVED":
        conn.close()
        raise HTTPException(status_code=400, detail=f"Action cannot be executed. Current status: {row['status']}")

    # Cryptographic Revalidation: Recompute hash to detect parameter tampering after approval
    current_hash = compute_action_hash(row["action_type"], row["target"], json.loads(row["arguments"]))
    if current_hash != row["action_hash"]:
        conn.close()
        log_audit_event("TAMPERING_DETECTED", id, {"stored_hash": row["action_hash"], "computed_hash": current_hash})
        raise HTTPException(status_code=403, detail="Security violation: Action arguments or target were modified after approval!")

    cursor.execute("UPDATE actions SET status = 'EXECUTED' WHERE action_id = ?", (id,))
    conn.commit()
    conn.close()

    log_audit_event("EXECUTE", id, {"target": row["target"], "action_type": row["action_type"]})
    return {"status": "success", "message": f"Action {id} verified and executed successfully."}

@app.get("/audit")
def get_audit_log():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_log ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/audit/verify")
def verify_audit_chain():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_log ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()

    prev_hash = "0" * 64
    for idx, row in enumerate(rows):
        if row["prev_hash"] != prev_hash:
            return {
                "valid": False,
                "verified": False,
                "message": f"Previous hash pointer mismatch at event ID {row['id']}!"
            }
        raw_str = f"{row['prev_hash']}|{row['timestamp']}|{row['event_type']}|{row['action_id']}|{row['details']}"
        computed_hash = hashlib.sha256(raw_str.encode()).hexdigest()
        if computed_hash != row["current_hash"]:
            return {
                "valid": False,
                "verified": False,
                "message": f"Current hash mismatch detected at event ID {row['id']} (Log Tampering)!"
            }
        prev_hash = row["current_hash"]

    return {
        "valid": True,
        "verified": True,
        "message": f"100% Cryptographic Match — Chain Unbroken ({len(rows)} events verified)",
        "total_events_checked": len(rows)
    }