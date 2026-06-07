"""Health diagnostic node -- LLM-powered root-cause analysis.

Combines SHAP explanations with Gemini to produce a structured diagnosis
when a non-trivial anomaly is detected.
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _build_prompt(
    machine_id: str,
    sensor_data: dict,
    anomaly_flags: dict,
    z_scores: dict,
    shap_values: dict,
) -> str:
    """Build a structured prompt for Gemini root-cause analysis."""
    anomalous = [s for s, flag in anomaly_flags.items() if flag]
    normal = [s for s, flag in anomaly_flags.items() if not flag]

    sensor_lines = []
    for name, value in sensor_data.items():
        z = z_scores.get(name, 0.0)
        shap_imp = shap_values.get(name, 0.0)
        flag = "ANOMALOUS" if anomaly_flags.get(name) else "normal"
        sensor_lines.append(
            f"  - {name}: value={value}, z_score={z:.2f}, shap_importance={shap_imp:.4f}, status={flag}"
        )
    sensor_block = "\n".join(sensor_lines)

    return f"""\
You are an expert industrial predictive-maintenance AI for SustainTwin.

Machine ID: {machine_id}
Anomalous sensors: {', '.join(anomalous) if anomalous else 'none'}
Normal sensors: {', '.join(normal) if normal else 'none'}

Current sensor readings with diagnostics:
{sensor_block}

Using the z-scores (deviation from historical mean) and SHAP importances
(model-derived feature contributions), provide a root-cause analysis.

Respond ONLY with a valid JSON object (no markdown, no code fences):
{{
  "root_cause": "<concise technical explanation of the most likely failure mode>",
  "confidence": <float between 0 and 1>,
  "recommended_action": "<specific maintenance action for a field technician>",
  "urgency": "<one of: immediate, scheduled, monitor>"
}}
"""


def _extract_json(text: str) -> Optional[dict]:
    """Robustly extract a JSON object from LLM text output."""
    # Strip markdown code fences if present
    cleaned = re.sub(r"```(?:json)?\s*", "", text)
    cleaned = cleaned.strip().rstrip("`")

    # Try direct parse first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try to find the first {...} block
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def _default_diagnosis(anomaly_flags: dict, z_scores: dict) -> dict:
    """Fallback diagnosis when LLM is unavailable or fails."""
    worst_sensor = max(z_scores, key=lambda k: abs(z_scores[k])) if z_scores else "unknown"
    return {
        "root_cause": f"Statistical anomaly detected in {worst_sensor} (z={z_scores.get(worst_sensor, 0):.2f})",
        "confidence": 0.5,
        "recommended_action": f"Inspect {worst_sensor} sensor and related subsystem",
        "urgency": "scheduled",
    }


def health_diagnostic_node(state: dict) -> dict:
    """LangGraph node: produce a root-cause diagnosis via SHAP + Gemini.

    **Expects in state:** ``machine_id``, ``sensor_data``, ``anomaly_flags``,
    ``z_scores``, ``severity``

    **Adds to state:** ``diagnosis``, ``shap_values``
    """
    machine_id: str = state["machine_id"]
    sensor_data: dict = state["sensor_data"]
    anomaly_flags: dict = state.get("anomaly_flags", {})
    z_scores: dict = state.get("z_scores", {})

    # ------------------------------------------------------------------
    # 1. SHAP explanation
    # ------------------------------------------------------------------
    shap_values: Dict[str, float] = {}
    try:
        from app.agents.shap_explainer import explain
        shap_values = explain(sensor_data)
    except Exception:
        logger.warning("SHAP explain failed -- proceeding without importances", exc_info=True)

    # ------------------------------------------------------------------
    # 2. Gemini LLM diagnosis
    # ------------------------------------------------------------------
    diagnosis: dict | None = None

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage

        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            api_key=api_key,
        )

        prompt = _build_prompt(machine_id, sensor_data, anomaly_flags, z_scores, shap_values)
        response = llm.invoke([HumanMessage(content=prompt)])
        raw_text: str = response.content

        diagnosis = _extract_json(raw_text)
        if diagnosis is None:
            logger.warning("Could not parse Gemini response as JSON: %s", raw_text[:300])

    except Exception:
        logger.error("Gemini diagnosis call failed", exc_info=True)

    # ------------------------------------------------------------------
    # 3. Fallback
    # ------------------------------------------------------------------
    if diagnosis is None:
        diagnosis = _default_diagnosis(anomaly_flags, z_scores)
        logger.info("Using fallback diagnosis for machine %s", machine_id)

    # Clamp confidence to [0, 1]
    try:
        diagnosis["confidence"] = max(0.0, min(1.0, float(diagnosis.get("confidence", 0.5))))
    except (TypeError, ValueError):
        diagnosis["confidence"] = 0.5

    logger.info(
        "Diagnosis for %s: root_cause=%s, confidence=%.2f, urgency=%s",
        machine_id,
        diagnosis.get("root_cause", "?")[:80],
        diagnosis["confidence"],
        diagnosis.get("urgency", "?"),
    )

    return {
        "diagnosis": diagnosis,
        "shap_values": shap_values,
    }
