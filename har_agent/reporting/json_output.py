from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from har_agent.models.report import AnalysisResult

try:  # pragma: no cover - optional dependency
    import orjson
except ImportError:  # pragma: no cover
    orjson = None


def write_json_output(result: AnalysisResult, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = result.model_dump(mode="json")
    if orjson is not None:
        output_path.write_bytes(orjson.dumps(payload, option=orjson.OPT_INDENT_2))
        return
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
