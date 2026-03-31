from __future__ import annotations

from har_agent.graph.state import extend_notes
from har_agent.models.agent_state import AgentState


def resolve_request_target_node(state: AgentState) -> dict:
    request_rules = list(state.get("request_rules", []))
    note = (
        "Resolved request target rules from the parsed intent/config."
        if request_rules
        else "No explicit request target rules were resolved; downstream matching may widen to the whole HAR context."
    )
    return {
        "request_rules": request_rules,
        "notes": extend_notes(state, note),
    }
