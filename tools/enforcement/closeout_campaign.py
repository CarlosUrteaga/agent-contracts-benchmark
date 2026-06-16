"""Close out a post-freeze campaign by validating it and generating derived artifacts."""

from __future__ import annotations

import argparse
import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .common import REPO_ROOT, ensure_relative, read_json, write_json, write_text
from .diagnose_f1 import build_report
from .evaluate import evaluate_runs
from .validate_campaign import validate_campaign
from .validate_execution_manifest import validate_execution_manifest


def _resolve_repo_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def _sha256_file(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _closeout_markdown(
    manifest: dict[str, Any],
    *,
    complete_valid_runs: int,
    partial_or_corrupt_runs: int,
    summary_present: bool,
    diagnosis_present: bool,
) -> str:
    lines = [
        f"# Campaign Closeout — {manifest['campaign_id']}",
        "",
        f"- benchmark_version: `{manifest['benchmark_version']}`",
        f"- freeze_commit: `{manifest['freeze_commit']}`",
        f"- runs_root: `{manifest['runs_root']}`",
        f"- model_profile_path: `{manifest['model_profile_path']}`",
        f"- profile_id: `{manifest['profile_id']}`",
        f"- provider: `{manifest['provider']}`",
        f"- model_id: `{manifest['model_id']}`",
        f"- declared_model_version: `{manifest['declared_model_version']}`",
        f"- expected_total_runs: `{manifest['expected_total_runs']}`",
        f"- complete_valid_runs: `{complete_valid_runs}`",
        f"- partial_or_corrupt_runs: `{partial_or_corrupt_runs}`",
        f"- closed_at: `{datetime.now(UTC).isoformat()}`",
        f"- summary_generated: `{'yes' if summary_present else 'no'}`",
        f"- diagnosis_generated: `{'yes' if diagnosis_present else 'no'}`",
        "- note: `no benchmark changes after execution`",
        "",
        "## Artifacts",
        "",
        f"- execution manifest: `{manifest['runs_root']}/execution_manifest.json`",
        f"- summary: `{manifest['runs_root']}/summary.json`",
        f"- diagnosis: `{manifest['runs_root']}/f1_diagnosis.json`",
        f"- artifact hashes: `{manifest['runs_root']}/artifact_hashes.json`",
    ]
    return "\n".join(lines) + "\n"


def closeout_campaign(manifest_path: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    benchmark_manifest_path = _resolve_repo_path(str(manifest["benchmark_manifest_path"]))
    model_profile_path = _resolve_repo_path(str(manifest["model_profile_path"]))
    runs_root = _resolve_repo_path(str(manifest["runs_root"]))

    manifest_report = validate_execution_manifest(
        manifest_path,
        benchmark_manifest_path=benchmark_manifest_path,
        model_profile_path=model_profile_path,
        replications=int(manifest["replications"]),
        runs_root=runs_root,
    )
    if not manifest_report["matches"]:
        raise ValueError(f"execution manifest does not match campaign inputs: {manifest_report['mismatches']}")

    campaign_report = validate_campaign(runs_root, expected_runs=int(manifest["expected_total_runs"]))
    if not campaign_report["is_complete"]:
        raise ValueError("campaign is incomplete or corrupt")

    diagnosis = build_report(runs_root)
    summary = evaluate_runs(runs_root)
    expected_total_runs = int(manifest["expected_total_runs"])
    if int(diagnosis["runs_total"]) != expected_total_runs:
        raise ValueError("diagnosis runs_total does not match expected_total_runs")
    if int(summary["runs_total"]) != expected_total_runs:
        raise ValueError("summary runs_total does not match expected_total_runs")

    diagnosis_path = runs_root / "f1_diagnosis.json"
    summary_path = runs_root / "summary.json"
    hashes_path = runs_root / "artifact_hashes.json"
    closeout_path = runs_root / "campaign_closeout.md"

    write_json(diagnosis_path, diagnosis)
    write_json(summary_path, summary)

    artifact_hashes = {
        "execution_manifest.json": _sha256_file(manifest_path),
        "summary.json": _sha256_file(summary_path),
        "f1_diagnosis.json": _sha256_file(diagnosis_path),
    }
    write_json(hashes_path, artifact_hashes)
    write_text(
        closeout_path,
        _closeout_markdown(
            manifest,
            complete_valid_runs=int(campaign_report["complete_valid_runs"]),
            partial_or_corrupt_runs=int(campaign_report["partial_or_corrupt_runs"]),
            summary_present=summary_path.exists(),
            diagnosis_present=diagnosis_path.exists(),
        ),
    )

    return {
        "campaign_id": manifest["campaign_id"],
        "runs_root": ensure_relative(runs_root),
        "expected_total_runs": expected_total_runs,
        "complete_valid_runs": int(campaign_report["complete_valid_runs"]),
        "partial_or_corrupt_runs": int(campaign_report["partial_or_corrupt_runs"]),
        "summary_path": ensure_relative(summary_path),
        "diagnosis_path": ensure_relative(diagnosis_path),
        "artifact_hashes_path": ensure_relative(hashes_path),
        "closeout_path": ensure_relative(closeout_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and close out a post-freeze benchmark campaign.")
    parser.add_argument("--manifest", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = closeout_campaign(Path(args.manifest))
    print(f"Closed out {report['campaign_id']} with {report['complete_valid_runs']} valid runs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
