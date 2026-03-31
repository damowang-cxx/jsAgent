from __future__ import annotations

from har_agent.models.agent_state import AgentState


def route_by_intent(state: AgentState) -> str:
    analysis_kind = state.get("analysis_kind")
    if analysis_kind in {"cookie_set_source", "cookie_generation_logic"}:
        return "cookie_path"
    if analysis_kind in {"field_origin", "field_generation_logic"}:
        return "field_path"
    return "fallback_path"


def route_after_cookie_target(state: AgentState) -> str:
    return "resolve_request_target" if state.get("target_cookie_name") else "fallback_path"


def route_after_field_target(state: AgentState) -> str:
    return "resolve_request_target" if state.get("target_field_name") else "fallback_path"


def route_after_request_match(state: AgentState) -> str:
    if state.get("matched_requests"):
        return "run_cookie_analysis" if state.get("analysis_kind", "").startswith("cookie_") else "run_field_analysis"
    if state.get("input_mode") == "goal_prompt":
        return "fallback_path"
    if state.get("input_mode") == "auto_discovery":
        return "auto_discovery"
    return "auto_discovery" if state.get("analysis_kind", "").startswith("field_") else "finalize"


def route_after_analysis(state: AgentState) -> str:
    return "review_cookie_evidence" if state.get("analysis_kind", "").startswith("cookie_") else "review_field_evidence"
