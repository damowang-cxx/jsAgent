from __future__ import annotations

from functools import partial

from langgraph.graph import END, START, StateGraph

from har_agent.graph.routes import (
    route_after_analysis,
    route_after_cookie_target,
    route_after_field_target,
    route_after_request_match,
    route_by_intent,
)
from har_agent.hooks.registry import HookRegistry
from har_agent.models.agent_state import AgentState
from har_agent.nodes.auto_discovery import auto_discovery_node
from har_agent.nodes.finalize import finalize_node
from har_agent.nodes.health_check import health_check_node
from har_agent.nodes.load_har import load_har_node
from har_agent.nodes.match_requests import match_requests_node
from har_agent.nodes.normalize_har import normalize_har_node
from har_agent.nodes.parse_goal import parse_goal_node
from har_agent.nodes.resolve_cookie_target import resolve_cookie_target_node
from har_agent.nodes.resolve_field_target import resolve_field_target_node
from har_agent.nodes.resolve_request_target import resolve_request_target_node
from har_agent.nodes.review_cookie_evidence import review_cookie_evidence_node
from har_agent.nodes.review_field_evidence import review_field_evidence_node
from har_agent.nodes.run_cookie_analysis import run_cookie_analysis_node
from har_agent.nodes.run_field_analysis import run_field_analysis_node


def build_analysis_graph(*, hook_registry: HookRegistry | None = None):
    hook_registry = hook_registry or HookRegistry()
    graph = StateGraph(AgentState)
    graph.add_node("load_har", load_har_node)
    graph.add_node("normalize_har", normalize_har_node)
    graph.add_node("health_check", health_check_node)
    graph.add_node("parse_goal", partial(parse_goal_node, hook_registry=hook_registry))
    graph.add_node("resolve_cookie_target", resolve_cookie_target_node)
    graph.add_node("resolve_field_target", resolve_field_target_node)
    graph.add_node("resolve_request_target", resolve_request_target_node)
    graph.add_node("match_requests", match_requests_node)
    graph.add_node("run_cookie_analysis", partial(run_cookie_analysis_node, hook_registry=hook_registry))
    graph.add_node("run_field_analysis", partial(run_field_analysis_node, hook_registry=hook_registry))
    graph.add_node("review_cookie_evidence", review_cookie_evidence_node)
    graph.add_node("review_field_evidence", review_field_evidence_node)
    graph.add_node("auto_discovery", auto_discovery_node)
    graph.add_node("finalize", partial(finalize_node, hook_registry=hook_registry))

    graph.add_edge(START, "load_har")
    graph.add_edge("load_har", "normalize_har")
    graph.add_edge("normalize_har", "health_check")
    graph.add_edge("health_check", "parse_goal")
    graph.add_conditional_edges(
        "parse_goal",
        route_by_intent,
        {
            "cookie_path": "resolve_cookie_target",
            "field_path": "resolve_field_target",
            "fallback_path": "auto_discovery",
        },
    )
    graph.add_conditional_edges(
        "resolve_cookie_target",
        route_after_cookie_target,
        {
            "resolve_request_target": "resolve_request_target",
            "fallback_path": "auto_discovery",
        },
    )
    graph.add_conditional_edges(
        "resolve_field_target",
        route_after_field_target,
        {
            "resolve_request_target": "resolve_request_target",
            "fallback_path": "auto_discovery",
        },
    )
    graph.add_edge("resolve_request_target", "match_requests")
    graph.add_conditional_edges(
        "match_requests",
        route_after_request_match,
        {
            "run_cookie_analysis": "run_cookie_analysis",
            "run_field_analysis": "run_field_analysis",
            "fallback_path": "auto_discovery",
            "auto_discovery": "auto_discovery",
            "finalize": "finalize",
        },
    )
    graph.add_conditional_edges(
        "run_cookie_analysis",
        route_after_analysis,
        {
            "review_cookie_evidence": "review_cookie_evidence",
            "review_field_evidence": "review_field_evidence",
        },
    )
    graph.add_conditional_edges(
        "run_field_analysis",
        route_after_analysis,
        {
            "review_cookie_evidence": "review_cookie_evidence",
            "review_field_evidence": "review_field_evidence",
        },
    )
    graph.add_edge("review_cookie_evidence", "finalize")
    graph.add_edge("review_field_evidence", "finalize")
    graph.add_edge("auto_discovery", "finalize")
    graph.add_edge("finalize", END)
    return graph.compile()


def run_analysis_graph(state: AgentState, *, hook_registry: HookRegistry | None = None) -> AgentState:
    graph = build_analysis_graph(hook_registry=hook_registry)
    return graph.invoke(state)
