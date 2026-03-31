from __future__ import annotations

from typing import Any

from har_agent.models.agent_state import AgentState


class NoOpAnalysisExplainer:
    name = "analysis_explainer"

    def run(self, payload: Any, state: AgentState) -> Any:
        return payload
