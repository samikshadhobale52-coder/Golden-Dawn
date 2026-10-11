# SentinelGate — AI Agent Action Security Gateway

## Problem
AI agents can take consequential actions such as changing records, deleting data, sending messages, or triggering payments. A model may misunderstand a request or be manipulated by hostile text. SentinelGate places a policy-enforcement gateway between an agent's proposed action and its execution.

## Prototype goal
Demonstrate a fail-closed gateway that evaluates a proposed action and returns exactly one of `ALLOW`, `BLOCK`, or `HOLD`.

- **ALLOW** — the deterministic policy permits the exact action.
- **BLOCK** — the request is invalid, unauthorized, unknown, or forbidden.
- **HOLD** — the action needs a separate human approval before execution.

The prototype uses simulated actions only. It must not send real messages, modify real accounts, or initiate real payments.

## Main requirements
1. Unknown agents and action types are blocked by default.
2. Agent permissions and action impact are checked by deterministic rules.
3. High-impact, bulk, or irreversible actions require approval or are blocked.
4. A requester cannot approve their own action.
5. Approval is bound to the exact canonical action hash.
6. Execution rechecks the action hash and policy; changed arguments require reauthorization.
7. Decisions, refusals, approvals, and execution attempts are written to a SHA-256 hash-chained audit log.
8. Audit verification detects changes to stored events.
9. If an optional AI assessor is unavailable or returns invalid output, deterministic policy remains authoritative and the fallback path is recorded.

## Stack
- Python
- FastAPI
- SQLite
- Streamlit frontend (owned separately by the frontend teammate)
- pytest for tests

## Repository layout
```text
sentinelgate/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/                 # frontend teammate owns this
├── tests/
├── docs/
├── README.md
└── .gitignore
```

## Run backend (Windows)
Open a terminal in the repository folder:
```powershell
py --version
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
uvicorn backend.main:app --reload
```
If `py` is unavailable, try `python` instead. API docs: http://127.0.0.1:8000/docs

## Safety scope
This is a hackathon demonstration, not a production security boundary. Do not connect it to real accounts or systems. Production deployment would need authentication, authorization, protected secrets, durable independent audit anchoring, concurrency controls, monitoring, and security review.
