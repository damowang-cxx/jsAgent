from har_agent.graph.routes import (
    route_after_analysis,
    route_after_cookie_target,
    route_after_field_target,
    route_after_request_match,
    route_by_intent,
)


def test_route_by_intent_cookie_path() -> None:
    assert route_by_intent({"analysis_kind": "cookie_set_source"}) == "cookie_path"


def test_route_by_intent_field_path() -> None:
    assert route_by_intent({"analysis_kind": "field_generation_logic"}) == "field_path"


def test_route_by_intent_unknown_fallback() -> None:
    assert route_by_intent({"analysis_kind": "auto_discovery"}) == "fallback_path"


def test_route_after_cookie_target() -> None:
    assert route_after_cookie_target({"target_cookie_name": "sid"}) == "resolve_request_target"
    assert route_after_cookie_target({"target_cookie_name": None}) == "fallback_path"


def test_route_after_field_target() -> None:
    assert route_after_field_target({"target_field_name": "token"}) == "resolve_request_target"
    assert route_after_field_target({"target_field_name": None}) == "fallback_path"


def test_route_after_request_match() -> None:
    assert route_after_request_match({"matched_requests": [{"entry_id": "1"}], "analysis_kind": "cookie_set_source"}) == "run_cookie_analysis"
    assert route_after_request_match({"matched_requests": [{"entry_id": "1"}], "analysis_kind": "field_origin"}) == "run_field_analysis"
    assert route_after_request_match({"matched_requests": [], "input_mode": "goal_prompt"}) == "fallback_path"
    assert route_after_request_match({"matched_requests": [], "input_mode": "auto_discovery"}) == "auto_discovery"


def test_route_after_analysis() -> None:
    assert route_after_analysis({"analysis_kind": "cookie_generation_logic"}) == "review_cookie_evidence"
    assert route_after_analysis({"analysis_kind": "field_origin"}) == "review_field_evidence"
