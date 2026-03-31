from pathlib import Path

from har_agent.config import AppConfig
from har_agent.graph import run_analysis_graph
from har_agent.graph.state import build_initial_state


FIXTURES = Path(__file__).parent / "fixtures"


def test_fallback_path_runs_auto_discovery_when_goal_is_incomplete() -> None:
    state = build_initial_state(
        FIXTURES / "basic.har",
        AppConfig(),
        goal="Analyze https://example.com/api/login cookie generation logic",
    )

    final_state = run_analysis_graph(state)
    result = final_state["final_result"]

    assert result.analysis_intent.analysis_kind == "cookie_generation_logic"
    assert any(gap.code == "goal_missing_cookie_name" for gap in result.analysis_intent.resolution_gaps)
    assert result.field_analysis or result.cookie_lineage
    assert any(item.discovered_candidate for item in result.field_analysis)
