from __future__ import annotations

import re
from collections import defaultdict
from typing import Iterable

from har_agent.inference.correlations import CorrelationMatch, ScalarObservation, collect_scalar_observations, find_correlated_observations
from har_agent.inference.encodings import detect_value_encodings
from har_agent.inference.heuristics import detect_value_heuristics
from har_agent.models.findings import CandidateSource, GenerationCandidate, ValueEncoding, ValueHeuristic
from har_agent.models.normalized import FieldRef, NormalizedEntry


SUSPICIOUS_NAME_RE = re.compile(r"(token|nonce|trace|sign|sig|session|sid|uuid|device|auth)", re.IGNORECASE)


def analyze_value_observation(
    target: ScalarObservation,
    observations: list[ScalarObservation],
) -> tuple[list[ValueEncoding], list[ValueHeuristic], list[CandidateSource], list[GenerationCandidate]]:
    encodings = detect_value_encodings(target.value)
    heuristics = detect_value_heuristics(target.value)
    correlations = find_correlated_observations(target, observations)
    sources = _candidate_sources_from_correlations(correlations)
    candidates = _generation_candidates_from_correlations(target, correlations, heuristics)
    if not candidates:
        candidates.append(
            GenerationCandidate(
                type="unresolved",
                source=None,
                confidence="unresolved",
                rationale="No direct or transformed source could be established from the HAR evidence.",
            )
        )
    return encodings, heuristics, sources, candidates


def discover_candidate_fields(entries: Iterable[NormalizedEntry], explicit_fields: list[FieldRef] | None = None) -> list[FieldRef]:
    observations = collect_scalar_observations(entries)
    explicit_keys = {(field.scope, field.selector) for field in explicit_fields or []}
    grouped: dict[tuple[str, str, str], list[ScalarObservation]] = defaultdict(list)
    for observation in observations:
        if observation.scope.endswith(".cookie"):
            continue
        grouped[(observation.scope, observation.selector, observation.name)].append(observation)

    discovered: list[FieldRef] = []
    for (scope, selector, name), items in grouped.items():
        if (scope, selector) in explicit_keys:
            continue
        values = [item.value for item in items if item.value]
        repeated = len(items) >= 2
        suspicious_name = SUSPICIOUS_NAME_RE.search(name) is not None
        high_entropy_repeat = repeated and any(
            heuristic.type in {"random_like", "hash_like", "uuid"}
            for value in values
            for heuristic in detect_value_heuristics(value)
        )
        correlated_request_field = False
        if scope.startswith("request."):
            correlated_request_field = any(
                find_correlated_observations(item, observations)
                for item in items
            )
        if suspicious_name or high_entropy_repeat or correlated_request_field:
            discovered.append(FieldRef(name=name, scope=scope, selector=selector))

    discovered.sort(key=lambda item: (item.scope, item.selector))
    return discovered[:15]


def _candidate_sources_from_correlations(correlations: list[CorrelationMatch]) -> list[CandidateSource]:
    output: list[CandidateSource] = []
    seen: set[tuple[str, str]] = set()
    for correlation in correlations:
        if correlation.observation.scope.startswith("response.json"):
            source_type = "response.json"
        elif correlation.observation.scope.endswith(".cookie"):
            source_type = "cookie"
        else:
            source_type = "request_field"
        source_ref = correlation.observation.reference
        key = (source_type, source_ref)
        if key in seen:
            continue
        seen.add(key)
        output.append(
            CandidateSource(
                source_type=source_type,
                source_ref=source_ref,
                confidence=correlation.confidence,
                rationale=correlation.rationale,
            )
        )
    return output[:5]


def _generation_candidates_from_correlations(
    target: ScalarObservation,
    correlations: list[CorrelationMatch],
    heuristics: list[ValueHeuristic],
) -> list[GenerationCandidate]:
    candidates: list[GenerationCandidate] = []
    seen: set[tuple[str, str | None]] = set()

    for correlation in correlations:
        source = correlation.observation.reference
        source_scope = correlation.observation.scope
        candidate_type = None
        confidence = correlation.confidence
        if correlation.relation == "exact" and source_scope.startswith("response."):
            candidate_type = "copied_from_response"
        elif correlation.relation == "exact" and source_scope.endswith(".cookie"):
            candidate_type = "copied_from_cookie"
        elif correlation.relation == "exact":
            candidate_type = "copied_from_request_field"
        elif correlation.relation in {"url_decoded_equal", "base64_decoded_equal"}:
            candidate_type = "encoded_from_source"
        elif correlation.relation in {"contains", "prefix_suffix"}:
            candidate_type = "concatenated_from_multiple_values"
            confidence = "low"
        if candidate_type is None:
            continue
        key = (candidate_type, source)
        if key in seen:
            continue
        seen.add(key)
        candidates.append(
            GenerationCandidate(
                type=candidate_type,
                source=source,
                confidence=confidence,
                rationale=correlation.rationale,
            )
        )

    if any(heuristic.type == "timestamp" for heuristic in heuristics):
        candidates.append(
            GenerationCandidate(
                type="timestamp_derived",
                source=target.reference,
                confidence="low",
                rationale="Value looks like a timestamp or is directly timestamp-shaped.",
            )
        )

    if any(heuristic.type == "random_like" for heuristic in heuristics):
        candidates.append(
            GenerationCandidate(
                type="random_like",
                source=target.reference,
                confidence="low",
                rationale="Value has high entropy and no stronger deterministic source was found.",
            )
        )

    if any(heuristic.type == "hash_like" for heuristic in heuristics):
        candidates.append(
            GenerationCandidate(
                type="signature_like",
                source=target.reference,
                confidence="low",
                rationale="Value matches common digest/signature shapes but HAR cannot confirm the exact algorithm.",
            )
        )

    return candidates[:6]
