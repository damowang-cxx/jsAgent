from __future__ import annotations

import base64
import json
import re
from urllib.parse import unquote

from har_agent.models.findings import ValueEncoding


JWT_RE = re.compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")
HEX_RE = re.compile(r"^[0-9a-fA-F]+$")


def detect_value_encodings(value: str | None) -> list[ValueEncoding]:
    if value is None:
        return []

    results: list[ValueEncoding] = []
    if "%" in value:
        decoded = unquote(value)
        if decoded != value:
            results.append(
                ValueEncoding(
                    type="urlencoded",
                    confidence="medium",
                    rationale="URL decoding changed the original value.",
                    decoded_value=decoded,
                )
            )

    if _looks_like_base64(value):
        decoded = _safe_b64decode(value)
        if decoded is not None:
            results.append(
                ValueEncoding(
                    type="base64",
                    confidence="medium",
                    rationale="Value matches base64 shape and decodes to printable text.",
                    decoded_value=decoded,
                )
            )

    if _looks_like_base64url(value):
        decoded = _safe_b64decode(value, urlsafe=True)
        if decoded is not None:
            results.append(
                ValueEncoding(
                    type="base64url",
                    confidence="medium",
                    rationale="Value matches base64url shape and decodes to printable text.",
                    decoded_value=decoded,
                )
            )

    if len(value) % 2 == 0 and len(value) >= 8 and HEX_RE.match(value):
        try:
            decoded = bytes.fromhex(value).decode("utf-8")
        except Exception:
            decoded = None
        results.append(
            ValueEncoding(
                type="hex",
                confidence="medium",
                rationale="Value is an even-length hexadecimal string.",
                decoded_value=decoded,
            )
        )

    if value.strip().startswith(("{", "[", "\"")):
        try:
            parsed = json.loads(value)
        except Exception:
            parsed = None
        if parsed is not None:
            results.append(
                ValueEncoding(
                    type="json_string",
                    confidence="medium",
                    rationale="Value is itself a valid JSON string/document.",
                    decoded_value=json.dumps(parsed, ensure_ascii=False),
                )
            )

    if JWT_RE.match(value):
        results.append(
            ValueEncoding(
                type="jwt_shape",
                confidence="medium",
                rationale="Value matches the common three-part JWT structure.",
                decoded_value=None,
            )
        )

    return results


def _looks_like_base64(value: str) -> bool:
    if len(value) < 8 or len(value) % 4 != 0:
        return False
    return re.fullmatch(r"[A-Za-z0-9+/=]+", value) is not None


def _looks_like_base64url(value: str) -> bool:
    if len(value) < 8:
        return False
    return re.fullmatch(r"[A-Za-z0-9_-]+", value) is not None


def _safe_b64decode(value: str, *, urlsafe: bool = False) -> str | None:
    padded = value + "=" * ((4 - len(value) % 4) % 4)
    try:
        decoded = base64.urlsafe_b64decode(padded) if urlsafe else base64.b64decode(padded)
        text = decoded.decode("utf-8")
    except Exception:
        return None
    if text.isprintable():
        return text
    return None
