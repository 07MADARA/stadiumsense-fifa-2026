"""
FastAPI entry point for the StadiumSense backend.
Provides endpoints for telemetry retrieval and AI insight generation.
"""

import time
import logging
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, List
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from src.data.simulator import generate_telemetry_data
from src.api.agent import get_actionable_insights

# Configure module logger
logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to limit the number of requests per IP address.
    """
    def __init__(self, app: FastAPI, max_requests: int = 20, window_seconds: int = 60) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.ip_records: Dict[str, List[float]] = {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Intercepts incoming requests and applies rate limiting.
        """
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        
        if client_ip not in self.ip_records:
            self.ip_records[client_ip] = []
            
        # Clean up old requests outside the window
        self.ip_records[client_ip] = [t for t in self.ip_records[client_ip] if now - t < self.window_seconds]
        
        if len(self.ip_records[client_ip]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
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
    """
    Request model for the insights endpoint.
    """
    telemetry: Dict[str, Any]

@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "healthy"}

@app.get("/api/telemetry")
async def get_telemetry() -> Dict[str, Any]:
    """Returns real-time simulated stadium telemetry."""
    try:
        data = generate_telemetry_data()
        return data
    except Exception as e:
        logger.error(f"Error generating telemetry: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while generating telemetry.")

@app.post("/api/insights")
async def get_insights(request: InsightRequest) -> Dict[str, str]:
    """
    Accepts telemetry data and returns GenAI operational insights.
    Uses POST to send potentially large JSON data in the body.
    """
    try:
        insights = get_actionable_insights(request.telemetry)
        return {"insights": insights}
    except Exception as e:
        logger.error(f"Error generating insights: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while generating insights.")
