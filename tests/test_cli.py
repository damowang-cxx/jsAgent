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


def test_cli_analyze_with_goal_prompt_generates_analysis_intent(tmp_path: Path) -> None:
    har_path = str((FIXTURES / "basic.har").resolve())
    json_path = tmp_path / "goal-result.json"
    report_path = tmp_path / "goal-report.md"

    result = RUNNER.invoke(
        app,
        [
            "analyze",
            "--input",
            har_path,
            "--goal",
            '分析 https://example.com/api/login 接口的 "token" 字段生成逻辑',
            "--output-json",
            str(json_path),
            "--output-report",
            str(report_path),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["analysis_intent"]["input_mode"] == "goal_prompt"
    assert payload["analysis_intent"]["resolved_field"]["name"] == "token"
    assert payload["targets"]["target_fields"][0]["scope"] == "request.json"
    assert report_path.exists()


def test_cli_analyze_with_goal_file(tmp_path: Path) -> None:
    har_path = str((FIXTURES / "basic.har").resolve())
    goal_path = str((FIXTURES / "goal.txt").resolve())
    json_path = tmp_path / "goal-file-result.json"
    report_path = tmp_path / "goal-file-report.md"

    result = RUNNER.invoke(
        app,
        [
            "analyze",
            "--input",
            har_path,
            "--goal-file",
            goal_path,
            "--output-json",
            str(json_path),
            "--output-report",
            str(report_path),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["analysis_intent"]["original_prompt"]
    assert payload["analysis_intent"]["analysis_kind"] == "field_generation_logic"


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


def test_cli_goal_prompt_on_sanitized_har_keeps_resolution_and_analysis_gaps(tmp_path: Path) -> None:
    har_path = str((FIXTURES / "sanitized.har").resolve())
    json_path = tmp_path / "sanitized-goal-result.json"
    report_path = tmp_path / "sanitized-goal-report.md"

    result = RUNNER.invoke(
        app,
        [
            "analyze",
            "--input",
            har_path,
            "--goal",
            '分析 https://example.com/api/token 接口的 "token" 字段生成逻辑',
            "--output-json",
            str(json_path),
            "--output-report",
            str(report_path),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["analysis_intent"]["resolved_request"]["match_count"] == 1
    assert payload["analysis_intent"]["resolved_field"]["resolved_scopes"] == ["response.json"]
    gap_codes = {gap["code"] for gap in payload["gaps"]}
    assert "likely_sanitized_har" in gap_codes
    assert report_path.exists()


def test_cli_goal_prompt_ambiguous_scope_keeps_multiple_candidate_fields(tmp_path: Path) -> None:
    har_path = str((FIXTURES / "goal_scope_ambiguous.har").resolve())
    json_path = tmp_path / "ambiguous-result.json"
    report_path = tmp_path / "ambiguous-report.md"

    result = RUNNER.invoke(
        app,
        [
            "analyze",
            "--input",
            har_path,
            "--goal",
            '分析 https://example.com/api/sendcode 接口的 "desc" 字段生成逻辑',
            "--output-json",
            str(json_path),
            "--output-report",
            str(report_path),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["analysis_intent"]["resolution_confidence"] in {"low", "medium"}
    assert len(payload["targets"]["target_fields"]) == 2
    scopes = {item["scope"] for item in payload["targets"]["target_fields"]}
    assert scopes == {"request.json", "response.json"}
    assert any(gap["code"] == "goal_ambiguous_field_scope" for gap in payload["analysis_intent"]["resolution_gaps"])


def test_cli_goal_and_config_together_return_exit_code_2(tmp_path: Path) -> None:
    har_path = str((FIXTURES / "basic.har").resolve())
    config_path = str((FIXTURES / "config.yaml").resolve())

    result = RUNNER.invoke(
        app,
        [
            "analyze",
            "--input",
            har_path,
            "--config",
            config_path,
            "--goal",
            '分析 https://example.com/api/login 接口的 "token" 字段生成逻辑',
        ],
    )

    assert result.exit_code == 2


def test_cli_invalid_config_returns_exit_code_2(tmp_path: Path) -> None:
    har_path = str((FIXTURES / "basic.har").resolve())
    bad_config = tmp_path / "bad.yaml"
    bad_config.write_text(":", encoding="utf-8")

    result = RUNNER.invoke(app, ["analyze", "--input", har_path, "--config", str(bad_config)])

    assert result.exit_code == 2
