from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DecodedVariant(BaseModel):
    model_config = ConfigDict(extra="forbid")

    encoding: str
    value: str


class CookieRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    value: str | None = None
    domain: str | None = None
    path: str | None = None
    expires: str | None = None
    max_age: int | None = None
    secure: bool | None = None
    http_only: bool | None = None
    same_site: str | None = None
    source: str
    raw: str | None = None


class ParsedBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mime_type: str | None = None
    raw_text: str | None = None
    json_data: Any = None
    form_data: dict[str, Any] | None = None
    decoded_variants: list[DecodedVariant] = Field(default_factory=list)


class RequestData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method: str
    url: str
    scheme: str
    host: str
    path: str
    query: dict[str, Any] = Field(default_factory=dict)
    headers: dict[str, str] = Field(default_factory=dict)
    cookies: list[CookieRecord] = Field(default_factory=list)
    body: ParsedBody | None = None


class ResponseData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: int
    headers: dict[str, str] = Field(default_factory=dict)
    cookies: list[CookieRecord] = Field(default_factory=list)
    body: ParsedBody | None = None


class NormalizedEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entry_id: str
    page_ref: str | None = None
    started_at: datetime
    request: RequestData
    response: ResponseData
    timings: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)


class FieldRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    scope: str
    selector: str


class NormalizedHar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entries: list[NormalizedEntry] = Field(default_factory=list)
