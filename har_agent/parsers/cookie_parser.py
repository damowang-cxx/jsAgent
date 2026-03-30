from __future__ import annotations

from typing import Iterable, Mapping

from har_agent.models.findings import Gap
from har_agent.models.normalized import CookieRecord


def _gap(message: str) -> Gap:
    return Gap(code="parse_error_cookie", message=message, severity="medium")


def _split_cookie_pair(pair: str) -> tuple[str, str | None]:
    if "=" not in pair:
        return pair.strip(), None
    name, value = pair.split("=", 1)
    return name.strip(), value.strip()


def parse_cookie_header(header_value: str, *, source: str) -> tuple[list[CookieRecord], list[Gap]]:
    cookies: list[CookieRecord] = []
    gaps: list[Gap] = []
    if not header_value:
        return cookies, gaps

    for raw_part in header_value.split(";"):
        part = raw_part.strip()
        if not part:
            continue
        name, value = _split_cookie_pair(part)
        if not name:
            gaps.append(_gap("Cookie header contained an empty name"))
            continue
        cookies.append(CookieRecord(name=name, value=value, source=source, raw=part))
    return cookies, gaps


def parse_set_cookie_header(header_value: str, *, source: str) -> tuple[list[CookieRecord], list[Gap]]:
    cookies: list[CookieRecord] = []
    gaps: list[Gap] = []
    if not header_value:
        return cookies, gaps

    parts = [item.strip() for item in header_value.split(";") if item.strip()]
    if not parts:
        return cookies, gaps

    name, value = _split_cookie_pair(parts[0])
    if not name:
        gaps.append(_gap("Set-Cookie header contained an empty name"))
        return cookies, gaps

    attributes: dict[str, str | bool | None] = {}
    for attribute_raw in parts[1:]:
        attribute_name, attribute_value = _split_cookie_pair(attribute_raw)
        key = attribute_name.lower()
        if key in {"secure", "httponly"} and attribute_value is None:
            attributes[key] = True
            continue
        attributes[key] = attribute_value

    max_age = attributes.get("max-age")
    parsed_max_age = None
    if isinstance(max_age, str):
        try:
            parsed_max_age = int(max_age)
        except ValueError:
            gaps.append(_gap("Set-Cookie max-age was not an integer"))

    cookies.append(
        CookieRecord(
            name=name,
            value=value,
            domain=attributes.get("domain") if isinstance(attributes.get("domain"), str) else None,
            path=attributes.get("path") if isinstance(attributes.get("path"), str) else None,
            expires=attributes.get("expires") if isinstance(attributes.get("expires"), str) else None,
            max_age=parsed_max_age,
            secure=bool(attributes.get("secure")) if "secure" in attributes else None,
            http_only=bool(attributes.get("httponly")) if "httponly" in attributes else None,
            same_site=attributes.get("samesite") if isinstance(attributes.get("samesite"), str) else None,
            source=source,
            raw=header_value,
        )
    )
    return cookies, gaps


def parse_cookie_objects(cookie_items: Iterable[Mapping[str, object]], *, source: str) -> tuple[list[CookieRecord], list[Gap]]:
    cookies: list[CookieRecord] = []
    gaps: list[Gap] = []

    for item in cookie_items:
        name = str(item.get("name", "")).strip()
        if not name:
            gaps.append(_gap("Cookie object missing name"))
            continue
        max_age = item.get("maxAge")
        parsed_max_age = max_age if isinstance(max_age, int) else None
        cookies.append(
            CookieRecord(
                name=name,
                value=str(item.get("value")) if item.get("value") is not None else None,
                domain=str(item.get("domain")) if item.get("domain") is not None else None,
                path=str(item.get("path")) if item.get("path") is not None else None,
                expires=str(item.get("expires")) if item.get("expires") is not None else None,
                max_age=parsed_max_age,
                secure=bool(item.get("secure")) if item.get("secure") is not None else None,
                http_only=bool(item.get("httpOnly")) if item.get("httpOnly") is not None else None,
                same_site=str(item.get("sameSite")) if item.get("sameSite") is not None else None,
                source=source,
                raw=None,
            )
        )
    return cookies, gaps
