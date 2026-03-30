from __future__ import annotations

from har_agent.models.findings import Gap


CONFIDENCE_ORDER = {
    "high": 3,
    "medium": 2,
    "low": 1,
    "unresolved": 0,
}


def downgrade_for_gaps(confidence: str, gaps: list[Gap]) -> str:
    if not gaps:
        return confidence
    current = CONFIDENCE_ORDER.get(confidence, 0)
    downgraded = max(current - 1, 0)
    for label, value in CONFIDENCE_ORDER.items():
        if value == downgraded:
            return label
    return "unresolved"
