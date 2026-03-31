from pathlib import Path

from har_agent.config import AppConfig
from har_agent.graph import run_analysis_graph
from har_agent.graph.state import build_initial_state


FIXTURES = Path(__file__).parent / "fixtures"


def test_field_branch_runs_and_produces_field_analysis() -> None:
    state = build_initial_state(
        FIXTURES / "basic.har",
        AppConfig(),
        goal='Analyze https://example.com/api/login endpoint field "token" generation logic',
    )

    final_state = run_analysis_graph(state)
    result = final_state["final_result"]

    assert result.analysis_intent.analysis_kind == "field_generation_logic"
    assert result.field_analysis
    assert result.field_analysis[0].name == "token"
    assert result.matched_requests


def test_field_branch_keeps_ambiguous_candidate_scopes() -> None:
    state = build_initial_state(
        FIXTURES / "goal_scope_ambiguous.har",
        AppConfig(),
        goal='Analyze https://example.com/api/sendcode endpoint field "desc" generation logic',
    )

    final_state = run_analysis_graph(state)
    result = final_state["final_result"]

    assert len(result.targets["target_fields"]) == 2
    assert {item["scope"] for item in result.targets["target_fields"]} == {"request.json", "response.json"}
    assert any(gap.code == "goal_ambiguous_field_scope" for gap in result.analysis_intent.resolution_gaps)
    assert len(result.field_analysis) == 2
