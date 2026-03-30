from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable

from har_agent.config import TargetFieldConfig, TargetRequestRule
from har_agent.models.findings import MatchedRequest
from har_agent.models.normalized import FieldRef, NormalizedEntry
from har_agent.selectors.field_selector import FieldSelector


@dataclass(slots=True)
class SelectionHints:
    target_cookies: set[str] = field(default_factory=set)
    target_fields: list[FieldRef] = field(default_factory=list)
    key_reference_time: datetime | None = None


class RequestSelector:
    def __init__(self, rule: TargetRequestRule) -> None:
        self.rule = rule
        self._regex = re.compile(rule.url_regex) if rule.url_regex else None

    def select(self, entries: Iterable[NormalizedEntry], hints: SelectionHints | None = None) -> list[MatchedRequest]:
        matched: list[MatchedRequest] = []
        for entry in entries:
            result = self.match(entry, hints=hints)
            if result is not None:
                matched.append(result)
        matched.sort(key=lambda item: (-item.score, item.entry_id))
        return matched

    def match(self, entry: NormalizedEntry, hints: SelectionHints | None = None) -> MatchedRequest | None:
        reasons: list[str] = []
        score = 0.0
        hints = hints or SelectionHints()

        if self.rule.url_contains:
            if self.rule.url_contains not in entry.request.url:
                return None
            score += 40
            reasons.append(f"url_contains:{self.rule.url_contains}")

        if self._regex:
            if not self._regex.search(entry.request.url):
                return None
            score += 45
            reasons.append(f"url_regex:{self.rule.url_regex}")

        if self.rule.methods:
            methods = {method.upper() for method in self.rule.methods}
            if entry.request.method.upper() not in methods:
                return None
            score += 10
            reasons.append(f"method:{entry.request.method.upper()}")

        if self.rule.status_in:
            if entry.response.status not in set(self.rule.status_in):
                return None
            score += 8
            reasons.append(f"status:{entry.response.status}")

        if self.rule.host_contains:
            if self.rule.host_contains not in entry.request.host:
                return None
            score += 15
            reasons.append(f"host_contains:{self.rule.host_contains}")

        if self.rule.header_exists:
            for header_name in self.rule.header_exists:
                if header_name.lower() not in entry.request.headers:
                    return None
                score += 5
                reasons.append(f"header_exists:{header_name.lower()}")

        if self.rule.cookie_exists:
            request_cookie_names = {cookie.name for cookie in entry.request.cookies}
            response_cookie_names = {cookie.name for cookie in entry.response.cookies}
            for cookie_name in self.rule.cookie_exists:
                if cookie_name not in request_cookie_names and cookie_name not in response_cookie_names:
                    return None
                score += 12
                reasons.append(f"cookie_exists:{cookie_name}")

        request_blob = _entry_text_blob(entry.request.headers, entry.request.query, entry.request.body.raw_text if entry.request.body else None)
        response_blob = _entry_text_blob(entry.response.headers, {}, entry.response.body.raw_text if entry.response.body else None)

        for needle in self.rule.body_contains:
            if needle not in request_blob:
                return None
            score += 6
            reasons.append(f"body_contains:{needle}")

        for needle in self.rule.response_contains:
            if needle not in response_blob:
                return None
            score += 6
            reasons.append(f"response_contains:{needle}")

        hint_score, hint_reasons = _score_hints(entry, hints)
        score += hint_score
        reasons.extend(hint_reasons)

        if not reasons:
            reasons.append("default_all_entries")

        return MatchedRequest(
            entry_id=entry.entry_id,
            method=entry.request.method,
            url=entry.request.url,
            status=entry.response.status,
            score=round(score, 2),
            reasons=reasons,
        )


def _entry_text_blob(headers: dict[str, str], query: dict[str, object], body_text: str | None) -> str:
    parts = [
        json.dumps(headers, ensure_ascii=False, sort_keys=True),
        json.dumps(query, ensure_ascii=False, sort_keys=True),
        body_text or "",
    ]
    return "\n".join(parts)


def _score_hints(entry: NormalizedEntry, hints: SelectionHints) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    if hints.target_cookies:
        cookie_names = {cookie.name for cookie in entry.request.cookies} | {cookie.name for cookie in entry.response.cookies}
        for name in sorted(hints.target_cookies):
            if name in cookie_names:
                score += 8
                reasons.append(f"hint_cookie:{name}")

    for field_ref in hints.target_fields:
        values, _ = FieldSelector(field_ref).extract(entry)
        if values:
            score += 7
            reasons.append(f"hint_field:{field_ref.name}")

    if hints.key_reference_time is not None:
        delta = abs((entry.started_at - hints.key_reference_time).total_seconds())
        proximity = max(0.0, 5.0 - min(delta, 25.0) / 5.0)
        if proximity > 0:
            score += proximity
            reasons.append("near_first_key_appearance")

    return score, reasons


def field_refs_from_config(fields: list[TargetFieldConfig]) -> list[FieldRef]:
    return [FieldRef(name=field.name, scope=field.scope, selector=field.selector) for field in fields]
