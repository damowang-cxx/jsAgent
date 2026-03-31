from __future__ import annotations

from pathlib import Path

from har_agent.analysis.gaps import dedupe_gaps
from har_agent.config import AppConfig
from har_agent.models.agent_state import AgentState
from har_agent.models.findings import Gap


def build_initial_state(
    input_har_path: str | Path,
    config: AppConfig,
    *,
    goal: str | None = None,
) -> AgentState:
    return AgentState(
        input_har_path=str(input_har_path),
        user_goal=goal,
        config_mode=None,
        provided_config=config,
        effective_config=config,
        har_document=None,
        normalized_entries=[],
        parse_gaps=[],
        health=None,
        input_mode="unknown",
        analysis_kind="unknown",
        target_url=None,
        target_host=None,
        target_path=None,
        target_cookie_name=None,
        target_field_name=None,
        target_field_scope=None,
        target_field_candidate_scopes=[],
        resolved_request=None,
        resolved_field=None,
        request_rules=[],
        selected_field_refs=[],
        discovered_field_refs=[],
        matched_requests=[],
        analysis_intent=None,
        cookie_lineage=[],
        field_analysis=[],
        claims=[],
        recommendations=[],
        gaps=[],
        notes=[],
        resolution_confidence="unresolved",
        final_result=None,
        semantic_hook_enabled=False,
        explanation_hook_enabled=False,
        reasoning_hook_enabled=False,
    )


def extend_notes(state: AgentState, *notes: str) -> list[str]:
    merged = [*state.get("notes", [])]
    for note in notes:
        if note and note not in merged:
            merged.append(note)
    return merged


def extend_gaps(state: AgentState, gaps: list[Gap]) -> list[Gap]:
    return dedupe_gaps([*state.get("gaps", []), *gaps])
