from pathlib import Path

from har_agent.analysis.gaps import assess_har_health
from har_agent.parsers.har_loader import load_har_document
from har_agent.parsers.normalizer import normalize_document


FIXTURES = Path(__file__).parent / "fixtures"


def test_normalize_document_captures_headers_cookies_and_bodies() -> None:
    document = load_har_document(FIXTURES / "basic.har")
    normalized, gaps = normalize_document(document)

    assert len(normalized.entries) == 4
    first = normalized.entries[0]
    assert first.request.headers["host"] == "example.com"
    assert first.response.cookies[0].name == "sid"
    assert first.response.cookies[0].http_only is True

    second = normalized.entries[1]
    assert second.request.cookies[0].name == "sid"
    assert second.request.body is not None
    assert second.request.body.json_data["token"] == "resp-token"

    third = normalized.entries[2]
    assert third.request.body is not None
    assert third.request.body.form_data == {"nonce": "n-1", "trace": "t-1"}

    fourth = normalized.entries[3]
    assert fourth.response.body is not None
    assert fourth.response.body.raw_text == "hello world"
    assert not gaps


def test_assess_har_health_flags_sanitized_and_incomplete_timeline() -> None:
    document = load_har_document(FIXTURES / "sanitized.har")
    normalized, parse_gaps = normalize_document(document)
    health = assess_har_health(document, normalized.entries, parse_gaps)

    assert health.likely_sanitized is True
    assert health.missing_cookie_headers is True
    assert health.missing_set_cookie_headers is True
    assert health.incomplete_timeline is True
    codes = {gap.code for gap in health.gaps}
    assert "likely_sanitized_har" in codes
    assert "incomplete_timeline" in codes


def test_assess_har_health_handles_empty_entries() -> None:
    document = load_har_document(FIXTURES / "empty.har")
    normalized, parse_gaps = normalize_document(document)
    health = assess_har_health(document, normalized.entries, parse_gaps)

    assert health.empty_entries is True
    assert health.entries_count == 0
    assert any(gap.code == "incomplete_timeline" for gap in health.gaps)
