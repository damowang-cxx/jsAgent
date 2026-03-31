from __future__ import annotations

from har_agent.analysis.gaps import make_gap
from har_agent.graph.state import extend_gaps, extend_notes
from har_agent.models.agent_state import AgentState


def resolve_field_target_node(state: AgentState) -> dict:
    field_name = state.get("target_field_name")
    gaps = []
    notes = []
    if field_name:
        notes.append("Resolved field target for the field branch.")
        if len(state.get("target_field_candidate_scopes", [])) > 1:
            notes.append("Field scope remains ambiguous; all candidate scopes will be analyzed deterministically.")
    else:
        code = "goal_missing_field_name" if state.get("input_mode") == "goal_prompt" else "missing_field_target"
        gaps.append(make_gap(code, "No field target could be resolved for field-path analysis.", "high"))
        notes.append("Field target was not resolved; routing will fall back to automatic discovery.")
    return {
        "gaps": extend_gaps(state, gaps),
        "notes": extend_notes(state, *notes),
    }
