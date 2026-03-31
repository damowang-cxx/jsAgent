from pathlib import Path

from har_agent.config import AppConfig
from har_agent.graph.state import build_initial_state
from har_agent.nodes.health_check import health_check_node
from har_agent.nodes.load_har import load_har_node
from har_agent.nodes.normalize_har import normalize_har_node
from har_agent.nodes.parse_goal import parse_goal_node


FIXTURES = Path(__file__).parent / "fixtures"


def _state_for_goal(goal: str):
    state = build_initial_state(FIXTURES / "basic.har", AppConfig(), goal=goal)
    state.update(load_har_node(state))
    state.update(normalize_har_node(state))
    state.update(health_check_node(state))
    return parse_goal_node(state)


def test_parse_goal_identifies_cookie_task() -> None:
    parsed = _state_for_goal('Analyze https://example.com/api/login Cookie "sid" set source')

    assert parsed["analysis_intent"].analysis_kind == "cookie_set_source"
    assert parsed["target_cookie_name"] == "sid"
    assert parsed["target_url"] == "https://example.com/api/login"


def test_parse_goal_identifies_field_task() -> None:
    parsed = _state_for_goal('Analyze https://example.com/api/login endpoint field "token" generation logic')

    assert parsed["analysis_intent"].analysis_kind == "field_generation_logic"
    assert parsed["target_field_name"] == "token"
    assert parsed["target_field_scope"] == "request.json"


def test_parse_goal_records_missing_request_target_gap() -> None:
    parsed = _state_for_goal('Analyze field "token" generation logic')

    assert any(gap.code == "goal_missing_request_target" for gap in parsed["analysis_intent"].resolution_gaps)


def test_parse_goal_records_missing_field_name_gap() -> None:
    parsed = _state_for_goal("Analyze https://example.com/api/login field generation logic")

    assert any(gap.code == "goal_missing_field_name" for gap in parsed["analysis_intent"].resolution_gaps)


def test_parse_goal_records_missing_cookie_name_gap() -> None:
    parsed = _state_for_goal("Analyze https://example.com/api/login cookie generation logic")

    assert any(gap.code == "goal_missing_cookie_name" for gap in parsed["analysis_intent"].resolution_gaps)
