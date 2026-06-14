"""Validate enforcement campaign completeness and per-run artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .common import RUN_COMPLETE_FILE, RUN_LEDGER_FILE, SUMMARY_FILE, TRACE_FILE, read_json


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"{path} contains non-object JSONL row")
        rows.append(row)
    return rows


def _metadata_matches(value: Any, expected: str | None) -> bool:
    if expected is None:
        return True
    return str(value) == expected


def validate_run_dir(
    run_dir: Path,
    *,
    expected_scenario_id: str | None = None,
    expected_mode: str | None = None,
    expected_replication_id: str | None = None,
    expected_profile_id: str | None = None,
    require_completion_marker: bool = True,
) -> dict[str, Any]:
    artifact_paths = {
        SUMMARY_FILE: run_dir / SUMMARY_FILE,
        TRACE_FILE: run_dir / TRACE_FILE,
        RUN_LEDGER_FILE: run_dir / RUN_LEDGER_FILE,
    }
    if require_completion_marker:
        artifact_paths[RUN_COMPLETE_FILE] = run_dir / RUN_COMPLETE_FILE
    problems: list[str] = []
    parsed: dict[str, Any] = {}

    for name, path in artifact_paths.items():
        if not path.exists():
            problems.append(f"missing:{name}")

    if problems:
        return {"complete": False, "problems": problems, "run_dir": str(run_dir)}

    try:
        parsed["summary"] = read_json(artifact_paths[SUMMARY_FILE])
    except Exception as exc:  # pragma: no cover - exercised via tests
        problems.append(f"invalid:{SUMMARY_FILE}:{exc}")

    try:
        parsed["ledger"] = read_json(artifact_paths[RUN_LEDGER_FILE])
    except Exception as exc:  # pragma: no cover - exercised via tests
        problems.append(f"invalid:{RUN_LEDGER_FILE}:{exc}")

    if require_completion_marker:
        try:
            parsed["complete"] = read_json(artifact_paths[RUN_COMPLETE_FILE])
        except Exception as exc:  # pragma: no cover - exercised via tests
            problems.append(f"invalid:{RUN_COMPLETE_FILE}:{exc}")

    try:
        parsed["trace"] = _read_jsonl(artifact_paths[TRACE_FILE])
    except Exception as exc:  # pragma: no cover - exercised via tests
        problems.append(f"invalid:{TRACE_FILE}:{exc}")

    if problems:
        return {"complete": False, "problems": problems, "run_dir": str(run_dir)}

    summary = parsed["summary"]
    ledger = parsed["ledger"]
    completion = parsed.get("complete", {})
    trace_rows = parsed["trace"]

    for field in [
        "scenario_id",
        "mode",
        "replication_id",
        "final_status",
        "validation_phases",
        "run_ledger_artifact_present",
        "run_ledger_presented_to_governor",
        "run_ledger_complete_for_governor",
        "run_ledger_valid",
    ]:
        if field not in summary:
            problems.append(f"summary_missing:{field}")

    if not trace_rows:
        problems.append("trace_empty")
    else:
        if trace_rows[0].get("event") != "run_started":
            problems.append("trace_missing_run_started")
        if trace_rows[-1].get("event") != "run_finished":
            problems.append("trace_missing_run_finished")

    if summary.get("run_ledger_artifact_present") is not True:
        problems.append("summary_run_ledger_artifact_present_false")

    if require_completion_marker:
        if not completion.get("artifacts"):
            problems.append("completion_missing_artifacts")
        else:
            declared = set(completion["artifacts"])
            required = {SUMMARY_FILE, TRACE_FILE, RUN_LEDGER_FILE}
            if declared != required:
                problems.append("completion_artifacts_mismatch")

    if not _metadata_matches(summary.get("scenario_id"), expected_scenario_id):
        problems.append("summary_scenario_mismatch")
    if not _metadata_matches(summary.get("mode"), expected_mode):
        problems.append("summary_mode_mismatch")
    if not _metadata_matches(summary.get("replication_id"), expected_replication_id):
        problems.append("summary_replication_mismatch")
    if require_completion_marker:
        if expected_profile_id is not None and str(completion.get("profile_id")) != expected_profile_id:
            problems.append("completion_profile_mismatch")
        if expected_scenario_id is not None and str(completion.get("scenario_id")) != expected_scenario_id:
            problems.append("completion_scenario_mismatch")
        if expected_mode is not None and str(completion.get("mode")) != expected_mode:
            problems.append("completion_mode_mismatch")
        if expected_replication_id is not None and str(completion.get("replication_id")) != expected_replication_id:
            problems.append("completion_replication_mismatch")

    if str(ledger.get("scenario_id")) != str(summary.get("scenario_id")):
        problems.append("ledger_scenario_mismatch")
    if str(ledger.get("mode")) != str(summary.get("mode")):
        problems.append("ledger_mode_mismatch")
    if str(ledger.get("replication_id")) != str(summary.get("replication_id")):
        problems.append("ledger_replication_mismatch")

    return {
        "complete": not problems,
        "problems": problems,
        "run_dir": str(run_dir),
        "summary": summary,
    }


def find_candidate_run_dirs(runs_root: Path) -> list[Path]:
    return sorted(path for path in runs_root.glob("**/S-*") if path.is_dir())


def validate_campaign(runs_root: Path, *, expected_runs: int) -> dict[str, Any]:
    run_dirs = find_candidate_run_dirs(runs_root)
    valid: list[str] = []
    invalid: list[dict[str, Any]] = []
    for run_dir in run_dirs:
        report = validate_run_dir(run_dir)
        if report["complete"]:
            valid.append(str(run_dir))
        else:
            has_any_artifact = any((run_dir / name).exists() for name in [SUMMARY_FILE, TRACE_FILE, RUN_LEDGER_FILE, RUN_COMPLETE_FILE])
            if has_any_artifact:
                invalid.append(report)
    complete_valid_runs = len(valid)
    partial_or_corrupt_runs = len(invalid)
    missing_runs = max(expected_runs - complete_valid_runs, 0)
    return {
        "runs_root": str(runs_root),
        "expected_runs": expected_runs,
        "complete_valid_runs": complete_valid_runs,
        "partial_or_corrupt_runs": partial_or_corrupt_runs,
        "missing_runs": missing_runs,
        "invalid_runs": invalid,
        "valid_run_dirs": valid,
        "is_complete": complete_valid_runs == expected_runs and partial_or_corrupt_runs == 0,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate enforcement campaign completeness.")
    parser.add_argument("--runs", required=True)
    parser.add_argument("--expected-runs", type=int, required=True)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = validate_campaign(Path(args.runs), expected_runs=args.expected_runs)
    print(json.dumps(report, indent=2))
    return 0 if report["is_complete"] or not args.strict else 1


if __name__ == "__main__":
    raise SystemExit(main())
