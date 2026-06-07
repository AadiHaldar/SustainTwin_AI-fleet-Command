from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from app.agents.health_agent import run_health_agent

router = APIRouter()

class TelemetryPayload(BaseModel):
    machine_id: str
    timestamp: str
    engine_rpm: float
    engine_temperature: float
    vibration_level: float
    fuel_consumption: float
    is_anomaly: bool = False

@router.post("/sync")
def sync_telemetry(payload: TelemetryPayload):
    # In a real app, we would save this to the DB here.
    
    analysis_result = None
    if payload.is_anomaly:
        print(f"[CLOUD ALERT] Edge Node flagged anomaly for {payload.machine_id}! Triggering LangGraph...")
        
        # Trigger the LangGraph Agentic workflow
        result = run_health_agent(
            machine_id=payload.machine_id,
            vibration=payload.vibration_level,
            temp=payload.engine_temperature,
            rpm=payload.engine_rpm
        )
        
        print(f"[XAI EXPLANATION]: {result['analysis']}")
        analysis_result = result
        
    return {
        "status": "success", 
        "recorded_at": datetime.utcnow().isoformat(),
        "agent_analysis": analysis_result
    }
