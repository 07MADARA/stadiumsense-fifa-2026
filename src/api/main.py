from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from src.data.simulator import generate_telemetry_data
from src.api.agent import get_actionable_insights

app = FastAPI(
    title="StadiumSense API",
    description="API for fetching stadium telemetry and GenAI insights.",
    version="1.0.0"
)

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
