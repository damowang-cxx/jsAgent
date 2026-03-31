from __future__ import annotations

from har_agent.graph.state import extend_notes
from har_agent.hooks.registry import HookRegistry
from har_agent.lineage.field_lineage import analyze_field_lineage
from har_agent.models.agent_state import AgentState


def run_field_analysis_node(state: AgentState, *, hook_registry: HookRegistry | None = None) -> dict:
    hook_registry = hook_registry or HookRegistry()
    entries = state.get("normalized_entries", [])
    matched_entry_ids = {item.entry_id for item in state.get("matched_requests", [])}
    focus_entries = [entry for entry in entries if entry.entry_id in matched_entry_ids] if matched_entry_ids else list(entries)
    selected_field_refs = state.get("selected_field_refs", [])
    field_analysis = (
        analyze_field_lineage(
            focus_entries,
            selected_field_refs,
            context_entries=entries,
            discovered_candidate_names={field.name for field in state.get("discovered_field_refs", [])},
        )
        if selected_field_refs
        else []
    )
    if state.get("reasoning_hook_enabled"):
        field_analysis = hook_registry.run_generation_logic_reasoner(field_analysis, state)
    return {
        "field_analysis": field_analysis,
        "notes": extend_notes(state, "Ran deterministic field lineage analysis."),
    }
