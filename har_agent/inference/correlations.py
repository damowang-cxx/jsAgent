from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable
from urllib.parse import unquote

from har_agent.models.normalized import NormalizedEntry


@dataclass(slots=True)
class ScalarObservation:
    entry_id: str
    timestamp: datetime
    scope: str
    selector: str
    name: str
    value: str

    @property
    def reference(self) -> str:
        return f"{self.entry_id}:{self.scope}:{self.selector}"


@dataclass(slots=True)
class CorrelationMatch:
    relation: str
    observation: ScalarObservation
    confidence: str
    rationale: str


def collect_scalar_observations(entries: Iterable[NormalizedEntry]) -> list[ScalarObservation]:
    observations: list[ScalarObservation] = []
    for entry in entries:
        observations.extend(_collect_from_mapping(entry.entry_id, entry.started_at, "request.header", entry.request.headers))
        observations.extend(_collect_from_mapping(entry.entry_id, entry.started_at, "request.query", entry.request.query))
        observations.extend(_collect_cookies(entry.entry_id, entry.started_at, "request.cookie", entry.request.cookies))
        if entry.request.body and entry.request.body.form_data:
            observations.extend(_collect_from_mapping(entry.entry_id, entry.started_at, "request.form", entry.request.body.form_data))
        if entry.request.body and entry.request.body.json_data is not None:
            observations.extend(_collect_json(entry.entry_id, entry.started_at, "request.json", entry.request.body.json_data))

        observations.extend(_collect_from_mapping(entry.entry_id, entry.started_at, "response.header", entry.response.headers))
        observations.extend(_collect_cookies(entry.entry_id, entry.started_at, "response.cookie", entry.response.cookies))
        if entry.response.body and entry.response.body.json_data is not None:
            observations.extend(_collect_json(entry.entry_id, entry.started_at, "response.json", entry.response.body.json_data))
    observations.sort(key=lambda item: (item.timestamp, item.entry_id, item.scope, item.selector))
    return observations


def find_correlated_observations(target: ScalarObservation, observations: Iterable[ScalarObservation]) -> list[CorrelationMatch]:
    matches: list[CorrelationMatch] = []
    for observation in observations:
        if observation.reference == target.reference and observation.value == target.value:
            continue
        if observation.timestamp > target.timestamp:
            continue

        if observation.value == target.value:
            matches.append(
                CorrelationMatch(
                    relation="exact",
                    observation=observation,
                    confidence="high" if observation.scope.startswith("response.") else "medium",
                    rationale="Observed exact same value earlier in the HAR.",
                )
            )
            continue

        decoded_target = _try_url_decode(target.value)
        decoded_observation = _try_url_decode(observation.value)
        if decoded_target == observation.value or decoded_observation == target.value:
            matches.append(
                CorrelationMatch(
                    relation="url_decoded_equal",
                    observation=observation,
                    confidence="medium",
                    rationale="Values match after URL decoding one side.",
                )
            )
            continue

        b64_target = _try_base64_decode(target.value)
        b64_observation = _try_base64_decode(observation.value)
        if b64_target == observation.value or b64_observation == target.value:
            matches.append(
                CorrelationMatch(
                    relation="base64_decoded_equal",
                    observation=observation,
                    confidence="medium",
                    rationale="Values match after base64 decoding one side.",
                )
            )
            continue

        if observation.value and observation.value != target.value and observation.value in target.value:
            matches.append(
                CorrelationMatch(
                    relation="contains",
                    observation=observation,
                    confidence="low",
                    rationale="Target value contains an earlier observed value as a substring.",
                )
            )
            continue

        if target.value.startswith(observation.value) or target.value.endswith(observation.value):
            matches.append(
                CorrelationMatch(
                    relation="prefix_suffix",
                    observation=observation,
                    confidence="low",
                    rationale="Target value shares a prefix or suffix with an earlier observed value.",
                )
            )
    return matches[:20]


def _collect_from_mapping(entry_id: str, timestamp: datetime, scope: str, mapping: dict[str, Any]) -> list[ScalarObservation]:
    observations: list[ScalarObservation] = []
    for key, value in mapping.items():
        if isinstance(value, list):
            for item in value:
                observations.append(_build_observation(entry_id, timestamp, scope, key, item))
            continue
        observations.append(_build_observation(entry_id, timestamp, scope, key, value))
    return observations


def _collect_cookies(entry_id: str, timestamp: datetime, scope: str, cookies: list[Any]) -> list[ScalarObservation]:
    observations: list[ScalarObservation] = []
    for cookie in cookies:
        observations.append(_build_observation(entry_id, timestamp, scope, cookie.name, cookie.value))
    return observations


def _collect_json(entry_id: str, timestamp: datetime, scope: str, value: Any, path: str = "$") -> list[ScalarObservation]:
    if isinstance(value, dict):
        observations: list[ScalarObservation] = []
        for key, child in value.items():
            observations.extend(_collect_json(entry_id, timestamp, scope, child, f"{path}.{key}"))
        return observations
    if isinstance(value, list):
        observations: list[ScalarObservation] = []
        for index, child in enumerate(value):
            observations.extend(_collect_json(entry_id, timestamp, scope, child, f"{path}[{index}]"))
        return observations
    return [_build_observation(entry_id, timestamp, scope, path.split(".")[-1], value, selector=path)]


def _build_observation(
    entry_id: str,
    timestamp: datetime,
    scope: str,
    name: str,
    value: Any,
    *,
    selector: str | None = None,
) -> ScalarObservation:
    return ScalarObservation(
        entry_id=entry_id,
        timestamp=timestamp,
        scope=scope,
        selector=selector or name,
        name=name,
        value="" if value is None else str(value),
    )


def _try_url_decode(value: str) -> str | None:
    decoded = unquote(value)
    return decoded if decoded != value else None


def _try_base64_decode(value: str) -> str | None:
    padded = value + "=" * ((4 - len(value) % 4) % 4)
    try:
        decoded = base64.b64decode(padded).decode("utf-8")
    except Exception:
        return None
    return decoded if decoded.isprintable() else None
