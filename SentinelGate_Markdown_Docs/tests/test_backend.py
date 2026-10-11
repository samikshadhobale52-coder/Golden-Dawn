import os
import pytest
from fastapi.testclient import TestClient
from backend.main import app, init_db, DB_FILE

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    # Remove database file before each test for isolated audit chains
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    init_db()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "2.0.0"}

def test_evaluate_permitted_action():
    payload = {
        "agent_id": "agent-01",
        "requester_id": "user-01",
        "action_type": "update_record",
        "target": "customer-101",
        "arguments": {"field": "status", "value": "verified"}
    }
    response = client.post("/actions/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "ALLOW"
    assert "action_hash" in data

def test_evaluate_unknown_agent():
    payload = {
        "agent_id": "agent-99",
        "requester_id": "user-01",
        "action_type": "update_record",
        "target": "customer-101",
        "arguments": {"field": "status", "value": "verified"}
    }
    response = client.post("/actions/evaluate", json=payload)
    assert response.status_code == 200
    assert response.json()["decision"] == "BLOCK"

def test_evaluate_destructive_action_holds():
    payload = {
        "agent_id": "agent-01",
        "requester_id": "user-01",
        "action_type": "delete_record",
        "target": "customer-101",
        "arguments": {"record_id": "101"}
    }
    response = client.post("/actions/evaluate", json=payload)
    assert response.status_code == 200
    assert response.json()["decision"] == "HOLD"

def test_audit_verification():
    # Trigger an evaluation to generate audit logs
    client.post("/actions/evaluate", json={
        "agent_id": "agent-01",
        "requester_id": "user-01",
        "action_type": "update_record",
        "target": "customer-101",
        "arguments": {"field": "status", "value": "verified"}
    })
    
    # Verify the hash chain
    response = client.get("/audit/verify")
    assert response.status_code == 200
    assert response.json()["verified"] is True