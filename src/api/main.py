import time
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.data.simulator import generate_telemetry_data
from src.api.agent import get_actionable_insights

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 20, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.ip_records = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        
        if client_ip not in self.ip_records:
            self.ip_records[client_ip] = []
            
        # Clean up old requests outside the window
        self.ip_records[client_ip] = [t for t in self.ip_records[client_ip] if now - t < self.window_seconds]
        
        if len(self.ip_records[client_ip]) >= self.max_requests:
            return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})
            
        self.ip_records[client_ip].append(now)
        response = await call_next(request)
        return response

app = FastAPI(
    title="StadiumSense API",
    description="API for fetching stadium telemetry and GenAI insights.",
    version="1.0.0"
)

# Apply the rate limiter middleware
app.add_middleware(RateLimitMiddleware, max_requests=20, window_seconds=60)

class InsightRequest(BaseModel):
    telemetry: Dict[str, Any]

@app.get("/api/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}

@app.get("/api/telemetry")
async def get_telemetry():
    """Returns real-time simulated stadium telemetry."""
    try:
        data = generate_telemetry_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/insights")
async def get_insights(request: InsightRequest):
    """
    Accepts telemetry data and returns GenAI operational insights.
    Uses POST to send potentially large JSON data in the body.
    """
    try:
        insights = get_actionable_insights(request.telemetry)
        return {"insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
