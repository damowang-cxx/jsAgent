from __future__ import annotations

from har_agent.analysis.claims import claims_from_cookie_results
from har_agent.graph.state import extend_gaps, extend_notes
from har_agent.models.agent_state import AgentState


def review_field_evidence_node(state: AgentState) -> dict:
    field_analysis = state.get("field_analysis", [])
    gaps = [gap for item in field_analysis for gap in item.gaps]
    notes = ["Reviewed field evidence and converted it into stable claims."]
    if any(item.confidence in {"low", "unresolved"} for item in field_analysis):
        notes.append("Field evidence remains partially unresolved; results stay explicitly tentative.")
    return {
        "claims": claims_from_cookie_results(state.get("cookie_lineage", []), field_analysis),
        "gaps": extend_gaps(state, gaps),
        "notes": extend_notes(state, *notes),
    }
