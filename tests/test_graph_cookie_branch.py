from pathlib import Path

from har_agent.config import AppConfig
from har_agent.graph import run_analysis_graph
from har_agent.graph.state import build_initial_state


FIXTURES = Path(__file__).parent / "fixtures"


def test_cookie_branch_runs_and_produces_cookie_lineage() -> None:
    state = build_initial_state(
        FIXTURES / "basic.har",
        AppConfig(),
        goal='Analyze https://example.com/api/login Cookie "sid" set source',
    )

    final_state = run_analysis_graph(state)
    result = final_state["final_result"]

    assert result.analysis_intent.analysis_kind == "cookie_set_source"
    assert result.cookie_lineage
    assert result.cookie_lineage[0].cookie_name == "sid"
    assert result.cookie_lineage[0].confidence in {"high", "medium", "low", "unresolved"}
    assert result.matched_requests
