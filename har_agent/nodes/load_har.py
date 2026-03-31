from __future__ import annotations

from har_agent.graph.state import extend_notes
from har_agent.models.agent_state import AgentState
from har_agent.parsers.har_loader import load_har_document


def load_har_node(state: AgentState) -> dict:
    document = load_har_document(state["input_har_path"])
    return {
        "har_document": document,
        "notes": extend_notes(state, "Loaded HAR document from local disk."),
    }
