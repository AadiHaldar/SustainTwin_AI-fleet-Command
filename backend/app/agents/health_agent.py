import os
from typing import TypedDict, Annotated, Sequence
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()

# Set up the Gemini LLM
# The API key is automatically picked up from the GEMINI_API_KEY env variable
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY not found in environment.")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, api_key=api_key)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], lambda a, b: a + b]
    machine_id: str
    vibration_level: float
    engine_temp: float
    engine_rpm: float
    risk_score: float
    analysis: str

def analyze_telemetry(state: AgentState):
    """Agent node that analyzes telemetry to calculate a risk score."""
    vibration = state["vibration_level"]
    temp = state["engine_temp"]
    rpm = state["engine_rpm"]
    
    # Simple risk heuristic for MVP. 
    # In production, this would be a XGBoost/SHAP model prediction.
    risk_score = 0.0
    if vibration > 40:
        risk_score += 0.5
    if temp > 100:
        risk_score += 0.3
    if rpm > 2200:
        risk_score += 0.1
        
    return {"risk_score": min(risk_score, 1.0)}

def generate_explanation(state: AgentState):
    """Agent node that uses Gemini to explain the risk score in plain English."""
    if state["risk_score"] < 0.4:
        return {"analysis": "Machine is operating normally. No immediate action required."}
        
    prompt = f"""
    You are an expert industrial mechanic AI (SustainTwin).
    Analyze the following machine telemetry for Machine {state['machine_id']}:
    - Vibration Level: {state['vibration_level']}
    - Engine Temperature: {state['engine_temp']}
    - Engine RPM: {state['engine_rpm']}
    
    The calculated risk of imminent failure is {state['risk_score'] * 100}%.
    
    Provide a 3-sentence root cause analysis and a recommended action for the field technician.
    Do not use markdown formatting like bolding or lists, just write a short paragraph.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"analysis": response.content}

# Build the LangGraph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("analyze_telemetry", analyze_telemetry)
workflow.add_node("generate_explanation", generate_explanation)

# Add edges
workflow.set_entry_point("analyze_telemetry")
workflow.add_edge("analyze_telemetry", "generate_explanation")
workflow.add_edge("generate_explanation", END)

# Compile the graph
health_agent_app = workflow.compile()

def run_health_agent(machine_id: str, vibration: float, temp: float, rpm: float):
    """Entry point to invoke the compiled LangGraph agent."""
    initial_state = {
        "messages": [],
        "machine_id": machine_id,
        "vibration_level": vibration,
        "engine_temp": temp,
        "engine_rpm": rpm,
        "risk_score": 0.0,
        "analysis": ""
    }
    
    result = health_agent_app.invoke(initial_state)
    return {
        "risk_score": result["risk_score"],
        "analysis": result["analysis"]
    }
