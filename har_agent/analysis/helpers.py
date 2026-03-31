from __future__ import annotations

from datetime import datetime

from har_agent.config import AppConfig, TargetRequestRule
from har_agent.inference.generation_candidates import discover_candidate_fields
from har_agent.intents.goal_resolver import (
    GoalResolver,
    build_auto_discovery_intent,
    build_structured_intent,
    intent_to_config,
)
from har_agent.models.intent import AnalysisIntent
from har_agent.models.normalized import FieldRef
from har_agent.selectors.request_selector import RequestSelector, SelectionHints


def effective_config_and_intent(
    config: AppConfig,
    entries: list,
    goal: str | None,
) -> tuple[AppConfig, AnalysisIntent]:
    if goal:
        intent = GoalResolver().resolve(goal, entries)
        return intent_to_config(intent), intent
    if config.target_requests or config.target_cookies or config.target_fields:
        return config, build_structured_intent(config)
    return config, build_auto_discovery_intent()


def cookie_target_input(config: AppConfig, intent: AnalysisIntent) -> list[str] | None:
    if intent.input_mode == "auto_discovery":
        return None
    return list(config.target_cookies)


def discovered_field_refs(
    intent: AnalysisIntent,
    entries: list,
    explicit_field_refs: list[FieldRef],
) -> list[FieldRef]:
    if intent.input_mode == "goal_prompt":
        return []
    return discover_candidate_fields(entries, explicit_field_refs)


def merge_field_refs(
    explicit_fields: list[FieldRef],
    discovered_fields: list[FieldRef],
) -> list[FieldRef]:
    merged: list[FieldRef] = []
    seen: set[tuple[str, str]] = set()
    for field in [*explicit_fields, *discovered_fields]:
        key = (field.scope, field.selector)
        if key in seen:
            continue
        seen.add(key)
        merged.append(field)
    return merged


def first_signal_time(entries, cookie_lineage, field_analysis) -> datetime | None:
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


def select_requests(
    entries,
    rules,
    *,
    cookie_targets: set[str],
    field_refs: list[FieldRef],
    first_signal_time,
    auto_all_when_no_rules: bool,
):
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

    if auto_all_when_no_rules:
        selector = RequestSelector(TargetRequestRule(name="auto_all"))
        return selector.select(entries, hints=hints)[:20]
    return []


def recommendations_from_gaps(gaps):
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
