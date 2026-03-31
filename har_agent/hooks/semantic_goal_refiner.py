from __future__ import annotations

from har_agent.models.agent_state import AgentState


class NoOpSemanticGoalRefiner:
    name = "semantic_goal_refiner"

    def run(self, payload: str | None, state: AgentState) -> str | None:
        return payload
