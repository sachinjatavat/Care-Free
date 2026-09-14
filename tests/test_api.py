import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["seed"] == 20260911

def test_api_dashboard():
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert data["total_beds"] == 45
    assert data["general_total"] == 30
    assert data["monitored_total"] == 10
    assert data["critical_total"] == 5

def test_api_beds():
    res = client.get("/api/beds")
    assert res.status_code == 200
    beds = res.json()
    assert len(beds) == 45

def test_api_waiting_patients():
    res = client.get("/api/patients/waiting")
    assert res.status_code == 200
    waiting = res.json()
    assert isinstance(waiting, list)

def test_api_simulate_arrival():
    res = client.post("/api/patients/simulate-arrival", json={"acuity": 3})
    assert res.status_code == 200
    data = res.json()
    assert "patient_id" in data
    assert data["acuity"] == 3

def test_api_decisions():
    res = client.get("/api/decisions")
    assert res.status_code == 200
    decisions = res.json()
    assert isinstance(decisions, list)

def test_api_export_decisions():
    res = client.get("/api/export/decisions")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]

def test_api_simulation_run():
    res = client.post("/api/simulation/run", json={"seed": 20260911, "patients": 500})
    assert res.status_code == 200
    data = res.json()
    assert data["seed"] == 20260911
    assert data["total_arrivals"] == 500
    assert "overall_score" in data

def test_api_analytics():
    res = client.get("/api/analytics")
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert "occupancy_over_time" in data

def test_api_chat():
    res = client.post("/api/chat", json={"messages": [{"role": "user", "content": "How many beds are available?"}], "user_role": "patient"})
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert "source" in data

