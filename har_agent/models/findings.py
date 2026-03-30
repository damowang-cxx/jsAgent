from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Gap(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    severity: str


class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reference: str
    detail: str
    kind: str = "observation"


class CandidateSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_type: str
    source_ref: str
    confidence: str
    rationale: str


class ValueEncoding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    confidence: str
    rationale: str
    decoded_value: str | None = None


class ValueHeuristic(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    confidence: str
    rationale: str


class GenerationCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    source: str | None = None
    confidence: str
    rationale: str


class MatchedRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entry_id: str
    method: str
    url: str
    status: int
    score: float
    reasons: list[str] = Field(default_factory=list)


class CookieEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entry_id: str
    timestamp: datetime
    source: str
    value: str | None = None


class CookieLineageResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cookie_name: str
    first_seen: str
    set_candidates: list[CandidateSource] = Field(default_factory=list)
    send_events: list[CookieEvent] = Field(default_factory=list)
    confidence: str
    gaps: list[Gap] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)
    encodings: list[ValueEncoding] = Field(default_factory=list)
    heuristics: list[ValueHeuristic] = Field(default_factory=list)
    candidate_generation_logic: list[GenerationCandidate] = Field(default_factory=list)


class FieldOccurrence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entry_id: str
    timestamp: datetime
    scope: str
    selector: str
    value: Any


class FieldAnalysisResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    scope: str
    selector: str
    discovered_candidate: bool = False
    occurrences: list[FieldOccurrence] = Field(default_factory=list)
    first_seen: str | None = None
    values: list[Any] = Field(default_factory=list)
    possible_sources: list[CandidateSource] = Field(default_factory=list)
    related_cookies: list[str] = Field(default_factory=list)
    confidence: str
    gaps: list[Gap] = Field(default_factory=list)
    encodings: list[ValueEncoding] = Field(default_factory=list)
    heuristics: list[ValueHeuristic] = Field(default_factory=list)
    candidate_generation_logic: list[GenerationCandidate] = Field(default_factory=list)


class HealthCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entries_count: int
    pages_count: int
    empty_entries: bool = False
    likely_sanitized: bool = False
    missing_cookie_headers: bool = False
    missing_set_cookie_headers: bool = False
    missing_request_bodies: bool = False
    incomplete_timeline: bool = False
    body_empty_ratio: float = 0.0
    gaps: list[Gap] = Field(default_factory=list)
    stats: dict[str, Any] = Field(default_factory=dict)


class Claim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: str
    title: str
    claim: str
    confidence: str
    evidence: list[EvidenceItem] = Field(default_factory=list)
    gaps: list[Gap] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)
    related_entries: list[str] = Field(default_factory=list)
    kind: str
