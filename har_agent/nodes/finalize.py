from __future__ import annotations

from datetime import datetime, timezone

from har_agent.analysis.claims import claims_from_cookie_results
from har_agent.analysis.gaps import dedupe_gaps
from har_agent.analysis.helpers import first_signal_time, recommendations_from_gaps, select_requests
from har_agent.config import AppConfig, config_to_targets
from har_agent.graph.state import extend_notes
from har_agent.hooks.registry import HookRegistry
from har_agent.lineage.cookie_lineage import analyze_cookie_lineage
from har_agent.lineage.field_lineage import analyze_field_lineage
from har_agent.models.agent_state import AgentState
from har_agent.models.report import AnalysisResult, AnalysisSummary


def finalize_node(state: AgentState, *, hook_registry: HookRegistry | None = None) -> dict:
    hook_registry = hook_registry or HookRegistry()
    effective_config = state.get("effective_config") or state.get("provided_config") or AppConfig()
    analysis_intent = state["analysis_intent"]
    entries = state.get("normalized_entries", [])
    cookie_lineage = state.get("cookie_lineage", [])
    field_analysis = state.get("field_analysis", [])
    field_refs = state.get("selected_field_refs", [])

    # Preserve structured-config compatibility: if one branch was chosen for routing
    # but the config also carries targets for the other analyzer, fill them in here
    # with the existing deterministic analyzers instead of dropping mature behavior.
    if not cookie_lineage and effective_config.target_cookies and state.get("input_mode") != "goal_prompt":
        cookie_lineage = analyze_cookie_lineage(entries, list(effective_config.target_cookies))
    if not field_analysis and field_refs and state.get("input_mode") != "goal_prompt":
        matched_entry_ids = {item.entry_id for item in state.get("matched_requests", [])}
        focus_entries = [entry for entry in entries if entry.entry_id in matched_entry_ids] if matched_entry_ids else list(entries)
        field_analysis = analyze_field_lineage(
            focus_entries,
            field_refs,
            context_entries=entries,
            discovered_candidate_names={field.name for field in state.get("discovered_field_refs", [])},
        )

    claims = claims_from_cookie_results(cookie_lineage, field_analysis)
    all_gaps = [*state.get("gaps", [])]
    if state.get("health") is not None:
        all_gaps.extend(state["health"].gaps)
    if analysis_intent is not None:
        all_gaps.extend(analysis_intent.resolution_gaps)
    for item in cookie_lineage:
        all_gaps.extend(item.gaps)
    for item in field_analysis:
        all_gaps.extend(item.gaps)
    all_gaps = dedupe_gaps(all_gaps)
    recommendations = state.get("recommendations") or recommendations_from_gaps(all_gaps)

    request_rules = state.get("request_rules", [])
    auto_all = state.get("input_mode") == "auto_discovery"
    if state.get("matched_requests") or request_rules or auto_all:
        matched_requests = select_requests(
            entries,
            request_rules,
            cookie_targets={item.cookie_name for item in cookie_lineage} or set(effective_config.target_cookies),
            field_refs=field_refs,
            first_signal_time=first_signal_time(entries, cookie_lineage, field_analysis),
            auto_all_when_no_rules=auto_all,
        )
    else:
        matched_requests = state.get("matched_requests", [])

    summary = AnalysisSummary(
        generated_at=datetime.now(tz=timezone.utc).isoformat(),
        input_file=state["input_har_path"],
        entry_count=len(entries),
        matched_request_count=len(matched_requests),
        cookie_lineage_count=len(cookie_lineage),
        field_analysis_count=len(field_analysis),
        gap_count=len(all_gaps),
    )
    result = AnalysisResult(
        summary=summary,
        analysis_intent=analysis_intent,
        health=state["health"],
        targets=config_to_targets(effective_config),
        matched_requests=matched_requests,
        cookie_lineage=cookie_lineage,
        field_analysis=field_analysis,
        claims=claims,
        gaps=all_gaps,
        recommendations=recommendations,
    )
    if state.get("explanation_hook_enabled"):
        result = hook_registry.run_analysis_explainer(result, state)
    return {
        "matched_requests": matched_requests,
        "claims": claims,
        "gaps": all_gaps,
        "recommendations": recommendations,
        "final_result": result,
        "notes": extend_notes(state, "Finalized the LangGraph run into the stable AnalysisResult payload."),
    }
