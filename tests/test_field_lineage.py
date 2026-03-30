from pathlib import Path

from har_agent.lineage.field_lineage import analyze_field_lineage
from har_agent.models.normalized import FieldRef
from har_agent.parsers.har_loader import load_har_document
from har_agent.parsers.normalizer import normalize_document


FIXTURES = Path(__file__).parent / "fixtures"


def test_field_lineage_finds_prior_response_json_and_related_cookie() -> None:
    document = load_har_document(FIXTURES / "field_lineage.har")
    normalized, _ = normalize_document(document)
    fields = [
        FieldRef(name="trace_id", scope="request.header", selector="x-trace-id"),
        FieldRef(name="session", scope="request.json", selector="$.payload.session"),
    ]

    results = analyze_field_lineage(normalized.entries, fields)
    trace_result = results[0]
    session_result = results[1]

    assert trace_result.confidence == "high"
    assert trace_result.possible_sources[0].source_type == "response.json"
    assert trace_result.first_seen == "request.header@entry-0001"

    assert session_result.related_cookies == ["sid"]
    assert session_result.possible_sources


def test_field_lineage_marks_unresolved_when_field_missing() -> None:
    document = load_har_document(FIXTURES / "field_lineage.har")
    normalized, _ = normalize_document(document)
    fields = [FieldRef(name="missing", scope="request.header", selector="x-missing")]

    result = analyze_field_lineage(normalized.entries, fields)[0]

    assert result.confidence == "unresolved"
    assert result.gaps[0].code == "field_not_found"
