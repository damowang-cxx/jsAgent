from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, urlsplit

from har_agent.models.findings import Gap
from har_agent.models.har import HarDocument, HarEntry, HarNameValue
from har_agent.models.normalized import CookieRecord, NormalizedEntry, NormalizedHar, RequestData, ResponseData
from har_agent.parsers.body_parser import parse_body_data
from har_agent.parsers.cookie_parser import parse_cookie_header, parse_cookie_objects, parse_set_cookie_header


def _gap(code: str, message: str, severity: str = "medium") -> Gap:
    return Gap(code=code, message=message, severity=severity)


def _parse_datetime(value: str) -> datetime:
    if value.endswith("Z"):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _flatten_header_values(headers: list[HarNameValue]) -> dict[str, str]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for header in headers:
        name = header.name.strip().lower()
        if not name:
            continue
        value = "" if header.value is None else str(header.value)
        grouped[name].append(value)
    return {name: ", ".join(values) for name, values in grouped.items()}


def _flatten_query(raw_query: list[HarNameValue], url: str) -> dict[str, Any]:
    if raw_query:
        grouped: dict[str, list[str]] = defaultdict(list)
        for item in raw_query:
            name = item.name
            if not name:
                continue
            grouped[name].append("" if item.value is None else str(item.value))
        return {
            key: values[0] if len(values) == 1 else values
            for key, values in grouped.items()
        }

    parsed = parse_qs(urlsplit(url).query, keep_blank_values=True)
    return {key: values[0] if len(values) == 1 else values for key, values in parsed.items()}


def _dedupe_cookies(cookies: list[CookieRecord]) -> list[CookieRecord]:
    seen: set[tuple[str, str | None, str, str | None, str | None]] = set()
    output: list[CookieRecord] = []
    for cookie in cookies:
        key = (cookie.name, cookie.value, cookie.source, cookie.domain, cookie.path)
        if key in seen:
            continue
        seen.add(key)
        output.append(cookie)
    return output


def _normalize_request(entry: HarEntry, entry_id: str) -> tuple[RequestData, list[Gap]]:
    gaps: list[Gap] = []
    request = entry.request
    url_parts = urlsplit(request.url)
    headers = _flatten_header_values(request.headers)
    query = _flatten_query(request.queryString, request.url)
    cookies: list[CookieRecord] = []

    object_cookies, cookie_gaps = parse_cookie_objects(
        [item.model_dump() for item in request.cookies],
        source="request.cookies",
    )
    cookies.extend(object_cookies)
    gaps.extend(cookie_gaps)

    header_cookie = headers.get("cookie")
    if header_cookie:
        header_cookies, header_gaps = parse_cookie_header(header_cookie, source="request.headers.cookie")
        cookies.extend(header_cookies)
        gaps.extend(header_gaps)

    body, body_gaps = parse_body_data(
        request.postData.model_dump() if request.postData is not None else None
    )
    gaps.extend(body_gaps)

    normalized = RequestData(
        method=request.method.upper(),
        url=request.url,
        scheme=url_parts.scheme,
        host=url_parts.hostname or "",
        path=url_parts.path or "/",
        query=query,
        headers=headers,
        cookies=_dedupe_cookies(cookies),
        body=body,
    )
    return normalized, gaps


def _normalize_response(entry: HarEntry, entry_id: str) -> tuple[ResponseData, list[Gap]]:
    gaps: list[Gap] = []
    response = entry.response
    headers = _flatten_header_values(response.headers)
    cookies: list[CookieRecord] = []

    object_cookies, cookie_gaps = parse_cookie_objects(
        [item.model_dump() for item in response.cookies],
        source="response.cookies",
    )
    cookies.extend(object_cookies)
    gaps.extend(cookie_gaps)

    for header in response.headers:
        if header.name.strip().lower() != "set-cookie":
            continue
        parsed_cookies, parsed_gaps = parse_set_cookie_header(
            "" if header.value is None else str(header.value),
            source="response.headers.set-cookie",
        )
        cookies.extend(parsed_cookies)
        gaps.extend(parsed_gaps)

    body, body_gaps = parse_body_data(
        response.content.model_dump() if response.content is not None else None
    )
    gaps.extend(body_gaps)

    normalized = ResponseData(
        status=response.status,
        headers=headers,
        cookies=_dedupe_cookies(cookies),
        body=body,
    )
    return normalized, gaps


def normalize_document(document: HarDocument) -> tuple[NormalizedHar, list[Gap]]:
    entries: list[NormalizedEntry] = []
    gaps: list[Gap] = []

    for index, entry in enumerate(document.log.entries):
        entry_id = f"entry-{index:04d}"
        try:
            started_at = _parse_datetime(entry.startedDateTime)
        except Exception:
            started_at = datetime.fromtimestamp(0, tz=timezone.utc)
            gaps.append(_gap("incomplete_timeline", f"{entry_id} has invalid startedDateTime"))

        request, request_gaps = _normalize_request(entry, entry_id)
        response, response_gaps = _normalize_response(entry, entry_id)
        gaps.extend(request_gaps)
        gaps.extend(response_gaps)

        meta = {
            "raw_index": index,
            "time": entry.time,
            "extra_fields": {
                key: value
                for key, value in entry.model_dump().items()
                if key not in {"pageref", "startedDateTime", "time", "request", "response", "timings"}
            },
        }

        entries.append(
            NormalizedEntry(
                entry_id=entry_id,
                page_ref=entry.pageref,
                started_at=started_at,
                request=request,
                response=response,
                timings=entry.timings,
                meta=meta,
            )
        )

    entries.sort(key=lambda item: item.started_at)
    return NormalizedHar(entries=entries), gaps
