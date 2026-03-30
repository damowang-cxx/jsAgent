from __future__ import annotations

from typing import Any

from jsonpath_ng import parse as parse_jsonpath

from har_agent.analysis.gaps import make_gap
from har_agent.models.findings import Gap
from har_agent.models.normalized import FieldRef, NormalizedEntry


SUPPORTED_SCOPES = {
    "request.header",
    "request.query",
    "request.cookie",
    "request.form",
    "request.json",
    "response.header",
    "response.cookie",
    "response.json",
}


class FieldSelector:
    def __init__(self, field_ref: FieldRef) -> None:
        self.field_ref = field_ref

    def extract(self, entry: NormalizedEntry) -> tuple[list[Any], list[Gap]]:
        scope = self.field_ref.scope
        selector = self.field_ref.selector
        if scope not in SUPPORTED_SCOPES:
            return [], [make_gap("invalid_field_scope", f"Unsupported field scope: {scope}", "medium")]

        if scope == "request.header":
            return _extract_mapping_value(entry.request.headers, selector.lower()), []
        if scope == "request.query":
            return _extract_mapping_value(entry.request.query, selector), []
        if scope == "request.cookie":
            return _extract_cookie_value(entry.request.cookies, selector), []
        if scope == "request.form":
            data = entry.request.body.form_data if entry.request.body else None
            return _extract_mapping_value(data or {}, selector), []
        if scope == "request.json":
            body = entry.request.body.json_data if entry.request.body else None
            return _extract_jsonpath(body, selector)
        if scope == "response.header":
            return _extract_mapping_value(entry.response.headers, selector.lower()), []
        if scope == "response.cookie":
            return _extract_cookie_value(entry.response.cookies, selector), []
        if scope == "response.json":
            body = entry.response.body.json_data if entry.response.body else None
            return _extract_jsonpath(body, selector)
        return [], []


def _extract_mapping_value(mapping: dict[str, Any], key: str) -> list[Any]:
    if key in mapping:
        return [mapping[key]]
    return []


def _extract_cookie_value(cookies: list[Any], key: str) -> list[Any]:
    values: list[Any] = []
    for cookie in cookies:
        if cookie.name == key:
            values.append(cookie.value)
    return values


def _extract_jsonpath(body: Any, selector: str) -> tuple[list[Any], list[Gap]]:
    if body is None:
        return [], []
    try:
        expression = parse_jsonpath(selector)
    except Exception:
        return [], [make_gap("invalid_field_selector", f"Invalid JSONPath selector: {selector}", "medium")]
    return [match.value for match in expression.find(body)], []
