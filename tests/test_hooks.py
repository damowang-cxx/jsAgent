from pathlib import Path

from har_agent.config import AppConfig
from har_agent.graph import run_analysis_graph
from har_agent.graph.state import build_initial_state
from har_agent.hooks.registry import HookRegistry


FIXTURES = Path(__file__).parent / "fixtures"


class _RaisingHook:
    name = "raising"

    def run(self, payload, state):
        raise AssertionError("hook should not be called when flags are disabled")


def test_hooks_default_to_noop_and_are_not_called_when_flags_are_false() -> None:
    registry = HookRegistry(
        semantic_goal_refiner=_RaisingHook(),
        analysis_explainer=_RaisingHook(),
        generation_logic_reasoner=_RaisingHook(),
    )
    state = build_initial_state(FIXTURES / "basic.har", AppConfig())

    final_state = run_analysis_graph(state, hook_registry=registry)

    assert final_state["final_result"] is not None
    assert final_state["final_result"].summary.entry_count == 4
