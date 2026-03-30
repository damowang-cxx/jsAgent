from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from har_agent.models.intent import AnalysisIntent
from har_agent.models.findings import Claim, CookieLineageResult, FieldAnalysisResult, Gap, HealthCheck, MatchedRequest


class AnalysisSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0"
    generated_at: str
    input_file: str
    entry_count: int
    matched_request_count: int
    cookie_lineage_count: int
    field_analysis_count: int
    gap_count: int


class AnalysisResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: AnalysisSummary
    analysis_intent: AnalysisIntent
    health: HealthCheck
    targets: dict[str, Any] = Field(default_factory=dict)
    matched_requests: list[MatchedRequest] = Field(default_factory=list)
    cookie_lineage: list[CookieLineageResult] = Field(default_factory=list)
    field_analysis: list[FieldAnalysisResult] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    gaps: list[Gap] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
