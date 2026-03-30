from pathlib import Path

from har_agent.config import TargetRequestRule
from har_agent.models.normalized import FieldRef
from har_agent.parsers.har_loader import load_har_document
from har_agent.parsers.normalizer import normalize_document
from har_agent.selectors.field_selector import FieldSelector
from har_agent.selectors.request_selector import RequestSelector, SelectionHints


FIXTURES = Path(__file__).parent / "fixtures"


def _entries():
    document = load_har_document(FIXTURES / "basic.har")
    normalized, _ = normalize_document(document)
    return normalized.entries


def test_request_selector_filters_and_scores_multiple_conditions() -> None:
    entries = _entries()
    rule = TargetRequestRule(
        name="login_api",
        url_regex=r"/api/login",
        methods=["POST"],
        host_contains="example.com",
        header_exists=["content-type"],
        cookie_exists=["sid"],
        body_contains=["alice"],
        response_contains=["ok"],
    )
    selector = RequestSelector(rule)
    matched = selector.select(
        entries,
        hints=SelectionHints(
            target_cookies={"sid"},
            target_fields=[FieldRef(name="token", scope="request.json", selector="$.token")],
            key_reference_time=entries[1].started_at,
        ),
    )

    assert len(matched) == 1
    assert matched[0].entry_id == entries[1].entry_id
    assert matched[0].score > 90
    assert "hint_cookie:sid" in matched[0].reasons
    assert "hint_field:token" in matched[0].reasons


def test_field_selector_supports_request_and_response_scopes() -> None:
    entries = _entries()
    second = entries[1]
    first = entries[0]
    third = entries[2]

    assert FieldSelector(FieldRef(name="cookie_sid", scope="request.cookie", selector="sid")).extract(second)[0] == ["abc123"]
    assert FieldSelector(FieldRef(name="trace", scope="request.query", selector="trace")).extract(second)[0] == ["1"]
    assert FieldSelector(FieldRef(name="req_token", scope="request.json", selector="$.token")).extract(second)[0] == ["resp-token"]
    assert FieldSelector(FieldRef(name="resp_token", scope="response.json", selector="$.token")).extract(first)[0] == ["resp-token"]
    assert FieldSelector(FieldRef(name="nonce", scope="request.form", selector="nonce")).extract(third)[0] == ["n-1"]


def test_field_selector_invalid_jsonpath_returns_gap() -> None:
    entries = _entries()
    values, gaps = FieldSelector(FieldRef(name="bad", scope="request.json", selector="$[" )).extract(entries[1])

    assert values == []
    assert gaps
    assert gaps[0].code == "invalid_field_selector"
