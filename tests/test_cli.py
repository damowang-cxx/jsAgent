import json
from pathlib import Path

from typer.testing import CliRunner

from har_agent.cli import app


FIXTURES = Path(__file__).parent / "fixtures"
RUNNER = CliRunner()


def test_cli_help() -> None:
    result = RUNNER.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "analyze" in result.stdout


def test_cli_analyze_uses_default_output_paths(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    har_path = str((FIXTURES / "basic.har").resolve())

    result = RUNNER.invoke(app, ["analyze", "--input", har_path])

    assert result.exit_code == 0
    assert (tmp_path / "out" / "result.json").exists()
    assert (tmp_path / "out" / "report.md").exists()
    payload = json.loads((tmp_path / "out" / "result.json").read_text(encoding="utf-8"))
    assert "summary" in payload
    assert "cookie_lineage" in payload
    assert "field_analysis" in payload


def test_cli_analyze_with_config_and_explicit_outputs(tmp_path: Path) -> None:
    har_path = str((FIXTURES / "basic.har").resolve())
    config_path = str((FIXTURES / "config.yaml").resolve())
    json_path = tmp_path / "custom-result.json"
    report_path = tmp_path / "custom-report.md"

    result = RUNNER.invoke(
        app,
        [
            "analyze",
            "--input",
            har_path,
            "--config",
            config_path,
            "--output-json",
            str(json_path),
            "--output-report",
            str(report_path),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["matched_requests"][0]["url"].endswith("/api/login?trace=1")
    assert payload["cookie_lineage"][0]["cookie_name"] == "sid"
    assert report_path.exists()


def test_cli_sanitized_har_keeps_running_and_records_gaps(tmp_path: Path) -> None:
    har_path = str((FIXTURES / "sanitized.har").resolve())
    json_path = tmp_path / "sanitized-result.json"
    report_path = tmp_path / "sanitized-report.md"

    result = RUNNER.invoke(
        app,
        [
            "analyze",
            "--input",
            har_path,
            "--output-json",
            str(json_path),
            "--output-report",
            str(report_path),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    gap_codes = {gap["code"] for gap in payload["gaps"]}
    assert "likely_sanitized_har" in gap_codes
    assert report_path.exists()


def test_cli_invalid_config_returns_exit_code_2(tmp_path: Path) -> None:
    har_path = str((FIXTURES / "basic.har").resolve())
    bad_config = tmp_path / "bad.yaml"
    bad_config.write_text(":", encoding="utf-8")

    result = RUNNER.invoke(app, ["analyze", "--input", har_path, "--config", str(bad_config)])

    assert result.exit_code == 2
