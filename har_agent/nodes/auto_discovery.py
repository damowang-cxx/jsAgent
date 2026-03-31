from __future__ import annotations

from har_agent.analysis.claims import claims_from_cookie_results
from har_agent.analysis.helpers import first_signal_time, merge_field_refs, select_requests
from har_agent.graph.state import extend_notes
from har_agent.inference.generation_candidates import discover_candidate_fields
from har_agent.lineage.cookie_lineage import analyze_cookie_lineage
from har_agent.lineage.field_lineage import analyze_field_lineage
from har_agent.models.agent_state import AgentState


def auto_discovery_node(state: AgentState) -> dict:
    entries = state.get("normalized_entries", [])
    explicit_field_refs = [] if state.get("input_mode") == "goal_prompt" else state.get("selected_field_refs", [])
    discovered_field_refs = discover_candidate_fields(entries, explicit_field_refs)
    selected_field_refs = merge_field_refs(explicit_field_refs, discovered_field_refs)
    cookie_lineage = analyze_cookie_lineage(entries, None)
    field_analysis = (
        analyze_field_lineage(
            entries,
            selected_field_refs,
            context_entries=entries,
            discovered_candidate_names={field.name for field in discovered_field_refs},
        )
        if selected_field_refs
        else []
    )
    matched_requests = select_requests(
        entries,
        [],
        cookie_targets={item.cookie_name for item in cookie_lineage},
        field_refs=selected_field_refs,
        first_signal_time=first_signal_time(entries, cookie_lineage, field_analysis),
        auto_all_when_no_rules=True,
    )
    notes = ["Ran fallback auto-discovery over the full HAR because the target was absent, ambiguous, or broad."]
    if state.get("input_mode") == "goal_prompt":
        notes.append("Fallback output is reported as discovered candidates rather than a precise target hit.")
    return {
        "discovered_field_refs": discovered_field_refs,
        "selected_field_refs": selected_field_refs,
        "matched_requests": matched_requests,
        "cookie_lineage": cookie_lineage,
        "field_analysis": field_analysis,
        "claims": claims_from_cookie_results(cookie_lineage, field_analysis),
        "notes": extend_notes(state, *notes),
    }
