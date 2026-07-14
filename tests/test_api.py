from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_telemetry():
    response = client.get("/api/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert "timestamp" in data
    assert "stadium_zones" in data
    assert len(data["stadium_zones"]) > 0

def test_get_insights_no_key():
    # If API key is not set, it should return a warning message, but still be a 200 OK from the API perspective
    dummy_telemetry = {
        "timestamp": "2026-07-14T21:34:49Z",
        "stadium_zones": [
            {"zone_name": "Gate A", "density_percentage": 95, "status": "Critical Bottleneck"}
        ]
    }
    
    response = client.post("/api/insights", json={"telemetry": dummy_telemetry})
    assert response.status_code == 200
    data = response.json()
    assert "insights" in data
    # We don't strictly assert the exact text, just that it returns an insights block
    assert isinstance(data["insights"], str)
