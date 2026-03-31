from __future__ import annotations

from typing import Any

from har_agent.models.agent_state import AgentState


class NoOpGenerationLogicReasoner:
    name = "generation_logic_reasoner"

    def run(self, payload: Any, state: AgentState) -> Any:
        return payload
