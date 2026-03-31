from __future__ import annotations

from har_agent.analysis.gaps import assess_har_health
from har_agent.graph.state import extend_gaps, extend_notes
from har_agent.models.agent_state import AgentState


def health_check_node(state: AgentState) -> dict:
    health = assess_har_health(state["har_document"], state.get("normalized_entries", []), state.get("parse_gaps", []))
    return {
        "health": health,
        "gaps": extend_gaps(state, health.gaps),
        "notes": extend_notes(state, "Assessed HAR health and collected capture-quality gaps."),
    }
