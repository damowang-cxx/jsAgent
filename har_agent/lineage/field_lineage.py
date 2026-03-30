from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from har_agent.analysis.gaps import make_gap
from har_agent.inference.correlations import ScalarObservation, collect_scalar_observations
from har_agent.inference.generation_candidates import analyze_value_observation
from har_agent.models.findings import FieldAnalysisResult, FieldOccurrence
from har_agent.models.normalized import FieldRef, NormalizedEntry
from har_agent.selectors.field_selector import FieldSelector


def analyze_field_lineage(
    entries: Iterable[NormalizedEntry],
    fields: list[FieldRef],
    *,
    discovered_candidate_names: set[str] | None = None,
) -> list[FieldAnalysisResult]:
    entry_list = list(entries)
    observations = collect_scalar_observations(entry_list)
    results: list[FieldAnalysisResult] = []
    discovered_candidate_names = discovered_candidate_names or set()

    for field_ref in fields:
        selector = FieldSelector(field_ref)
        occurrences: list[FieldOccurrence] = []
        observation_refs: list[ScalarObservation] = []
        values: list[object] = []
        related_cookies: set[str] = set()
        for entry in entry_list:
            extracted, _ = selector.extract(entry)
            for value in extracted:
                occurrences.append(
                    FieldOccurrence(
                        entry_id=entry.entry_id,
                        timestamp=entry.started_at,
                        scope=field_ref.scope,
                        selector=field_ref.selector,
                        value=value,
                    )
                )
                values.append(value)
                observation_refs.append(
                    ScalarObservation(
                        entry_id=entry.entry_id,
                        timestamp=entry.started_at,
                        scope=field_ref.scope,
                        selector=field_ref.selector,
                        name=field_ref.name,
                        value="" if value is None else str(value),
                    )
                )
                for cookie in [*entry.request.cookies, *entry.response.cookies]:
                    if cookie.value == value:
                        related_cookies.add(cookie.name)

        gaps = []
        if not occurrences:
            gaps.append(make_gap("field_not_found", f"Field {field_ref.name} did not appear in the HAR.", "low"))
            results.append(
                FieldAnalysisResult(
                    name=field_ref.name,
                    scope=field_ref.scope,
                    selector=field_ref.selector,
                    discovered_candidate=field_ref.name in discovered_candidate_names,
                    occurrences=[],
                    first_seen=None,
                    values=[],
                    possible_sources=[],
                    related_cookies=[],
                    confidence="unresolved",
                    gaps=gaps,
                )
            )
            continue

        first_occurrence = occurrences[0]
        target_observation = observation_refs[0]
        encodings, heuristics, possible_sources, candidate_generation_logic = analyze_value_observation(
            target_observation,
            observations,
        )
        confidence = "low"
        if possible_sources and possible_sources[0].source_type == "response.json":
            confidence = "high"
        elif possible_sources:
            confidence = "medium"
        else:
            gaps.append(
                make_gap(
                    "cannot_confirm_js_generation_from_har_alone",
                    f"HAR alone cannot confirm how field {field_ref.name} was generated.",
                    "medium",
                )
            )
            confidence = "unresolved" if field_ref.scope.startswith("response.") else "low"

        results.append(
            FieldAnalysisResult(
                name=field_ref.name,
                scope=field_ref.scope,
                selector=field_ref.selector,
                discovered_candidate=field_ref.name in discovered_candidate_names,
                occurrences=occurrences,
                first_seen=f"{first_occurrence.scope}@{first_occurrence.entry_id}",
                values=_unique(values),
                possible_sources=possible_sources,
                related_cookies=sorted(related_cookies),
                confidence=confidence,
                gaps=gaps,
                encodings=encodings,
                heuristics=heuristics,
                candidate_generation_logic=candidate_generation_logic,
            )
        )
    return results


def _unique(values: list[Any]) -> list[Any]:
    output: list[Any] = []
    seen: set[str] = set()
    for value in values:
        marker = repr(value)
        if marker in seen:
            continue
        seen.add(marker)
        output.append(value)
    return output
