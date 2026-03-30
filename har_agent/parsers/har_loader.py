from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from har_agent.models.har import HarDocument

try:  # pragma: no cover - optional dependency
    import orjson
except ImportError:  # pragma: no cover - exercised by default environment
    orjson = None


class HarLoaderError(RuntimeError):
    """Raised when a HAR file cannot be loaded or validated."""


def _loads(content: bytes) -> Any:
    if orjson is not None:
        return orjson.loads(content)
    return json.loads(content.decode("utf-8"))


def load_har_document(path: str | Path) -> HarDocument:
    har_path = Path(path)
    if not har_path.exists():
        raise HarLoaderError(f"HAR file not found: {har_path}")

    try:
        raw = _loads(har_path.read_bytes())
    except Exception as exc:
        raise HarLoaderError(f"Failed to parse HAR JSON: {har_path}") from exc

    try:
        return HarDocument.model_validate(raw)
    except Exception as exc:
        raise HarLoaderError(f"Invalid HAR structure: {har_path}") from exc
