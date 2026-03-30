from __future__ import annotations

from collections import Counter
from typing import Iterable

from har_agent.models.findings import Gap, HealthCheck
from har_agent.models.har import HarDocument
from har_agent.models.normalized import NormalizedEntry


KNOWN_GAP_CODES = {
    "missing_prior_requests_before_har_start",
    "likely_sanitized_har",
    "missing_cookie_headers",
    "missing_set_cookie_headers",
    "missing_request_bodies",
    "multiple_same_name_cookie_candidates",
    "cannot_confirm_js_generation_from_har_alone",
    "incomplete_timeline",
    "parse_error_body",
    "parse_error_cookie",
}


def make_gap(code: str, message: str, severity: str = "medium") -> Gap:
    return Gap(code=code, message=message, severity=severity)


def dedupe_gaps(gaps: Iterable[Gap]) -> list[Gap]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[Gap] = []
    for gap in gaps:
        key = (gap.code, gap.message, gap.severity)
        if key in seen:
            continue
        seen.add(key)
        unique.append(gap)
    return unique


def assess_har_health(document: HarDocument, entries: list[NormalizedEntry], parse_gaps: list[Gap]) -> HealthCheck:
    gaps: list[Gap] = []
    empty_entries = len(entries) == 0
    if empty_entries:
        gaps.append(make_gap("incomplete_timeline", "HAR contains no entries", "high"))

    pages_count = len(document.log.pages)
    missing_page_refs = sum(1 for entry in entries if entry.page_ref is None)
    if pages_count == 0 or missing_page_refs == len(entries) and entries:
        gaps.append(make_gap("incomplete_timeline", "HAR page scope metadata is incomplete", "medium"))

    request_cookie_count = sum(len(entry.request.cookies) for entry in entries)
    response_cookie_count = sum(len(entry.response.cookies) for entry in entries)
    if request_cookie_count == 0:
        gaps.append(make_gap("missing_cookie_headers", "No request cookies were present in the HAR", "medium"))
    if response_cookie_count == 0:
        gaps.append(make_gap("missing_set_cookie_headers", "No response Set-Cookie values were present in the HAR", "medium"))

    likely_sanitized = request_cookie_count == 0 and response_cookie_count == 0 and len(entries) > 0
    if likely_sanitized:
        gaps.append(
            make_gap(
                "likely_sanitized_har",
                "HAR appears sanitized because both request cookies and response Set-Cookie values are absent",
                "medium",
            )
        )

    body_candidates = [entry for entry in entries if entry.request.method not in {"GET", "HEAD", "OPTIONS"}]
    missing_bodies = sum(1 for entry in body_candidates if entry.request.body is None or not entry.request.body.raw_text)
    body_empty_ratio = (missing_bodies / len(body_candidates)) if body_candidates else 0.0
    if missing_bodies > 0:
        gaps.append(
            make_gap(
                "missing_request_bodies",
                f"{missing_bodies} state-changing requests did not contain request bodies",
                "low" if body_empty_ratio < 0.5 else "medium",
            )
        )

    incomplete_timeline = False
    if any(gap.code == "incomplete_timeline" for gap in parse_gaps):
        incomplete_timeline = True
    if any(any(isinstance(value, (int, float)) and value < -1 for value in entry.timings.values()) for entry in entries):
        incomplete_timeline = True
        gaps.append(make_gap("incomplete_timeline", "HAR contains negative timing values", "medium"))

    gaps.extend(parse_gaps)
    deduped = dedupe_gaps(gaps)
    stats = {
        "request_cookie_count": request_cookie_count,
        "response_cookie_count": response_cookie_count,
        "missing_page_refs": missing_page_refs,
        "gap_counts": dict(Counter(gap.code for gap in deduped)),
    }
    return HealthCheck(
        entries_count=len(entries),
        pages_count=pages_count,
        empty_entries=empty_entries,
        likely_sanitized=likely_sanitized,
        missing_cookie_headers=request_cookie_count == 0,
        missing_set_cookie_headers=response_cookie_count == 0,
        missing_request_bodies=missing_bodies > 0,
        incomplete_timeline=incomplete_timeline,
        body_empty_ratio=body_empty_ratio,
        gaps=deduped,
        stats=stats,
    )
