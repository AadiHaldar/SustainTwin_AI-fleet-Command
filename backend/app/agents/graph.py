"""LangGraph state-graph definition for the SustainTwin predictive-maintenance
multi-agent pipeline.

Pipeline topology::

    [ingest] --severity=='low'--> END
         |
         +--(medium|critical)--> [diagnose] --> [sustain] --> END
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from typing_extensions import TypedDict

from langgraph.graph import END, StateGraph

from app.agents.telemetry_ingest_node import telemetry_ingest_node
from app.agents.health_diagnostic_node import health_diagnostic_node
from app.agents.sustainability_node import sustainability_node

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared agent state
# ---------------------------------------------------------------------------

class AgentState(TypedDict, total=False):
    """Complete state flowing through the SustainTwin agent graph."""

    # --- Inputs (set by caller) ---
    machine_id: str
    sensor_data: Dict[str, Any]
    db_session: Any          # sqlalchemy Session -- not serialisable
    timestamp: Optional[str]

    # --- Populated by ingest node ---
    anomaly_flags: Dict[str, bool]
    z_scores: Dict[str, float]
    severity: str            # 'low' | 'medium' | 'critical'

    # --- Populated by diagnostic node ---
    shap_values: Dict[str, float]
    diagnosis: Optional[Dict[str, Any]]

    # --- Populated by sustainability node ---
    sustainability: Optional[Dict[str, Any]]


# ---------------------------------------------------------------------------
# Routing logic
# ---------------------------------------------------------------------------

def _route_after_ingest(state: AgentState) -> str:
    """Conditional edge: skip diagnosis if severity is low."""
    severity = state.get("severity", "low")
    if severity == "low":
        logger.info("Severity is 'low' -- short-circuiting to END")
        return "end"
    logger.info("Severity is '%s' -- routing to diagnose", severity)
    return "diagnose"


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    """Construct and return the *uncompiled* state graph."""
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("ingest", telemetry_ingest_node)
    graph.add_node("diagnose", health_diagnostic_node)
    graph.add_node("sustain", sustainability_node)

    # Entry
    graph.set_entry_point("ingest")

    # Conditional edge after ingest
    graph.add_conditional_edges(
        "ingest",
        _route_after_ingest,
        {
            "end": END,
            "diagnose": "diagnose",
        },
    )

    # Linear edges for the diagnosis path
    graph.add_edge("diagnose", "sustain")
    graph.add_edge("sustain", END)

    return graph


# Module-level compiled graph (importable as ``from app.agents.graph import agent_graph``)
agent_graph = build_graph().compile()
