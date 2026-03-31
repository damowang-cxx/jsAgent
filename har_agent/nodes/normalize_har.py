from __future__ import annotations

from har_agent.graph.state import extend_notes
from har_agent.models.agent_state import AgentState
from har_agent.parsers.normalizer import normalize_document


def normalize_har_node(state: AgentState) -> dict:
    normalized, parse_gaps = normalize_document(state["har_document"])
    return {
        "normalized_entries": normalized.entries,
        "parse_gaps": parse_gaps,
        "notes": extend_notes(state, "Normalized HAR entries into the internal stable model."),
    }
