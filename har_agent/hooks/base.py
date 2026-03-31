from __future__ import annotations

from typing import Any, Protocol

from har_agent.models.agent_state import AgentState


class BaseHook(Protocol):
    name: str

    def run(self, payload: Any, state: AgentState) -> Any:
        ...
