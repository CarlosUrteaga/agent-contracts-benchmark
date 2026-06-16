"""Validate that a post-freeze execution manifest matches the intended campaign inputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .common import ensure_relative, read_json
from .execution_manifest import build_execution_manifest


def validate_execution_manifest(
    manifest_path: Path,
    *,
    benchmark_manifest_path: Path,
    model_profile_path: Path,
    replications: int,
    runs_root: Path,
) -> dict[str, Any]:
    actual = read_json(manifest_path)
    expected = build_execution_manifest(
        benchmark_manifest_path=benchmark_manifest_path,
        model_profile_path=model_profile_path,
        replications=replications,
        runs_root=runs_root,
        campaign_id=str(actual.get("campaign_id") or runs_root.name),
        notes=list(actual.get("notes") or []),
    )

    mismatches: list[str] = []
    fields = [
        "manifest_schema_version",
        "benchmark_version",
        "benchmark_manifest_path",
        "freeze_commit",
        "campaign_id",
        "runs_root",
        "model_profile_path",
        "model_profile_hash",
        "profile_id",
        "provider",
        "model_id",
        "declared_model_version",
        "replications",
        "scenario_count",
        "mode_count",
        "expected_total_runs",
    ]
    for field in fields:
        if actual.get(field) != expected.get(field):
            mismatches.append(field)

    if actual.get("generator") != expected.get("generator"):
        mismatches.append("generator")

    return {
        "manifest_path": ensure_relative(manifest_path),
        "benchmark_manifest_path": ensure_relative(benchmark_manifest_path),
        "model_profile_path": ensure_relative(model_profile_path),
        "runs_root": ensure_relative(runs_root),
        "replications": replications,
        "matches": not mismatches,
        "mismatches": mismatches,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a post-freeze execution manifest.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--benchmark-manifest", required=True)
    parser.add_argument("--model-profile", required=True)
    parser.add_argument("--replications", type=int, required=True)
    parser.add_argument("--runs-root", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = validate_execution_manifest(
        Path(args.manifest),
        benchmark_manifest_path=Path(args.benchmark_manifest),
        model_profile_path=Path(args.model_profile),
        replications=args.replications,
        runs_root=Path(args.runs_root),
    )
    print(json.dumps(report, indent=2))
    return 0 if report["matches"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
