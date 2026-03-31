from __future__ import annotations

from har_agent.analysis.claims import claims_from_cookie_results
from har_agent.graph.state import extend_gaps, extend_notes
from har_agent.models.agent_state import AgentState


def review_cookie_evidence_node(state: AgentState) -> dict:
    cookie_lineage = state.get("cookie_lineage", [])
    gaps = [gap for item in cookie_lineage for gap in item.gaps]
    notes = ["Reviewed cookie evidence and converted it into stable claims."]
    if any(item.confidence in {"low", "unresolved"} for item in cookie_lineage):
        notes.append("Cookie evidence remains partially unresolved; recommendations may suggest collecting a wider or less-sanitized HAR.")
    return {
        "claims": claims_from_cookie_results(cookie_lineage, state.get("field_analysis", [])),
        "gaps": extend_gaps(state, gaps),
        "notes": extend_notes(state, *notes),
    }
