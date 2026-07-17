import time
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

def test_rate_limiter():
    # We allow 20 requests per minute
    # Make 20 requests
    for _ in range(20):
        res = client.get("/api/health")
        if res.status_code == 429:
            # Maybe tests run quickly and hit limit from other tests?
            # Let's break if we hit it early, though we shouldn't unless tests share state.
            break
            
    # The 21st request should be rate-limited
    res = client.get("/api/health")
    assert res.status_code == 429
    assert res.json() == {"detail": "Too Many Requests"}
    
    # Optional: wait or reset state to avoid affecting other tests if they run sequentially and share state.
    # FastAPI test client recreates the app, but the app object is imported so state persists across tests!
    # Let's clear the IP records for safety.
    for route in app.user_middleware:
        if hasattr(route.cls, 'ip_records'):
            # It's a class, but we need the instance. 
            # Easiest way to reset is to wait or manually clear if possible. 
            pass
    # We can just reset it directly on the app instance if we could find it, but 
    # letting it fail for the next test is bad. We can just sleep or clear it.
    
    # Clean up the middleware state manually so other tests don't fail if they run after this.
    app.middleware_stack = app.build_middleware_stack() 
    # Actually, the middleware instance holds the state.
    # We can clear all ip records from all middlewares that have it.
    for m in app.user_middleware:
        # Note: This is an ugly hack for tests, ideally we inject state
        pass
        
    # To be safe, we will just use a different IP for this specific test by faking the client host
    # TestClient doesn't easily let us spoof IP in every request method unless we pass headers/scope.
    # Let's just run it as the last test or clear it.
