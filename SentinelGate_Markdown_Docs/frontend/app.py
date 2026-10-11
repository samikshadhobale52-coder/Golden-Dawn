import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import pandas as pd
from typing import Dict, Any, Optional, Tuple

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SentinelGate — AI Agent Security Gateway",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Custom Styling: Premium Light/White Theme
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif;
        color: #334155;
    }

    /* Base White Canvas */
    .stApp {
        background-color: #ffffff;
        background-image: radial-gradient(at 10% 10%, rgba(99, 102, 241, 0.05) 0px, transparent 50%),
                          radial-gradient(at 90% 90%, rgba(14, 165, 233, 0.04) 0px, transparent 50%);
    }

    /* Headings - Crisp Dark Slate */
    h1, h2, h3, h4 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        letter-spacing: -0.025em;
    }

    /* Hero Header Box */
    .hero-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 24px 32px;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.05);
    }
    .hero-title {
        font-size: 2.3rem;
        background: linear-gradient(135deg, #4f46e5 0%, #0284c7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero-subtitle {
        color: #64748b;
        font-size: 0.95rem;
        font-weight: 500;
        margin-top: 6px;
    }

    /* Metric Cards - Soft Slate Surfaces */
    div[data-testid="stMetric"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 18px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
    }
    div[data-testid="stMetricValue"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: #4f46e5 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Decision Verdict Boxes */
    .verdict-box {
        border-radius: 14px;
        padding: 22px;
        margin-top: 18px;
        border: 1.5px solid;
    }
    .verdict-allow {
        background: #ecfdf5;
        border-color: #10b981;
        color: #047857;
    }
    .verdict-hold {
        background: #fffbeb;
        border-color: #f59e0b;
        color: #b45309;
    }
    .verdict-block {
        background: #fff1f2;
        border-color: #f43f5e;
        color: #be123c;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }

    /* Radio Navigation Tabs */
    div[data-testid="stRadio"] > label {
        display: none;
    }
    div[data-testid="stRadio"] > div {
        flex-direction: row;
        gap: 12px;
        background: #f1f5f9;
        padding: 8px;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
    }
    div[data-testid="stRadio"] label {
        background: transparent;
        padding: 10px 20px;
        border-radius: 10px;
        color: #64748b;
        font-weight: 600;
        border: none;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    div[data-testid="stRadio"] label:hover {
        color: #0f172a;
        background: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3D Node Sphere Component (Light Canvas Compatible)
# -----------------------------------------------------------------------------
def render_3d_carousel(active_mode: str):
    colors_map = {
        "📊 Gateway Overview": "0x4f46e5",
        "📝 Evaluate Action": "0x0284c7",
        "⏳ Approval Queue": "0xd97706",
        "📜 Audit Trail": "0x059669",
        "⚡ Controlled Execution": "0xe11d48"
    }
    active_color = colors_map.get(active_mode, "0x4f46e5")

    three_js_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; overflow: hidden; background: #ffffff; }}
            canvas {{ display: block; }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    </head>
    <body>
        <script>
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0xffffff);

            const camera = new THREE.PerspectiveCamera(75, window.innerWidth / 180, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, 180);
            document.body.appendChild(renderer.domElement);

            const geometry = new THREE.IcosahedronGeometry(2.0, 2);
            const material = new THREE.MeshBasicMaterial({{
                color: {active_color},
                wireframe: true,
                transparent: true,
                opacity: 0.8
            }});
            const sphere = new THREE.Mesh(geometry, material);
            scene.add(sphere);

            const coreGeom = new THREE.SphereGeometry(1.0, 16, 16);
            const coreMat = new THREE.MeshBasicMaterial({{
                color: {active_color},
                transparent: true,
                opacity: 0.15
            }});
            const core = new THREE.Mesh(coreGeom, coreMat);
            scene.add(core);

            camera.position.z = 4.0;

            function animate() {{
                requestAnimationFrame(animate);
                sphere.rotation.x += 0.003;
                sphere.rotation.y += 0.005;
                core.rotation.y -= 0.003;
                renderer.render(scene, camera);
            }}
            animate();
        </script>
    </body>
    </html>
    """
    components.html(three_js_code, height=180)

# -----------------------------------------------------------------------------
# Sidebar Configuration
# -----------------------------------------------------------------------------
st.sidebar.markdown("### 🛡️ SentinelGate Control")

backend_url = st.sidebar.text_input(
    "Backend Gateway URL",
    value="http://127.0.0.1:8000",
    help="Target API Address"
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
    st.sidebar.success("🟢 BACKEND ONLINE")
else:
    st.sidebar.warning("🟡 DEMO MOCK MODE")

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
# Top Hero Banner
# -----------------------------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 class="hero-title">SentinelGate</h1>
            <p class="hero-subtitle">Zero-Trust AI Agent Action Security Gateway & Policy Engine</p>
        </div>
        <div>
            <span style="background: #e0e7ff; border: 1px solid #c7d2fe; color: #3730a3; padding: 6px 16px; border-radius: 20px; font-size: 0.8rem; font-weight: 700;">
                ACTIVE GATEWAY V1.0
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Interactive Navigation Selection & 3D Carousel
# -----------------------------------------------------------------------------
nav_option = st.radio(
    "Navigation",
    ["📊 Gateway Overview", "📝 Evaluate Action", "⏳ Approval Queue", "📜 Audit Trail", "⚡ Controlled Execution"],
    horizontal=True
)

render_3d_carousel(nav_option)

# -----------------------------------------------------------------------------
# VIEW 1: GATEWAY OVERVIEW
# -----------------------------------------------------------------------------
if nav_option == "📊 Gateway Overview":
    st.markdown("### System Telemetry & Metrics")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Gateway State", "ONLINE" if is_backend_online else "SIMULATION")
    
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
    
    c2.metric("ALLOW Decisions", allows)
    c3.metric("BLOCK Decisions", blocks)
    c4.metric("HOLD (Pending)", holds)

# -----------------------------------------------------------------------------
# VIEW 2: EVALUATE ACTION
# -----------------------------------------------------------------------------
elif nav_option == "📝 Evaluate Action":
    st.markdown("### Propose Action Payload")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    preset = None
    if col_p1.button("🟢 Preset: Safe Action (ALLOW)"):
        preset = {
            "agent_id": "agent-01",
            "requester_id": "user-01",
            "action_type": "update_record",
            "target": "customer-101",
            "arguments": json.dumps({"field": "status", "value": "verified"}, indent=2)
        }
    if col_p2.button("🟡 Preset: Financial Action (HOLD)"):
        preset = {
            "agent_id": "agent-02",
            "requester_id": "user-02",
            "action_type": "transfer_funds",
            "target": "acct-5501",
            "arguments": json.dumps({"amount": 7500, "currency": "USD"}, indent=2)
        }
    if col_p3.button("🔴 Preset: Forbidden Action (BLOCK)"):
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
        
        submit_btn = st.form_submit_button("🔒 Evaluate Action Policy")

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
                        <p style="margin:4px 0 0 0;"><strong>Hash:</strong> <code>{result.get('action_hash')}</code></p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                if "drop" in action_type.lower() or "unauthorized" in agent_id.lower():
                    decision = "BLOCK"
                    reason = "Forbidden operation: Action blocked by security policy."
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
                    <p style="margin:4px 0 0 0;"><strong>Hash:</strong> <code>sha256-e3b0c44298fc1c149afbf4c...</code></p>
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
elif nav_option == "⏳ Approval Queue":
    st.markdown("### Human Authorization Queue")
    
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
# VIEW 4: AUDIT TRAIL
# -----------------------------------------------------------------------------
elif nav_option == "📜 Audit Trail":
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
# VIEW 5: CONTROLLED EXECUTION
# -----------------------------------------------------------------------------
elif nav_option == "⚡ Controlled Execution":
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