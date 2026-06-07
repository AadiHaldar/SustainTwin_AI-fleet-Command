from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
import xgboost as xgb
import numpy as np

# Define State
class AgentState(TypedDict):
    machine_id: str
    telemetry_data: Dict[str, Any]
    health_score: float
    predicted_failure_prob: float
    recommendation: str

# Node Functions
def analyze_telemetry(state: AgentState):
    """
    Mock function for XGBoost inference on telemetry data.
    """
    telemetry = state["telemetry_data"]
    # Mocking prediction based on vibration and temp
    vibration = telemetry.get("vibration", 0)
    temp = telemetry.get("engine_temperature", 0)
    
    # Mock failure probability
    prob = min(1.0, (vibration * 0.05 + temp * 0.01) / 10)
    score = 100 - (prob * 100)
    
    return {"health_score": score, "predicted_failure_prob": prob}

def generate_recommendation(state: AgentState):
    prob = state["predicted_failure_prob"]
    if prob > 0.8:
        rec = "Immediate maintenance required. High risk of failure."
    elif prob > 0.5:
        rec = "Schedule maintenance within 7 days."
    else:
        rec = "Machine operating normally."
    return {"recommendation": rec}

# Build Graph
graph = StateGraph(AgentState)

graph.add_node("analyze", analyze_telemetry)
graph.add_node("recommend", generate_recommendation)

graph.set_entry_point("analyze")
graph.add_edge("analyze", "recommend")
graph.add_edge("recommend", END)

health_agent = graph.compile()
