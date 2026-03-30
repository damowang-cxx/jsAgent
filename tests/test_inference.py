from pathlib import Path

from har_agent.inference.correlations import ScalarObservation, collect_scalar_observations
from har_agent.inference.encodings import detect_value_encodings
from har_agent.inference.generation_candidates import analyze_value_observation, discover_candidate_fields
from har_agent.inference.heuristics import detect_value_heuristics
from har_agent.models.normalized import FieldRef
from har_agent.parsers.har_loader import load_har_document
from har_agent.parsers.normalizer import normalize_document


FIXTURES = Path(__file__).parent / "fixtures"


def _load_entries(name: str):
    document = load_har_document(FIXTURES / name)
    normalized, _ = normalize_document(document)
    return normalized.entries


def test_detect_value_encodings_covers_common_shapes() -> None:
    types = {item.type for item in detect_value_encodings("aGVsbG8=")}
    assert "base64" in types

    types = {item.type for item in detect_value_encodings("hello%20world")}
    assert "urlencoded" in types

    types = {item.type for item in detect_value_encodings("68656c6c6f")}
    assert "hex" in types

    types = {item.type for item in detect_value_encodings("{\"a\":1}")}
    assert "json_string" in types

    types = {item.type for item in detect_value_encodings("aaa.bbb.ccc")}
    assert "jwt_shape" in types


def test_detect_value_heuristics_covers_uuid_timestamp_random_and_hash() -> None:
    types = {item.type for item in detect_value_heuristics("550e8400-e29b-41d4-a716-446655440000")}
    assert "uuid" in types

    types = {item.type for item in detect_value_heuristics("1712345678901")}
    assert "timestamp" in types

    types = {item.type for item in detect_value_heuristics("9f86d081884c7d659a2feaa0c55ad015")}
    assert "hash_like" in types

    types = {item.type for item in detect_value_heuristics("A1b2C3d4E5f6G7h8")}
    assert "random_like" in types


def test_analyze_value_observation_finds_copied_from_response_candidate() -> None:
    entries = _load_entries("field_lineage.har")
    observations = collect_scalar_observations(entries)
    target = ScalarObservation(
        entry_id="entry-0001",
        timestamp=entries[1].started_at,
        scope="request.header",
        selector="x-trace-id",
        name="trace_id",
        value="trace-123",
    )

    encodings, heuristics, sources, candidates = analyze_value_observation(target, observations)

    assert encodings == []
    assert heuristics == []
    assert sources[0].source_type == "response.json"
    assert any(candidate.type == "copied_from_response" for candidate in candidates)


def test_discover_candidate_fields_finds_suspicious_and_correlated_fields() -> None:
    entries = _load_entries("field_lineage.har")
    explicit = [FieldRef(name="session", scope="request.json", selector="$.payload.session")]
    discovered = discover_candidate_fields(entries, explicit)
    discovered_pairs = {(field.scope, field.selector) for field in discovered}

    assert ("request.header", "x-trace-id") in discovered_pairs
    assert ("request.json", "$.payload.session") not in discovered_pairs
