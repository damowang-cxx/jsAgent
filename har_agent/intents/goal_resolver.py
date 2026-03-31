from __future__ import annotations

import re
from urllib.parse import urlsplit

from har_agent.analysis.gaps import make_gap
from har_agent.config import AppConfig, TargetFieldConfig, TargetRequestRule
from har_agent.models.intent import AnalysisIntent, ResolvedField, ResolvedRequest
from har_agent.models.normalized import FieldRef, NormalizedEntry
from har_agent.selectors.field_selector import FieldSelector
from har_agent.selectors.request_selector import RequestSelector


AUTO_SCOPE_ORDER = [
    "response.json",
    "request.json",
    "request.form",
    "request.header",
    "response.header",
    "request.query",
    "request.cookie",
    "response.cookie",
]

EXPLICIT_SCOPE_MAP = {
    "request.json": ["request.json", "request json", "请求json", "request body", "请求体"],
    "response.json": ["response.json", "response json", "响应json", "response body", "响应体", "返回体", "返回json"],
    "request.header": ["request.header", "request header", "请求头"],
    "response.header": ["response.header", "response header", "响应头", "返回头"],
    "request.query": ["request.query", "query string", "request query", "query参数", "查询参数"],
    "request.form": ["request.form", "request form", "form data", "表单"],
    "request.cookie": ["request.cookie"],
    "response.cookie": ["response.cookie"],
}

GENERIC_TARGET_TOKENS = {
    "analyze",
    "analysis",
    "field",
    "fields",
    "cookie",
    "cookies",
    "endpoint",
    "api",
    "request",
    "response",
    "generation",
    "logic",
    "origin",
    "source",
    "set",
}

URL_RE = re.compile(r"https?://[^\s\"'“”‘’>]+", re.IGNORECASE)
HOST_RE = re.compile(r"\b(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}\b")
PATH_RE = re.compile(r"/[A-Za-z0-9._~!$&'()*+,;=:@%/-]+")
QUOTED_RE = re.compile(r"[\"“'‘]([^\"”'’]{1,200})[\"”'’]")
FIELD_RE = re.compile(r"([\w\u4e00-\u9fff-]+)\s*字段")
COOKIE_NAME_RE = re.compile(r"(?:cookie|Cookie)\s*(?:name|named|called)?\s*[\"“'‘]?([\w-]{1,128})[\"”'’]?")


class GoalResolver:
    def resolve(self, prompt: str, entries: list[NormalizedEntry]) -> AnalysisIntent:
        cleaned_prompt = prompt.strip()
        lowered = cleaned_prompt.lower()
        analysis_kind = _detect_analysis_kind(cleaned_prompt, lowered)
        resolution_notes: list[str] = []
        resolution_gaps = []

        full_url = _extract_full_url(cleaned_prompt)
        host_contains, path_contains = _extract_host_and_path(cleaned_prompt, full_url)
        resolved_request, matched_entries = _resolve_request(entries, full_url, host_contains, path_contains)
        if full_url:
            resolution_notes.append("Full URL extracted from goal prompt.")
        elif host_contains or path_contains:
            resolution_notes.append("Partial request target extracted from goal prompt.")
        else:
            resolution_gaps.append(
                make_gap("goal_missing_request_target", "No request URL or path could be extracted from the goal prompt.", "medium")
            )

        if resolved_request.match_count > 1:
            resolution_gaps.append(
                make_gap(
                    "goal_ambiguous_request_match",
                    f"Goal request target matched {resolved_request.match_count} requests in the HAR.",
                    "medium",
                )
            )
            resolution_notes.append("Request target matched multiple HAR entries and will be kept as a ranked candidate set.")
        elif resolved_request.match_count == 0 and (resolved_request.url or resolved_request.host_contains or resolved_request.path_contains):
            resolution_gaps.append(
                make_gap("goal_no_matching_request", "Goal request target did not match any request in the HAR.", "medium")
            )

        scope_hint = _detect_explicit_scope_hint(cleaned_prompt, lowered)
        field_name = _extract_field_name(cleaned_prompt, analysis_kind)
        cookie_name = _extract_cookie_name(cleaned_prompt, analysis_kind, field_name)

        resolved_field = None
        if analysis_kind.startswith("field_"):
            if not field_name:
                resolution_gaps.append(
                    make_gap("goal_missing_field_name", "No target field name could be extracted from the goal prompt.", "high")
                )
            else:
                resolved_field, field_notes, field_gaps = _resolve_field(
                    entries=entries,
                    matched_entries=matched_entries or entries,
                    field_name=field_name,
                    scope_hint=scope_hint,
                )
                resolution_notes.extend(field_notes)
                resolution_gaps.extend(field_gaps)
        elif analysis_kind.startswith("cookie_"):
            if not cookie_name:
                resolution_gaps.append(
                    make_gap("goal_missing_cookie_name", "No target cookie name could be extracted from the goal prompt.", "high")
                )
            else:
                resolution_notes.append("Cookie name extracted from goal prompt.")

        confidence = _resolution_confidence(
            analysis_kind=analysis_kind,
            full_url=bool(full_url),
            partial_request=bool(host_contains or path_contains),
            field_resolved=bool(resolved_field and (resolved_field.resolved_scopes or resolved_field.candidate_scopes)),
            cookie_resolved=bool(cookie_name),
            gaps=resolution_gaps,
        )
        return AnalysisIntent(
            input_mode="goal_prompt",
            original_prompt=cleaned_prompt,
            analysis_kind=analysis_kind,
            resolved_request=resolved_request,
            resolved_field=resolved_field,
            resolved_cookie_name=cookie_name,
            resolution_confidence=confidence,
            resolution_gaps=resolution_gaps,
            resolution_notes=resolution_notes,
        )


def intent_to_config(intent: AnalysisIntent) -> AppConfig:
    if intent.input_mode != "goal_prompt":
        raise ValueError("intent_to_config only supports goal_prompt intents")

    request_rules: list[TargetRequestRule] = []
    if intent.resolved_request and (intent.resolved_request.url_contains or intent.resolved_request.host_contains):
        request_rules.append(
            TargetRequestRule(
                name="goal_target",
                url_contains=intent.resolved_request.url_contains,
                host_contains=intent.resolved_request.host_contains,
            )
        )

    target_fields: list[TargetFieldConfig] = []
    if intent.analysis_kind.startswith("field_") and intent.resolved_field and intent.resolved_field.name:
        execution_scopes = intent.resolved_field.resolved_scopes or intent.resolved_field.candidate_scopes
        selectors = intent.resolved_field.selectors or [_selector_for_scope(scope, intent.resolved_field.name) for scope in execution_scopes]
        for scope, selector in zip(execution_scopes, selectors):
            target_fields.append(
                TargetFieldConfig(
                    name=intent.resolved_field.name,
                    scope=scope,
                    selector=selector,
                )
            )

    target_cookies = [intent.resolved_cookie_name] if intent.analysis_kind.startswith("cookie_") and intent.resolved_cookie_name else []
    return AppConfig(
        target_requests=request_rules,
        target_cookies=target_cookies,
        target_fields=target_fields,
    )


def build_structured_intent(config: AppConfig) -> AnalysisIntent:
    analysis_kind = "field_origin"
    if config.target_cookies and not config.target_fields:
        analysis_kind = "cookie_set_source"
    elif config.target_fields:
        analysis_kind = "field_origin"

    return AnalysisIntent(
        input_mode="structured_config",
        original_prompt=None,
        analysis_kind=analysis_kind,
        resolved_request=None,
        resolved_field=None,
        resolved_cookie_name=config.target_cookies[0] if config.target_cookies else None,
        resolution_confidence="high",
        resolution_gaps=[],
        resolution_notes=["Using explicit structured config as the analysis target source."],
    )


def build_auto_discovery_intent() -> AnalysisIntent:
    return AnalysisIntent(
        input_mode="auto_discovery",
        original_prompt=None,
        analysis_kind="auto_discovery",
        resolved_request=None,
        resolved_field=None,
        resolved_cookie_name=None,
        resolution_confidence="high",
        resolution_gaps=[],
        resolution_notes=["No goal prompt or structured config was provided; running automatic discovery."],
    )


def _detect_analysis_kind(prompt: str, lowered: str) -> str:
    generation_keywords = ["生成逻辑", "generation logic", "生成方式"]
    set_source_keywords = ["设置源", "set-cookie", "set cookie", "set source", "设置来源"]
    cookie_like = "cookie" in lowered

    if cookie_like and any(keyword in lowered or keyword in prompt for keyword in set_source_keywords):
        return "cookie_set_source"
    if cookie_like and any(keyword in lowered or keyword in prompt for keyword in generation_keywords):
        return "cookie_generation_logic"
    if cookie_like:
        return "cookie_set_source" if "来源" in prompt else "cookie_generation_logic"
    if any(keyword in lowered or keyword in prompt for keyword in generation_keywords):
        return "field_generation_logic"
    return "field_origin"


def _extract_full_url(prompt: str) -> str | None:
    match = URL_RE.search(prompt)
    if not match:
        return None
    return match.group(0).rstrip("，。；,.);）》]")


def _extract_host_and_path(prompt: str, full_url: str | None) -> tuple[str | None, str | None]:
    if full_url:
        parts = urlsplit(full_url)
        return parts.hostname, parts.path or None

    host_match = HOST_RE.search(prompt)
    path_matches = PATH_RE.findall(prompt)
    host = host_match.group(0) if host_match else None
    path = max(path_matches, key=len) if path_matches else None
    return host, path


def _resolve_request(
    entries: list[NormalizedEntry],
    full_url: str | None,
    host_contains: str | None,
    path_contains: str | None,
) -> tuple[ResolvedRequest, list[NormalizedEntry]]:
    rule = None
    if full_url:
        rule = TargetRequestRule(name="goal_target", url_contains=full_url, host_contains=host_contains)
    elif host_contains or path_contains:
        rule = TargetRequestRule(name="goal_target", url_contains=path_contains, host_contains=host_contains)

    if rule is None:
        return ResolvedRequest(), []

    matches = RequestSelector(rule).select(entries)
    entry_by_id = {entry.entry_id: entry for entry in entries}
    matched_entries = [entry_by_id[item.entry_id] for item in matches if item.entry_id in entry_by_id]
    resolved_request = ResolvedRequest(
        url=full_url,
        url_contains=rule.url_contains,
        host_contains=rule.host_contains,
        path_contains=path_contains,
        matched_entry_ids=[item.entry_id for item in matches],
        matched_urls=[item.url for item in matches[:10]],
        match_count=len(matches),
    )
    return resolved_request, matched_entries


def _detect_explicit_scope_hint(prompt: str, lowered: str) -> str | None:
    for scope, keywords in EXPLICIT_SCOPE_MAP.items():
        for keyword in keywords:
            if keyword.lower() in lowered:
                return scope
    if "cookie" in lowered:
        return "request.cookie"
    return None


def _extract_field_name(prompt: str, analysis_kind: str) -> str | None:
    candidates = [item.strip() for item in QUOTED_RE.findall(prompt) if item.strip()]
    filtered = [item for item in candidates if not item.lower().startswith("http")]
    if filtered:
        return filtered[-1]
    field_match = FIELD_RE.search(prompt)
    if field_match:
        return field_match.group(1)
    if analysis_kind.startswith("field_"):
        scrubbed = URL_RE.sub(" ", prompt)
        before_field = re.search(r"\b([A-Za-z_][A-Za-z0-9_-]{0,127})\b\s+field\b", scrubbed, re.IGNORECASE)
        if before_field and before_field.group(1).lower() not in GENERIC_TARGET_TOKENS:
            return before_field.group(1)
        after_field = re.search(r"\bfield\b\s+[\"“'‘]?([A-Za-z_][A-Za-z0-9_-]{0,127})[\"”'’]?", scrubbed, re.IGNORECASE)
        if after_field and after_field.group(1).lower() not in GENERIC_TARGET_TOKENS:
            return after_field.group(1)
    return None


def _extract_cookie_name(prompt: str, analysis_kind: str, field_name: str | None) -> str | None:
    if not analysis_kind.startswith("cookie_"):
        return None
    match = COOKIE_NAME_RE.search(prompt)
    if match:
        candidate = match.group(1)
        if candidate.lower() not in GENERIC_TARGET_TOKENS:
            return candidate
    if field_name and field_name.lower() not in GENERIC_TARGET_TOKENS:
        return field_name
    return None


def _resolve_field(
    *,
    entries: list[NormalizedEntry],
    matched_entries: list[NormalizedEntry],
    field_name: str,
    scope_hint: str | None,
) -> tuple[ResolvedField, list[str], list]:
    notes: list[str] = []
    gaps = []
    used_matched_entries = bool(matched_entries)
    candidate_entries = matched_entries or entries

    if scope_hint:
        scopes = _expand_scope_hint(scope_hint)
        selectors = [_selector_for_scope(scope, field_name) for scope in scopes]
        notes.append("Field scope was explicitly hinted in the goal prompt.")
        return (
            ResolvedField(
                name=field_name,
                scope_hint=scope_hint,
                resolved_scopes=scopes,
                candidate_scopes=scopes,
                selectors=selectors,
            ),
            notes,
            gaps,
        )

    candidate_scopes: list[str] = []
    selectors: list[str] = []
    for scope in AUTO_SCOPE_ORDER:
        selector = _selector_for_scope(scope, field_name)
        field_ref = FieldRef(name=field_name, scope=scope, selector=selector)
        if any(FieldSelector(field_ref).extract(entry)[0] for entry in candidate_entries):
            candidate_scopes.append(scope)
            selectors.append(selector)

    if len(candidate_scopes) == 1:
        if used_matched_entries:
            notes.append("Field scope was inferred uniquely from HAR entries matched to the target request.")
        else:
            notes.append("Field scope was inferred uniquely from HAR entries because no request match was available.")
        return (
            ResolvedField(
                name=field_name,
                scope_hint=None,
                resolved_scopes=candidate_scopes,
                candidate_scopes=candidate_scopes,
                selectors=selectors,
            ),
            notes,
            gaps,
        )

    if len(candidate_scopes) > 1:
        gaps.append(
            make_gap(
                "goal_ambiguous_field_scope",
                f"Field {field_name} appears in multiple scopes: {', '.join(candidate_scopes)}.",
                "medium",
            )
        )
        if used_matched_entries:
            notes.append("Field scope is ambiguous within the matched request set; all matching candidate scopes will be analyzed.")
        else:
            notes.append("Field scope is ambiguous across HAR entries; all matching candidate scopes will be analyzed.")
        return (
            ResolvedField(
                name=field_name,
                scope_hint=None,
                resolved_scopes=[],
                candidate_scopes=candidate_scopes,
                selectors=selectors,
            ),
            notes,
            gaps,
        )

    gaps.append(make_gap("goal_no_matching_field", f"Field {field_name} was not found in the HAR under supported scopes.", "medium"))
    return (
        ResolvedField(
            name=field_name,
            scope_hint=None,
            resolved_scopes=[],
            candidate_scopes=[],
            selectors=[],
        ),
        notes,
        gaps,
    )


def _expand_scope_hint(scope_hint: str) -> list[str]:
    if scope_hint == "cookie":
        return ["request.cookie", "response.cookie"]
    return [scope_hint]


def _selector_for_scope(scope: str, field_name: str) -> str:
    if scope.endswith(".json"):
        return f"$..{field_name}"
    return field_name


def _resolution_confidence(
    *,
    analysis_kind: str,
    full_url: bool,
    partial_request: bool,
    field_resolved: bool,
    cookie_resolved: bool,
    gaps: list,
) -> str:
    if any(gap.code == "goal_no_matching_request" for gap in gaps):
        return "low"
    if analysis_kind.startswith("field_") and not field_resolved:
        return "low" if full_url or partial_request else "unresolved"
    if analysis_kind.startswith("cookie_") and not cookie_resolved:
        return "low" if full_url or partial_request else "unresolved"
    if full_url and not any(gap.code.startswith("goal_ambiguous") or gap.code == "goal_no_matching_request" for gap in gaps):
        return "high"
    if full_url or partial_request:
        return "medium"
    if field_resolved or cookie_resolved:
        return "low"
    return "unresolved"
