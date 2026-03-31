from __future__ import annotations

from har_agent.analysis.gaps import make_gap
from har_agent.graph.state import extend_gaps, extend_notes
from har_agent.models.agent_state import AgentState


def resolve_cookie_target_node(state: AgentState) -> dict:
    cookie_name = state.get("target_cookie_name")
    gaps = []
    notes = ["Resolved cookie target for the cookie branch."] if cookie_name else []
    if not cookie_name:
        code = "goal_missing_cookie_name" if state.get("input_mode") == "goal_prompt" else "missing_cookie_target"
        gaps.append(make_gap(code, "No cookie target could be resolved for cookie-path analysis.", "high"))
        notes.append("Cookie target was not resolved; routing will fall back to automatic discovery.")
    return {
        "gaps": extend_gaps(state, gaps),
        "notes": extend_notes(state, *notes),
    }
