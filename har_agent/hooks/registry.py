from __future__ import annotations

from typing import Any

from har_agent.hooks.analysis_explainer import NoOpAnalysisExplainer
from har_agent.hooks.base import BaseHook
from har_agent.hooks.generation_logic_reasoner import NoOpGenerationLogicReasoner
from har_agent.hooks.semantic_goal_refiner import NoOpSemanticGoalRefiner
from har_agent.models.agent_state import AgentState


class HookRegistry:
    def __init__(
        self,
        *,
        semantic_goal_refiner: BaseHook | None = None,
        analysis_explainer: BaseHook | None = None,
        generation_logic_reasoner: BaseHook | None = None,
    ) -> None:
        self.semantic_goal_refiner = semantic_goal_refiner or NoOpSemanticGoalRefiner()
        self.analysis_explainer = analysis_explainer or NoOpAnalysisExplainer()
        self.generation_logic_reasoner = generation_logic_reasoner or NoOpGenerationLogicReasoner()

    def run_semantic_goal_refiner(self, payload: Any, state: AgentState) -> Any:
        return self.semantic_goal_refiner.run(payload, state)

    def run_analysis_explainer(self, payload: Any, state: AgentState) -> Any:
        return self.analysis_explainer.run(payload, state)

    def run_generation_logic_reasoner(self, payload: Any, state: AgentState) -> Any:
        return self.generation_logic_reasoner.run(payload, state)
