from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from har_agent.models.findings import Gap


class ResolvedRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str | None = None
    url_contains: str | None = None
    host_contains: str | None = None
    path_contains: str | None = None
    matched_entry_ids: list[str] = Field(default_factory=list)
    matched_urls: list[str] = Field(default_factory=list)
    match_count: int = 0


class ResolvedField(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    scope_hint: str | None = None
    resolved_scopes: list[str] = Field(default_factory=list)
    candidate_scopes: list[str] = Field(default_factory=list)
    selectors: list[str] = Field(default_factory=list)


class AnalysisIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    input_mode: str
    original_prompt: str | None = None
    analysis_kind: str
    resolved_request: ResolvedRequest | None = None
    resolved_field: ResolvedField | None = None
    resolved_cookie_name: str | None = None
    resolution_confidence: str
    resolution_gaps: list[Gap] = Field(default_factory=list)
    resolution_notes: list[str] = Field(default_factory=list)
