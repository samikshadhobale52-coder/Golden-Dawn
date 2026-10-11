# Backend Build Steps (Fast Hackathon Path)

## 1. Verify Python
In VS Code, open Terminal → New Terminal:
```powershell
py --version
```
If that fails:
```powershell
python --version
```
Use whichever command works in the next steps.

## 2. Create folders
Create `backend` and `tests` in the repository. Add an empty `backend/__init__.py` so the module import is reliable.

## 3. Create a virtual environment
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```
If PowerShell blocks activation, use:
```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

## 4. Install dependencies
Put FastAPI, Uvicorn, and pytest in `backend/requirements.txt`, then run:
```powershell
python -m pip install -r backend\requirements.txt
```

## 5. Build in this order
1. `GET /health`
2. Define and validate the action request model.
3. Implement canonical JSON serialization and SHA-256 action hashing.
4. Implement deterministic agent/action permission checks.
5. Implement `POST /actions/evaluate` and audit every decision.
6. Add SQLite persistence for actions and audit events.
7. Implement approval/rejection with requester/approver separation.
8. Implement execution with hash and policy revalidation; executor is simulated only.
9. Implement `GET /audit` and `GET /audit/verify`.
10. Add tests from `TEST_PLAN.md`.

## 6. Start server
```powershell
python -m uvicorn backend.main:app --reload
```
Open http://127.0.0.1:8000/docs and test `/health` first.

## 7. Integrate with frontend teammate
Give them the API contract in `API_CONTRACT.md`. Ask them to use the exact endpoint names, request fields, and response fields. They can build with mock responses before the API is ready.

## 8. Important demo rule
Use only simulated records. Do not connect this prototype to email, payments, real customer accounts, or external systems.
