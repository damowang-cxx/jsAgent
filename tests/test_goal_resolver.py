from pathlib import Path

from har_agent.intents.goal_resolver import GoalResolver, intent_to_config
from har_agent.parsers.har_loader import load_har_document
from har_agent.parsers.normalizer import normalize_document


FIXTURES = Path(__file__).parent / "fixtures"


def _entries(name: str):
    document = load_har_document(FIXTURES / name)
    normalized, _ = normalize_document(document)
    return normalized.entries


def test_goal_resolver_handles_full_url_and_field_name() -> None:
    intent = GoalResolver().resolve(
        '分析 https://example.com/api/login 接口的 "token" 字段生成逻辑',
        _entries("basic.har"),
    )

    assert intent.analysis_kind == "field_generation_logic"
    assert intent.resolved_request is not None
    assert intent.resolved_request.url == "https://example.com/api/login"
    assert intent.resolved_request.match_count == 1
    assert intent.resolved_field is not None
    assert intent.resolved_field.name == "token"
    assert intent.resolved_field.resolved_scopes == ["request.json"]


def test_goal_resolver_handles_host_and_path_without_full_url() -> None:
    intent = GoalResolver().resolve(
        '分析 example.com 上 /api/login 接口的 "token" 字段来源',
        _entries("basic.har"),
    )

    assert intent.resolved_request is not None
    assert intent.resolved_request.url is None
    assert intent.resolved_request.host_contains == "example.com"
    assert intent.resolved_request.path_contains == "/api/login"
    assert intent.resolved_request.match_count == 1
    assert intent.resolution_confidence in {"medium", "high"}


def test_goal_resolver_does_not_crash_when_url_missing() -> None:
    intent = GoalResolver().resolve('分析 "token" 字段生成逻辑', _entries("basic.har"))

    assert intent.resolved_request is not None
    assert intent.resolved_request.match_count == 0
    assert any(gap.code == "goal_missing_request_target" for gap in intent.resolution_gaps)


def test_goal_resolver_reports_ambiguous_scope() -> None:
    intent = GoalResolver().resolve(
        '分析 https://example.com/api/sendcode 接口的 "desc" 字段生成逻辑',
        _entries("goal_scope_ambiguous.har"),
    )

    assert intent.resolved_field is not None
    assert intent.resolved_field.resolved_scopes == []
    assert set(intent.resolved_field.candidate_scopes) == {"request.json", "response.json"}
    assert any(gap.code == "goal_ambiguous_field_scope" for gap in intent.resolution_gaps)


def test_intent_to_config_uses_candidate_scopes_when_scope_is_ambiguous() -> None:
    intent = GoalResolver().resolve(
        '分析 https://example.com/api/sendcode 接口的 "desc" 字段生成逻辑',
        _entries("goal_scope_ambiguous.har"),
    )
    config = intent_to_config(intent)

    assert len(config.target_fields) == 2
    assert {field.scope for field in config.target_fields} == {"request.json", "response.json"}
