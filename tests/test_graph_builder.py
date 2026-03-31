from pathlib import Path

from har_agent.config import AppConfig
from har_agent.graph import build_analysis_graph
from har_agent.graph.state import build_initial_state


FIXTURES = Path(__file__).parent / "fixtures"


def test_graph_builds_and_runs_from_start_to_end() -> None:
    graph = build_analysis_graph()
    state = build_initial_state(FIXTURES / "basic.har", AppConfig())

    final_state = graph.invoke(state)

    assert final_state["final_result"] is not None
    assert final_state["final_result"].summary.entry_count == 4
    assert final_state["final_result"].analysis_intent.input_mode == "auto_discovery"
