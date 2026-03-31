from __future__ import annotations

from pathlib import Path

from har_agent.config import AppConfig
from har_agent.graph.builder import run_analysis_graph
from har_agent.graph.state import build_initial_state
from har_agent.models.report import AnalysisResult


def analyze_har(input_path: str | Path, config: AppConfig, *, goal: str | None = None) -> AnalysisResult:
    state = build_initial_state(input_path, config, goal=goal)
    final_state = run_analysis_graph(state)
    return final_state["final_result"]
