from __future__ import annotations

from typing import TypedDict

from har_agent.config import AppConfig, TargetRequestRule
from har_agent.models.findings import Claim, CookieLineageResult, FieldAnalysisResult, Gap, HealthCheck, MatchedRequest
from har_agent.models.har import HarDocument
from har_agent.models.intent import AnalysisIntent, ResolvedField, ResolvedRequest
from har_agent.models.normalized import FieldRef, NormalizedEntry
from har_agent.models.report import AnalysisResult


class AgentState(TypedDict, total=False):
    input_har_path: str
    user_goal: str | None
    config_mode: str | None
    provided_config: AppConfig
    effective_config: AppConfig
    har_document: HarDocument | None
    normalized_entries: list[NormalizedEntry]
    parse_gaps: list[Gap]
    health: HealthCheck | None
    input_mode: str
    analysis_kind: str
    target_url: str | None
    target_host: str | None
    target_path: str | None
    target_cookie_name: str | None
    target_field_name: str | None
    target_field_scope: str | None
    target_field_candidate_scopes: list[str]
    resolved_request: ResolvedRequest | None
    resolved_field: ResolvedField | None
    request_rules: list[TargetRequestRule]
    selected_field_refs: list[FieldRef]
    discovered_field_refs: list[FieldRef]
    matched_requests: list[MatchedRequest]
    analysis_intent: AnalysisIntent | None
    cookie_lineage: list[CookieLineageResult]
    field_analysis: list[FieldAnalysisResult]
    claims: list[Claim]
    recommendations: list[str]
    gaps: list[Gap]
    notes: list[str]
    resolution_confidence: str
    final_result: AnalysisResult | None
    semantic_hook_enabled: bool
    explanation_hook_enabled: bool
    reasoning_hook_enabled: bool
