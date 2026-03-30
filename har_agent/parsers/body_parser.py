from __future__ import annotations

import base64
import json
from typing import Any, Mapping
from urllib.parse import parse_qs

from har_agent.models.findings import Gap
from har_agent.models.normalized import DecodedVariant, ParsedBody


def _gap(message: str) -> Gap:
    return Gap(code="parse_error_body", message=message, severity="medium")


def _flatten_multimap(values: dict[str, list[str]]) -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key, value_list in values.items():
        if len(value_list) == 1:
            flattened[key] = value_list[0]
        else:
            flattened[key] = value_list
    return flattened


def _decode_base64(text: str) -> tuple[str | None, Gap | None]:
    try:
        decoded = base64.b64decode(text)
    except Exception:
        return None, _gap("Failed to decode base64 body")

    for encoding in ("utf-8", "latin-1"):
        try:
            return decoded.decode(encoding), None
        except UnicodeDecodeError:
            continue
    return decoded.decode("latin-1", errors="replace"), None


def parse_body_data(body_source: Mapping[str, Any] | None, *, default_mime_type: str | None = None) -> tuple[ParsedBody | None, list[Gap]]:
    if not body_source:
        return None, []

    mime_type = body_source.get("mimeType") or default_mime_type
    raw_text = body_source.get("text")
    encoding = body_source.get("encoding")
    params = body_source.get("params") or []
    gaps: list[Gap] = []
    decoded_variants: list[DecodedVariant] = []

    if encoding == "base64" and raw_text:
        decoded_text, gap = _decode_base64(raw_text)
        if gap is not None:
            gaps.append(gap)
        if decoded_text is not None:
            raw_text = decoded_text
            decoded_variants.append(DecodedVariant(encoding="base64", value=decoded_text))

    form_data: dict[str, Any] | None = None
    if params:
        pairs: dict[str, list[Any]] = {}
        for param in params:
            if not isinstance(param, Mapping):
                continue
            name = str(param.get("name", ""))
            value = param.get("value")
            if not name:
                continue
            pairs.setdefault(name, []).append(value)
        form_data = {
            key: values[0] if len(values) == 1 else values
            for key, values in pairs.items()
        }

    json_data: Any = None
    if raw_text:
        if mime_type and "json" in mime_type:
            try:
                json_data = json.loads(raw_text)
            except json.JSONDecodeError:
                gaps.append(_gap("Failed to parse JSON body"))
        elif mime_type and "application/x-www-form-urlencoded" in mime_type:
            form_data = _flatten_multimap(parse_qs(raw_text, keep_blank_values=True))
        elif raw_text.strip().startswith(("{", "[")):
            try:
                json_data = json.loads(raw_text)
                decoded_variants.append(DecodedVariant(encoding="json_string", value=raw_text))
            except json.JSONDecodeError:
                gaps.append(_gap("Body looked like JSON but could not be parsed"))

    if form_data is None and raw_text and mime_type and "application/x-www-form-urlencoded" in mime_type:
        form_data = _flatten_multimap(parse_qs(raw_text, keep_blank_values=True))

    parsed = ParsedBody(
        mime_type=mime_type,
        raw_text=raw_text,
        json_data=json_data,
        form_data=form_data,
        decoded_variants=decoded_variants,
    )
    return parsed, gaps
