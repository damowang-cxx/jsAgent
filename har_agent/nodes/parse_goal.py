from __future__ import annotations

from har_agent.config import AppConfig
from har_agent.graph.state import extend_gaps, extend_notes
from har_agent.hooks.registry import HookRegistry
from har_agent.intents.goal_resolver import GoalResolver, build_auto_discovery_intent, build_structured_intent, intent_to_config
from har_agent.models.agent_state import AgentState
from har_agent.selectors.request_selector import field_refs_from_config


def parse_goal_node(state: AgentState, *, hook_registry: HookRegistry | None = None) -> dict:
    hook_registry = hook_registry or HookRegistry()
    entries = state.get("normalized_entries", [])
    config = state.get("provided_config") or AppConfig()
    goal = state.get("user_goal")

    if goal:
        prompt = hook_registry.run_semantic_goal_refiner(goal, state) if state.get("semantic_hook_enabled") else goal
        analysis_intent = GoalResolver().resolve(prompt, entries)
        effective_config = intent_to_config(analysis_intent)
        notes = extend_notes(state, "Parsed deterministic goal prompt intent for LangGraph routing.")
    elif config.target_requests or config.target_cookies or config.target_fields:
        analysis_intent = build_structured_intent(config)
        effective_config = config
        notes = extend_notes(state, "Built structured intent from explicit YAML config.")
    else:
        analysis_intent = build_auto_discovery_intent()
        effective_config = config
        notes = extend_notes(state, "Built auto-discovery intent because no goal prompt or config targets were provided.")

    field_refs = field_refs_from_config(effective_config.target_fields)
    resolved_field = analysis_intent.resolved_field
    target_field_name = resolved_field.name if resolved_field and resolved_field.name else (field_refs[0].name if field_refs else None)
    target_field_candidate_scopes = (
        list(resolved_field.candidate_scopes)
        if resolved_field and resolved_field.candidate_scopes
        else sorted({field.scope for field in field_refs if field.name == target_field_name})
    )
    target_field_scope = (
        resolved_field.resolved_scopes[0]
        if resolved_field and resolved_field.resolved_scopes
        else field_refs[0].scope if len(field_refs) == 1 else None
    )
    resolved_request = analysis_intent.resolved_request
    return {
        "analysis_intent": analysis_intent,
        "effective_config": effective_config,
        "input_mode": analysis_intent.input_mode,
        "config_mode": analysis_intent.input_mode,
        "analysis_kind": analysis_intent.analysis_kind,
        "resolved_request": resolved_request,
        "resolved_field": resolved_field,
        "target_url": resolved_request.url if resolved_request else None,
        "target_host": resolved_request.host_contains if resolved_request else None,
        "target_path": resolved_request.path_contains if resolved_request else None,
        "target_cookie_name": analysis_intent.resolved_cookie_name or (effective_config.target_cookies[0] if effective_config.target_cookies else None),
        "target_field_name": target_field_name,
        "target_field_scope": target_field_scope,
        "target_field_candidate_scopes": target_field_candidate_scopes,
        "selected_field_refs": field_refs,
        "request_rules": list(effective_config.target_requests),
        "resolution_confidence": analysis_intent.resolution_confidence,
        "gaps": extend_gaps(state, analysis_intent.resolution_gaps),
        "notes": notes,
    }
