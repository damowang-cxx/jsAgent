from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field


class TargetRequestRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    url_contains: str | None = None
    url_regex: str | None = None
    methods: list[str] = Field(default_factory=list)
    status_in: list[int] = Field(default_factory=list)
    host_contains: str | None = None
    header_exists: list[str] = Field(default_factory=list)
    cookie_exists: list[str] = Field(default_factory=list)
    body_contains: list[str] = Field(default_factory=list)
    response_contains: list[str] = Field(default_factory=list)


class TargetFieldConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    scope: str
    selector: str


class ReportConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    include_timeline: bool = True
    include_raw_examples: bool = True


class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_requests: list[TargetRequestRule] = Field(default_factory=list)
    target_cookies: list[str] = Field(default_factory=list)
    target_fields: list[TargetFieldConfig] = Field(default_factory=list)
    report: ReportConfig = Field(default_factory=ReportConfig)


class ConfigLoadError(RuntimeError):
    """Raised when the user config cannot be loaded."""


def load_config(path: str | Path | None) -> AppConfig:
    if path is None:
        return AppConfig()

    config_path = Path(path)
    if not config_path.exists():
        raise ConfigLoadError(f"Config file not found: {config_path}")

    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigLoadError(f"Invalid YAML config: {config_path}") from exc

    if not isinstance(raw, dict):
        raise ConfigLoadError("Config root must be a mapping")

    try:
        return AppConfig.model_validate(raw)
    except Exception as exc:  # pragma: no cover - pydantic normalizes details
        raise ConfigLoadError("Config validation failed") from exc


def config_to_targets(config: AppConfig) -> dict[str, Any]:
    return {
        "target_requests": [rule.model_dump() for rule in config.target_requests],
        "target_cookies": list(config.target_cookies),
        "target_fields": [field.model_dump() for field in config.target_fields],
    }
