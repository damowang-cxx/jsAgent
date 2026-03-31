from __future__ import annotations

from har_agent.models.findings import Claim, EvidenceItem, Gap


def build_claim(
    *,
    claim_id: str,
    title: str,
    claim: str,
    confidence: str,
    kind: str,
    evidence: list[EvidenceItem] | None = None,
    gaps: list[Gap] | None = None,
    alternatives: list[str] | None = None,
    related_entries: list[str] | None = None,
) -> Claim:
    return Claim(
        claim_id=claim_id,
        title=title,
        claim=claim,
        confidence=confidence,
        evidence=evidence or [],
        gaps=gaps or [],
        alternatives=alternatives or [],
        related_entries=related_entries or [],
        kind=kind,
    )


def claims_from_cookie_results(cookie_results: list, field_results: list) -> list[Claim]:
    claims: list[Claim] = []
    for index, result in enumerate(cookie_results):
        evidence = [
            EvidenceItem(reference=item.source_ref, detail=item.rationale, kind="direct_evidence")
            for item in result.set_candidates
        ]
        claims.append(
            build_claim(
                claim_id=f"cookie-{index}",
                title=f"Cookie {result.cookie_name} lineage",
                claim=f"Cookie {result.cookie_name} was first observed as {result.first_seen}.",
                confidence=result.confidence,
                kind="direct_evidence" if result.set_candidates else "unresolved",
                evidence=evidence,
                gaps=result.gaps,
                alternatives=result.alternatives,
                related_entries=[event.entry_id for event in result.send_events],
            )
        )
    for index, result in enumerate(field_results):
        evidence = [
            EvidenceItem(reference=item.source_ref, detail=item.rationale, kind="inferred_candidate")
            for item in result.possible_sources
        ]
        claims.append(
            build_claim(
                claim_id=f"field-{index}",
                title=f"Field {result.name} analysis",
                claim=f"Field {result.name} was first observed at {result.first_seen or 'not observed'}.",
                confidence=result.confidence,
                kind="inferred_candidate" if result.possible_sources else "unresolved",
                evidence=evidence,
                gaps=result.gaps,
                related_entries=[occurrence.entry_id for occurrence in result.occurrences],
            )
        )
    return claims
