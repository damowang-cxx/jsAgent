from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class HarNameValue(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str = ""
    value: Any = None


class HarCookie(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str = ""
    value: str | None = None
    path: str | None = None
    domain: str | None = None
    expires: str | None = None
    httpOnly: bool | None = None
    secure: bool | None = None
    sameSite: str | None = None


class HarPostData(BaseModel):
    model_config = ConfigDict(extra="allow")

    mimeType: str | None = None
    text: str | None = None
    params: list[HarNameValue] = Field(default_factory=list)
    encoding: str | None = None


class HarContent(BaseModel):
    model_config = ConfigDict(extra="allow")

    mimeType: str | None = None
    text: str | None = None
    size: int | None = None
    encoding: str | None = None


class HarRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    method: str
    url: str
    headers: list[HarNameValue] = Field(default_factory=list)
    queryString: list[HarNameValue] = Field(default_factory=list)
    cookies: list[HarCookie] = Field(default_factory=list)
    postData: HarPostData | None = None


class HarResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    status: int = 0
    headers: list[HarNameValue] = Field(default_factory=list)
    cookies: list[HarCookie] = Field(default_factory=list)
    content: HarContent | None = None


class HarEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    pageref: str | None = None
    startedDateTime: str
    time: float | None = None
    request: HarRequest
    response: HarResponse
    timings: dict[str, Any] = Field(default_factory=dict)


class HarPage(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str | None = None
    startedDateTime: str | None = None
    title: str | None = None
    pageTimings: dict[str, Any] = Field(default_factory=dict)


class HarLog(BaseModel):
    model_config = ConfigDict(extra="allow")

    version: str | None = None
    creator: dict[str, Any] = Field(default_factory=dict)
    pages: list[HarPage] = Field(default_factory=list)
    entries: list[HarEntry] = Field(default_factory=list)


class HarDocument(BaseModel):
    model_config = ConfigDict(extra="allow")

    log: HarLog
