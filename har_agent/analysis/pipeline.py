from __future__ import annotations

from datetime import timezone, datetime
from pathlib import Path

from har_agent.analysis.gaps import assess_har_health, dedupe_gaps
from har_agent.config import AppConfig, config_to_targets
from har_agent.analysis.claims import claims_from_cookie_results
from har_agent.config import TargetRequestRule
from har_agent.models.normalized import FieldRef
from har_agent.models.report import AnalysisResult, AnalysisSummary
from har_agent.inference.generation_candidates import discover_candidate_fields
from har_agent.lineage.cookie_lineage import analyze_cookie_lineage
from har_agent.lineage.field_lineage import analyze_field_lineage
from har_agent.parsers.har_loader import load_har_document
from har_agent.parsers.normalizer import normalize_document
from har_agent.selectors.request_selector import RequestSelector, SelectionHints


def analyze_har(input_path: str | Path, config: AppConfig) -> AnalysisResult:
    document = load_har_document(input_path)
    normalized, parse_gaps = normalize_document(document)
    health = assess_har_health(document, normalized.entries, parse_gaps)
    cookie_targets = list(config.target_cookies)
    cookie_lineage = analyze_cookie_lineage(normalized.entries, cookie_targets or None)
    explicit_field_refs = [
        FieldRef(name=field.name, scope=field.scope, selector=field.selector)
        for field in config.target_fields
    ]
    discovered_field_refs = discover_candidate_fields(normalized.entries, explicit_field_refs)
    combined_field_refs = _merge_field_refs(explicit_field_refs, discovered_field_refs)
    field_analysis = analyze_field_lineage(
        normalized.entries,
        combined_field_refs,
        discovered_candidate_names={field.name for field in discovered_field_refs},
    ) if combined_field_refs else []
    first_signal_time = _first_signal_time(normalized.entries, cookie_lineage, field_analysis)
    matched_requests = _select_requests(
        normalized.entries,
        config.target_requests,
        cookie_targets={item.cookie_name for item in cookie_lineage},
        field_refs=combined_field_refs,
        first_signal_time=first_signal_time,
    )
    claims = claims_from_cookie_results(cookie_lineage, field_analysis)
    all_gaps = [*health.gaps]
    for item in cookie_lineage:
        all_gaps.extend(item.gaps)
    for item in field_analysis:
        all_gaps.extend(item.gaps)
    all_gaps = dedupe_gaps(all_gaps)
    recommendations = _recommendations_from_gaps(all_gaps)
    summary = AnalysisSummary(
        generated_at=datetime.now(tz=timezone.utc).isoformat(),
        input_file=str(input_path),
        entry_count=len(normalized.entries),
        matched_request_count=len(matched_requests),
        cookie_lineage_count=len(cookie_lineage),
        field_analysis_count=len(field_analysis),
        gap_count=len(all_gaps),
    )
    return AnalysisResult(
        summary=summary,
        health=health,
        targets=config_to_targets(config),
        matched_requests=matched_requests,
        cookie_lineage=cookie_lineage,
        field_analysis=field_analysis,
        claims=claims,
        gaps=all_gaps,
        recommendations=recommendations,
    )


def _merge_field_refs(explicit_fields: list[FieldRef], discovered_fields: list[FieldRef]) -> list[FieldRef]:
    merged: list[FieldRef] = []
    seen: set[tuple[str, str]] = set()
    for field in [*explicit_fields, *discovered_fields]:
        key = (field.scope, field.selector)
        if key in seen:
            continue
        seen.add(key)
        merged.append(field)
    return merged


def _first_signal_time(entries, cookie_lineage, field_analysis):
    candidates = []
    if entries:
        candidates.append(entries[0].started_at)
    for item in field_analysis:
        if item.occurrences:
            candidates.append(item.occurrences[0].timestamp)
    for item in cookie_lineage:
        if item.send_events:
            candidates.append(item.send_events[0].timestamp)
    return min(candidates) if candidates else None


def _select_requests(entries, rules, *, cookie_targets: set[str], field_refs: list[FieldRef], first_signal_time):
    hints = SelectionHints(
        target_cookies=cookie_targets,
        target_fields=field_refs,
        key_reference_time=first_signal_time,
    )
    if rules:
        aggregated = {}
        for rule in rules:
            selector = RequestSelector(rule)
            for matched in selector.select(entries, hints=hints):
                if matched.entry_id not in aggregated or aggregated[matched.entry_id].score < matched.score:
                    aggregated[matched.entry_id] = matched
                    aggregated[matched.entry_id].reasons.insert(0, f"rule:{rule.name}")
                else:
                    aggregated[matched.entry_id].reasons.extend(
                        reason for reason in matched.reasons if reason not in aggregated[matched.entry_id].reasons
                    )
        return sorted(aggregated.values(), key=lambda item: (-item.score, item.entry_id))

    selector = RequestSelector(TargetRequestRule(name="auto_all"))
    return selector.select(entries, hints=hints)[:20]


def _recommendations_from_gaps(gaps):
    messages = {
        "likely_sanitized_har": "The HAR looks sanitized. Re-export it with request cookies, Set-Cookie headers, and full request bodies preserved.",
        "missing_cookie_headers": "Capture a HAR that retains Cookie headers if cookie lineage is a priority.",
        "missing_set_cookie_headers": "Capture a HAR that retains Set-Cookie headers to confirm cookie setting sources.",
        "missing_request_bodies": "Re-record requests with request bodies preserved to improve field lineage and generation-candidate analysis.",
        "incomplete_timeline": "Capture a wider time window so the HAR includes the requests and responses that occur before the first target appears.",
        "cannot_confirm_js_generation_from_har_alone": "Do not treat inferred JavaScript generation as fact; use browser instrumentation in a later phase if stronger proof is required.",
    }
    output = []
    seen = set()
    for gap in gaps:
        message = messages.get(gap.code)
        if message and message not in seen:
            seen.add(message)
            output.append(message)
    return output
