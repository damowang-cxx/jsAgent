from __future__ import annotations

from har_agent.analysis.helpers import select_requests
from har_agent.graph.state import extend_notes
from har_agent.models.agent_state import AgentState


def match_requests_node(state: AgentState) -> dict:
    entries = state.get("normalized_entries", [])
    rules = state.get("request_rules", [])
    field_refs = state.get("selected_field_refs", [])
    effective_config = state.get("effective_config")
    cookie_targets = {item for item in effective_config.target_cookies if item} if effective_config is not None else set()
    matched_requests = select_requests(
        entries,
        rules,
        cookie_targets=cookie_targets,
        field_refs=field_refs,
        first_signal_time=None,
        auto_all_when_no_rules=state.get("input_mode") in {"structured_config", "auto_discovery"},
    )
    notes = []
    if rules and not matched_requests and state.get("input_mode") != "goal_prompt":
        matched_requests = select_requests(
            entries,
            [],
            cookie_targets=cookie_targets,
            field_refs=field_refs,
            first_signal_time=None,
            auto_all_when_no_rules=True,
        )
        if matched_requests:
            notes.append("Explicit request rules matched no entries; using ranked whole-HAR context to preserve deterministic analysis coverage.")
    if not matched_requests:
        notes.append("Request matching produced no candidates.")
    elif len(matched_requests) > 1:
        notes.append(f"Request matching kept {len(matched_requests)} ranked candidates instead of collapsing to a single request.")
    return {
        "matched_requests": matched_requests,
        "notes": extend_notes(state, *notes),
    }
