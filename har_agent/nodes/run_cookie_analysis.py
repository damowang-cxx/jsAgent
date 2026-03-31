from __future__ import annotations

from har_agent.analysis.helpers import cookie_target_input
from har_agent.graph.state import extend_notes
from har_agent.hooks.registry import HookRegistry
from har_agent.lineage.cookie_lineage import analyze_cookie_lineage
from har_agent.models.agent_state import AgentState


def run_cookie_analysis_node(state: AgentState, *, hook_registry: HookRegistry | None = None) -> dict:
    hook_registry = hook_registry or HookRegistry()
    cookie_targets = cookie_target_input(state["effective_config"], state["analysis_intent"])
    cookie_lineage = analyze_cookie_lineage(state.get("normalized_entries", []), cookie_targets)
    if state.get("reasoning_hook_enabled"):
        cookie_lineage = hook_registry.run_generation_logic_reasoner(cookie_lineage, state)
    return {
        "cookie_lineage": cookie_lineage,
        "notes": extend_notes(state, "Ran deterministic cookie lineage analysis."),
    }
