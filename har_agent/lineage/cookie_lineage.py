from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from har_agent.analysis.confidence import downgrade_for_gaps
from har_agent.analysis.gaps import make_gap
from har_agent.inference.correlations import ScalarObservation, collect_scalar_observations
from har_agent.inference.generation_candidates import analyze_value_observation
from har_agent.models.findings import CandidateSource, CookieEvent, CookieLineageResult, Gap
from har_agent.models.normalized import CookieRecord, NormalizedEntry


@dataclass(slots=True)
class _CookieObservation:
    entry_id: str
    timestamp: datetime
    source: str
    cookie: CookieRecord


def analyze_cookie_lineage(entries: Iterable[NormalizedEntry], target_cookies: list[str] | None = None) -> list[CookieLineageResult]:
    entry_list = list(entries)
    observations = collect_scalar_observations(entry_list)
    available_names = sorted(
        {
            cookie.name
            for entry in entry_list
            for cookie in [*entry.request.cookies, *entry.response.cookies]
        }
    )
    cookie_names = target_cookies or available_names
    return [_analyze_single_cookie(entry_list, observations, cookie_name) for cookie_name in cookie_names]


def _analyze_single_cookie(
    entries: list[NormalizedEntry],
    observations: list[ScalarObservation],
    cookie_name: str,
) -> CookieLineageResult:
    set_events: list[_CookieObservation] = []
    send_events: list[_CookieObservation] = []

    for entry in entries:
        for cookie in entry.response.cookies:
            if cookie.name == cookie_name:
                set_events.append(_CookieObservation(entry.entry_id, entry.started_at, "response.set-cookie", cookie))
        for cookie in entry.request.cookies:
            if cookie.name == cookie_name:
                send_events.append(_CookieObservation(entry.entry_id, entry.started_at, "request.cookie", cookie))

    all_events = sorted([*set_events, *send_events], key=lambda item: item.timestamp)
    first_seen = f"{all_events[0].source}@{all_events[0].entry_id}" if all_events else "unresolved"
    gaps: list[Gap] = []
    alternatives: list[str] = []
    confidence = "unresolved"
    candidates: list[CandidateSource] = []
    encodings = []
    heuristics = []
    candidate_generation_logic = []

    if set_events and not send_events:
        primary = set_events[0]
        confidence = "high"
        candidates.append(
            CandidateSource(
                source_type="response.set-cookie",
                source_ref=primary.entry_id,
                confidence="high",
                rationale="Cookie first appears in a response Set-Cookie and was never observed being sent later in the HAR.",
            )
        )
    elif send_events:
        first_send = send_events[0]
        prior_set_events = [event for event in set_events if event.timestamp <= first_send.timestamp]
        exact_value_matches = [event for event in prior_set_events if event.cookie.value == first_send.cookie.value]

        if exact_value_matches:
            primary = exact_value_matches[-1]
            candidates.append(
                CandidateSource(
                    source_type="response.set-cookie",
                    source_ref=primary.entry_id,
                    confidence="high",
                    rationale="A prior Set-Cookie had the same name and exact value before the cookie was sent in a later request.",
                )
            )
            confidence = "high"
            if len(exact_value_matches) > 1:
                gaps.append(
                    make_gap(
                        "multiple_same_name_cookie_candidates",
                        f"Multiple exact Set-Cookie candidates were found for {cookie_name}.",
                        "medium",
                    )
                )
        elif prior_set_events:
            for candidate in prior_set_events[-3:]:
                candidates.append(
                    CandidateSource(
                        source_type="response.set-cookie",
                        source_ref=candidate.entry_id,
                        confidence="medium",
                        rationale="A prior Set-Cookie with the same name was found, but the value did not exactly match the later request value.",
                    )
                )
            confidence = "medium"
            if len(prior_set_events) > 1:
                gaps.append(
                    make_gap(
                        "multiple_same_name_cookie_candidates",
                        f"Multiple Set-Cookie candidates with the same name were found for {cookie_name}.",
                        "medium",
                    )
                )
        else:
            gaps.extend(
                [
                    make_gap(
                        "missing_prior_requests_before_har_start",
                        f"{cookie_name} was first seen in a request without any earlier Set-Cookie in the HAR.",
                        "medium",
                    ),
                    make_gap(
                        "cannot_confirm_js_generation_from_har_alone",
                        f"HAR alone cannot confirm whether {cookie_name} was created by JavaScript or existed before capture started.",
                        "medium",
                    ),
                ]
            )
            alternatives.extend(
                [
                    "The cookie may have existed before HAR capture started.",
                    "The cookie may have been set by another tab, redirect chain, or external context.",
                    "The cookie may have been written by front-end JavaScript, but HAR alone cannot confirm that.",
                    "The setting source may be missing because the HAR timeline is incomplete.",
                ]
            )
            confidence = "low"

    value_observation = _build_value_observation(cookie_name, set_events, send_events)
    if value_observation is not None and value_observation.value:
        encodings, heuristics, inferred_sources, candidate_generation_logic = analyze_value_observation(
            value_observation,
            observations,
        )
        existing_refs = {(candidate.source_type, candidate.source_ref) for candidate in candidates}
        for inferred_source in inferred_sources:
            key = (inferred_source.source_type, inferred_source.source_ref)
            if key in existing_refs:
                continue
            candidates.append(inferred_source)
            existing_refs.add(key)

    confidence = downgrade_for_gaps(confidence, gaps)
    send_event_models = [
        CookieEvent(
            entry_id=event.entry_id,
            timestamp=event.timestamp,
            source=event.source,
            value=event.cookie.value,
        )
        for event in send_events
    ]
    return CookieLineageResult(
        cookie_name=cookie_name,
        first_seen=first_seen,
        set_candidates=candidates,
        send_events=send_event_models,
        confidence=confidence,
        gaps=gaps,
        alternatives=alternatives,
        encodings=encodings,
        heuristics=heuristics,
        candidate_generation_logic=candidate_generation_logic,
    )


def _build_value_observation(
    cookie_name: str,
    set_events: list[_CookieObservation],
    send_events: list[_CookieObservation],
) -> ScalarObservation | None:
    if send_events:
        primary = send_events[0]
        return ScalarObservation(
            entry_id=primary.entry_id,
            timestamp=primary.timestamp,
            scope="request.cookie",
            selector=cookie_name,
            name=cookie_name,
            value="" if primary.cookie.value is None else primary.cookie.value,
        )
    if set_events:
        primary = set_events[0]
        return ScalarObservation(
            entry_id=primary.entry_id,
            timestamp=primary.timestamp,
            scope="response.cookie",
            selector=cookie_name,
            name=cookie_name,
            value="" if primary.cookie.value is None else primary.cookie.value,
        )
    return None
