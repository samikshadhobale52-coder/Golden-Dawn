import streamlit as st
import requests
import json
import pandas as pd
from typing import Dict, Any, Optional, Tuple

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AuditGate — AI Quality & Compliance Gateway",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Custom Styling: Aesthetic Light Theme with AI/Security Visual Highlights
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #334155;
    }

    /* Clean Ice-Blue Light Canvas */
    .stApp {
        background-color: #f8fafc;
        background-image: 
            radial-gradient(at 0% 0%, #e0f2fe 0px, transparent 50%),
            radial-gradient(at 100% 100%, #e0e7ff 0px, transparent 50%);
    }

    /* Headings */
    h1, h2, h3, h4 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        letter-spacing: -0.025em;
    }

    /* Main Hero Headline & Subtext */
    .main-headline {
        font-size: 2.6rem;
        line-height: 1.2;
        background: linear-gradient(135deg, #0284c7 0%, #4f46e5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    .main-subtext {
        color: #475569;
        font-size: 1.05rem;
        max-width: 800px;
        margin-bottom: 24px;
        line-height: 1.6;
    }

    /* Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid #bae6fd;
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 25px -5px rgba(2, 132, 199, 0.05);
        height: 100%;
    }

    /* JSON Code Editor Box */
    .code-editor-box {
        background: #f1f5f9;
        padding: 16px;
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        font-family: monospace;
        font-size: 0.9rem;
        color: #0369a1;
        box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.03);
    }

    /* Checklist Items */
    .checklist-item {
        padding: 12px 16px;
        margin-bottom: 10px;
        border-radius: 10px;
        font-size: 0.9rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .check-pass {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #166534;
    }
    .check-fail {
        background: #fef2f2;
        border: 1px solid #fecaca;
        color: #991b1b;
    }
    .check-warn {
        background: #fffbeb;
        border: 1px solid #fef08a;
        color: #854d0e;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #f0f7ff;
        border-right: 1px solid #bae6fd;
    }

    /* Sidebar Logo */
    .sidebar-logo {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0284c7 0%, #4f46e5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
        padding-left: 4px;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #bae6fd;
        padding: 18px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.04);
    }
    div[data-testid="stMetricValue"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: #0284c7 !important;
    }

    /* Decision Verdict Boxes */
    .verdict-box {
        border-radius: 14px;
        padding: 20px;
        margin-top: 18px;
        border: 1.5px solid;
    }
    .verdict-allow {
        background: #f0fdf4;
        border-color: #22c55e;
        color: #15803d;
    }
    .verdict-hold {
        background: #fffbeb;
        border-color: #f59e0b;
        color: #b45309;
    }
    .verdict-block {
        background: #fef2f2;
        border-color: #ef4444;
        color: #b91c1c;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Sidebar Navigation & Controls
# -----------------------------------------------------------------------------
st.sidebar.markdown('<div class="sidebar-logo">AuditGate</div>', unsafe_allow_html=True)

nav_option = st.sidebar.radio(
    "Navigation Menu",
    [
        "Overview & Live Gatekeeper", 
        "Evaluate AI Output", 
        "Approval Queue", 
        "Audit Log", 
        "Execution Gateway"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Security Gatekeeper Controls")

comp_threshold = st.sidebar.slider("Compliance Threshold", 0, 100, 85)
safety_filter = st.sidebar.slider("Safety Filter", 0, 100, 90)
acc_tolerance = st.sidebar.slider("Accuracy Tolerance", 0, 100, 95)
toxicity_level = st.sidebar.slider("Toxicity Level", 0, 100, 10)

st.sidebar.toggle("Block Toxic Output", value=True)
st.sidebar.toggle("Require Dual-Signer for HOLD", value=False)

st.sidebar.markdown("---")

backend_url = st.sidebar.text_input(
    "Gateway Backend Endpoint",
    value="http://127.0.0.1:8000",
    help="Target API URL"
).rstrip('/')

def check_backend_health(url: str) -> bool:
    try:
        res = requests.get(f"{url}/health", timeout=2)
        if res.status_code == 200 and res.json().get("status") == "ok":
            return True
    except Exception:
        pass
    return False

is_backend_online = check_backend_health(backend_url)

if is_backend_online:
    st.sidebar.success("🟢 BACKEND ACTIVE")
else:
    st.sidebar.warning("🟡 MOCK MODE ACTIVE")

# Session State Setup
if "mock_pending" not in st.session_state:
    st.session_state["mock_pending"] = [
        {
            "action_id": "act-mock-001",
            "agent_id": "agent-01",
            "requester_id": "user-01",
            "action_type": "delete_database_table",
            "target": "production_db.users",
            "arguments": {"cascade": True},
            "decision": "HOLD",
            "reason": "Destructive operation requires human authorization",
            "timestamp": "2026-10-11T12:00:00Z"
        }
    ]

if "mock_audit" not in st.session_state:
    st.session_state["mock_audit"] = [
        {
            "timestamp": "2026-10-11T11:30:00Z",
            "action_id": "act-mock-000",
            "agent_id": "agent-01",
            "action_type": "update_record",
            "target": "customer-101",
            "decision": "ALLOW",
            "status": "EXECUTED"
        }
    ]

def make_api_request(method: str, path: str, json_data: Optional[Dict[str, Any]] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    url = f"{backend_url}{path}"
    try:
        response = requests.request(method, url, json=json_data, timeout=5)
        if response.status_code in [200, 201]:
            return response.json(), None
        else:
            return None, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return None, str(e)

# -----------------------------------------------------------------------------
# Main Headline Header
# -----------------------------------------------------------------------------
st.markdown("""
<div>
    <h1 class="main-headline">The Ultimate Gateway for AI Quality & Compliance</h1>
    <p class="main-subtext">
        Evaluate, audit, and approve AI-generated output before it goes live. 
        Ensure compliance, accuracy, and safety with real-time automated guardrails.
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# VIEW 1: OVERVIEW & LIVE GATEKEEPER
# -----------------------------------------------------------------------------
if nav_option == "Overview & Live Gatekeeper":
    # Aesthetic Feature Banner with High-Tech Illustration
    st.markdown("""
    <div class="glass-card" style="margin-bottom: 24px; padding: 20px 28px; background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="background: #e0f2fe; border: 1px solid #7dd3fc; color: #0369a1; padding: 4px 12px; border-radius: 20px; font-size: 0.78rem; font-weight: 700;">
                    ZERO-TRUST AI GUARDRAILS
                </span>
                <h3 style="margin: 10px 0 4px 0; color: #0f172a;">Active Policy Verification Pipeline</h3>
                <p style="margin: 0; color: #64748b; font-size: 0.9rem;">
                    Pre-execution governance ensuring deterministic rules and cryptographic non-repudiation.
                </p>
            </div>
            <div style="font-size: 2.8rem; line-height: 1;">🛡️</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("""
        <div class="glass-card">
            <h4 style="margin-top:0; color:#0284c7;">🤖 AI Output Payload Stream</h4>
            <p style="font-size:0.85rem; color:#64748b;">Ingested Code Stream</p>
            <div class="code-editor-box">
                {<br>
                &nbsp;&nbsp;"agent": "finance-bot",<br>
                &nbsp;&nbsp;"action": "wire_transfer",<br>
                &nbsp;&nbsp;"amount": 7500,<br>
                &nbsp;&nbsp;"recipient": "acct-9921"<br>
                }
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div class="glass-card">
            <h4 style="margin-top:0; color:#0284c7;">✅ Real-Time Rule Checklist</h4>
            <div class="checklist-item check-pass">
                🟢 Compliance Policy Check: PASSED
            </div>
            <div class="checklist-item check-pass">
                🟢 Data Privacy Leak Guard: PASSED
            </div>
            <div class="checklist-item check-fail">
                🔴 Financial Approval Limit ($1,000): EXCEEDED
            </div>
            <div class="checklist-item check-warn">
                ⚠️ Gatekeeper Action: ROUTED TO HUMAN HOLD QUEUE
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Real-Time Policy Telemetry")
    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
    c_m1.metric("Gateway State", "ONLINE" if is_backend_online else "SIMULATION")
    
    if is_backend_online:
        audit_data, _ = make_api_request("GET", "/audit")
        pending_data, _ = make_api_request("GET", "/actions/pending")
        events = audit_data if isinstance(audit_data, list) else []
        pending = pending_data if isinstance(pending_data, list) else []
        allows = sum(1 for e in events if e.get("decision") == "ALLOW")
        blocks = sum(1 for e in events if e.get("decision") == "BLOCK")
        holds = len(pending)
    else:
        allows = sum(1 for e in st.session_state["mock_audit"] if e.get("decision") == "ALLOW")
        blocks = sum(1 for e in st.session_state["mock_audit"] if e.get("decision") == "BLOCK")
        holds = len(st.session_state["mock_pending"])
    
    c_m2.metric("ALLOW Decisions", allows)
    c_m3.metric("BLOCK Decisions", blocks)
    c_m4.metric("HOLD Queued", holds)

# -----------------------------------------------------------------------------
# VIEW 2: EVALUATE AI OUTPUT
# -----------------------------------------------------------------------------
elif nav_option == "Evaluate AI Output":
    st.markdown("### Propose Action Payload for Policy Verification")
    
    st.markdown("**Test Scenarios:**")
    col_p1, col_p2, col_p3 = st.columns(3)
    
    preset = None
    if col_p1.button("🟢 Safe Action (ALLOW)"):
        preset = {
            "agent_id": "agent-01",
            "requester_id": "user-01",
            "action_type": "update_record",
            "target": "customer-101",
            "arguments": json.dumps({"field": "status", "value": "verified"}, indent=2)
        }
    if col_p2.button("🟡 High-Impact Financial (HOLD)"):
        preset = {
            "agent_id": "agent-02",
            "requester_id": "user-02",
            "action_type": "transfer_funds",
            "target": "acct-5501",
            "arguments": json.dumps({"amount": 7500, "currency": "USD"}, indent=2)
        }
    if col_p3.button("🔴 Forbidden Operation (BLOCK)"):
        preset = {
            "agent_id": "unauthorized-agent",
            "requester_id": "user-99",
            "action_type": "drop_table",
            "target": "production_db",
            "arguments": json.dumps({"force": True}, indent=2)
        }

    with st.form("evaluate_action_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            agent_id = st.text_input("Agent Identity", value=preset["agent_id"] if preset else "agent-01")
            action_type = st.text_input("Action Type", value=preset["action_type"] if preset else "update_record")
        with col_b:
            requester_id = st.text_input("Requester Identity", value=preset["requester_id"] if preset else "user-01")
            target = st.text_input("Target Resource", value=preset["target"] if preset else "customer-101")
        
        arguments_raw = st.text_area(
            "Payload Arguments (JSON)",
            value=preset["arguments"] if preset else '{\n  "field": "status",\n  "value": "verified"\n}',
            height=120
        )
        
        submit_btn = st.form_submit_button("🔒 Evaluate Action via AuditGate")

    if submit_btn:
        try:
            parsed_args = json.loads(arguments_raw)
            payload = {
                "agent_id": agent_id,
                "requester_id": requester_id,
                "action_type": action_type,
                "target": target,
                "arguments": parsed_args
            }

            if is_backend_online:
                result, err = make_api_request("POST", "/actions/evaluate", payload)
                if err:
                    st.error(f"Evaluation Error: {err}")
                else:
                    decision = result.get("decision", "UNKNOWN")
                    v_class = f"verdict-{decision.lower()}"
                    st.markdown(f"""
                    <div class="verdict-box {v_class}">
                        <h2 style="margin:0; color:inherit;">VERDICT: {decision}</h2>
                        <p style="margin:8px 0 0 0;"><strong>Reason:</strong> {result.get('reason')}</p>
                        <p style="margin:4px 0 0 0;"><strong>Action Hash:</strong> <code>{result.get('action_hash')}</code></p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                if "drop" in action_type.lower() or "unauthorized" in agent_id.lower():
                    decision = "BLOCK"
                    reason = "Forbidden operation: Action blocked by security baseline policy."
                elif "transfer" in action_type.lower() or "delete" in action_type.lower():
                    decision = "HOLD"
                    reason = "High-impact threshold exceeded. Sent to approval queue."
                else:
                    decision = "ALLOW"
                    reason = "Action compliant with baseline policy rules."

                v_class = f"verdict-{decision.lower()}"
                st.markdown(f"""
                <div class="verdict-box {v_class}">
                    <h2 style="margin:0; color:inherit;">VERDICT: {decision}</h2>
                    <p style="margin:8px 0 0 0;"><strong>Reason:</strong> {reason}</p>
                    <p style="margin:4px 0 0 0;"><strong>Action Hash:</strong> <code>sha256-e3b0c44298fc1c149afbf4c...</code></p>
                </div>
                """, unsafe_allow_html=True)

                if decision == "HOLD":
                    st.session_state["mock_pending"].append({
                        **payload,
                        "action_id": f"act-gen-{hash(agent_id + action_type) % 10000}",
                        "decision": "HOLD",
                        "reason": reason,
                        "timestamp": "Just now"
                    })

                st.session_state["mock_audit"].append({
                    "timestamp": "Just now",
                    "action_id": f"act-gen-{hash(agent_id + action_type) % 10000}",
                    "agent_id": agent_id,
                    "action_type": action_type,
                    "target": target,
                    "decision": decision,
                    "status": "EVALUATED"
                })

        except json.JSONDecodeError:
            st.error("Invalid JSON format in Payload Arguments field.")

# -----------------------------------------------------------------------------
# VIEW 3: APPROVAL QUEUE
# -----------------------------------------------------------------------------
elif nav_option == "Approval Queue":
    st.markdown("### Human Supervisor Authorization Queue")
    
    if is_backend_online:
        pending_list, err = make_api_request("GET", "/actions/pending")
        pending_list = pending_list if isinstance(pending_list, list) else []
    else:
        pending_list = st.session_state["mock_pending"]

    if not pending_list:
        st.info("Queue is empty. No actions currently pending human authorization.")
    else:
        for idx, item in enumerate(pending_list):
            action_id = item.get("action_id", f"unknown-{idx}")
            with st.expander(f"⚠️ ACTION PENDING: {action_id} — {item.get('action_type')}", expanded=True):
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.write(f"**Agent Identity:** `{item.get('agent_id')}`")
                    st.write(f"**Requester Identity:** `{item.get('requester_id')}`")
                    st.write(f"**Target Resource:** `{item.get('target')}`")
                with col_d2:
                    st.write(f"**Reason:** {item.get('reason')}")
                    st.json(item.get('arguments', {}))

                st.markdown("---")
                approver_id = st.text_input(
                    f"Supervisor Identity (Must differ from '{item.get('requester_id')}')",
                    key=f"approver_{action_id}"
                )
                reject_reason = st.text_input("Rejection Justification", key=f"reason_{action_id}")

                col_btn1, col_btn2 = st.columns(2)
                if col_btn1.button("✅ Approve Action", key=f"app_btn_{action_id}"):
                    if not approver_id.strip():
                        st.error("Please specify Supervisor Identity.")
                    elif approver_id.strip() == item.get("requester_id"):
                        st.error("Security Violation: Approver cannot match Requester.")
                    else:
                        if is_backend_online:
                            res, err = make_api_request("POST", f"/actions/{action_id}/approve", {"approver_id": approver_id})
                            if err:
                                st.error(f"Approval failed: {err}")
                            else:
                                st.success("Approved cleanly.")
                                st.rerun()
                        else:
                            st.session_state["mock_pending"] = [p for p in st.session_state["mock_pending"] if p.get("action_id") != action_id]
                            st.session_state["mock_audit"].append({
                                "timestamp": "Just now",
                                "action_id": action_id,
                                "agent_id": item.get("agent_id"),
                                "action_type": item.get("action_type"),
                                "target": item.get("target"),
                                "decision": "APPROVED",
                                "status": f"Approved by {approver_id}"
                            })
                            st.success("Approved (Mock Mode).")
                            st.rerun()

                if col_btn2.button("❌ Reject Action", key=f"rej_btn_{action_id}"):
                    if not approver_id.strip() or not reject_reason.strip():
                        st.error("Provide Supervisor Identity and Rejection Justification.")
                    else:
                        if is_backend_online:
                            res, err = make_api_request("POST", f"/actions/{action_id}/reject", {
                                "approver_id": approver_id,
                                "reason": reject_reason
                            })
                            if err:
                                st.error(f"Rejection failed: {err}")
                            else:
                                st.success("Rejected cleanly.")
                                st.rerun()
                        else:
                            st.session_state["mock_pending"] = [p for p in st.session_state["mock_pending"] if p.get("action_id") != action_id]
                            st.session_state["mock_audit"].append({
                                "timestamp": "Just now",
                                "action_id": action_id,
                                "agent_id": item.get("agent_id"),
                                "action_type": item.get("action_type"),
                                "target": item.get("target"),
                                "decision": "REJECTED",
                                "status": f"Rejected by {approver_id}"
                            })
                            st.success("Rejected (Mock Mode).")
                            st.rerun()

# -----------------------------------------------------------------------------
# VIEW 4: AUDIT LOG
# -----------------------------------------------------------------------------
elif nav_option == "Audit Log":
    st.markdown("### Cryptographic Audit Trail")
    
    col_v1, col_v2 = st.columns([3, 1])
    with col_v2:
        if st.button("🔍 Verify Cryptographic Chain Integrity"):
            if is_backend_online:
                v_res, err = make_api_request("GET", "/audit/verify")
                if err:
                    st.error(f"Verification Error: {err}")
                else:
                    if v_res.get("valid"):
                        st.success(f"✅ INTEGRITY VERIFIED: {v_res.get('message')}")
                    else:
                        st.error(f"❌ TAMPER DETECTED: {v_res.get('message')}")
            else:
                st.success("✅ INTEGRITY VERIFIED: 100% Cryptographic Match (Mock Mode)")

    if is_backend_online:
        audit_events, err = make_api_request("GET", "/audit")
        audit_events = audit_events if isinstance(audit_events, list) else []
    else:
        audit_events = st.session_state["mock_audit"]

    if audit_events:
        st.dataframe(pd.DataFrame(audit_events), use_container_width=True)
    else:
        st.info("No audit logs recorded.")

# -----------------------------------------------------------------------------
# VIEW 5: EXECUTION GATEWAY
# -----------------------------------------------------------------------------
elif nav_option == "Execution Gateway":
    st.markdown("### Controlled Execution Gateway")
    
    with st.form("execute_action_form"):
        exec_action_id = st.text_input("Approved Action ID", placeholder="e.g. act-mock-001")
        executor_id = st.text_input("Operator Identity", value="operator-01")
        submit_exec = st.form_submit_button("⚡ Trigger Controlled Execution")

    if submit_exec:
        if is_backend_online:
            res, err = make_api_request("POST", f"/actions/{exec_action_id}/execute", {"executor_id": executor_id})
            if err:
                st.error(f"Execution Denied by Gateway: {err}")
            else:
                st.success(f"✅ Execution Confirmed for {exec_action_id}")
                st.json(res)
        else:
            st.warning("⚠️ Execution Refused: Gateway is in offline demo mode. Unconfirmed actions cannot be executed.")