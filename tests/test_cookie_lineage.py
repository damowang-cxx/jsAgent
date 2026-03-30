from pathlib import Path

from har_agent.lineage.cookie_lineage import analyze_cookie_lineage
from har_agent.parsers.har_loader import load_har_document
from har_agent.parsers.normalizer import normalize_document


FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str):
    document = load_har_document(FIXTURES / name)
    normalized, _ = normalize_document(document)
    return normalized.entries


def test_cookie_lineage_high_confidence_exact_set_cookie_chain() -> None:
    results = analyze_cookie_lineage(_load("basic.har"), ["sid"])
    result = results[0]

    assert result.confidence == "high"
    assert result.first_seen.startswith("response.set-cookie")
    assert result.set_candidates[0].source_ref == "entry-0000"
    assert result.send_events[0].entry_id == "entry-0001"


def test_cookie_lineage_medium_when_name_matches_but_value_differs() -> None:
    results = analyze_cookie_lineage(_load("cookie_medium.har"), ["sid"])
    result = results[0]

    assert result.confidence == "medium"
    assert result.set_candidates
    assert result.set_candidates[0].confidence == "medium"


def test_cookie_lineage_without_prior_source_stays_low_and_records_gaps() -> None:
    results = analyze_cookie_lineage(_load("cookie_no_source.har"), ["sid"])
    result = results[0]

    assert result.confidence in {"low", "unresolved"}
    codes = {gap.code for gap in result.gaps}
    assert "missing_prior_requests_before_har_start" in codes
    assert "cannot_confirm_js_generation_from_har_alone" in codes
    assert result.alternatives
