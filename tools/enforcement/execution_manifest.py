"""Generate reproducible execution manifests for post-freeze benchmark campaigns."""

from __future__ import annotations

import argparse
import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .common import MODES, SCENARIOS_ROOT, ensure_relative, load_model_profile, read_json, write_json

SCHEMA_VERSION = "execution-manifest-v1"
GENERATOR = {"tool": "tools.enforcement.execution_manifest", "version": "v1"}
REQUIRED_PROFILE_FIELDS = ("profile_id", "provider", "model_id", "declared_model_version")


def _sha256_file_bytes(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _require_profile_fields(model_profile: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_PROFILE_FIELDS if field not in model_profile]
    if missing:
        raise ValueError(f"model profile missing required fields: {', '.join(missing)}")


def build_execution_manifest(
    *,
    benchmark_manifest_path: Path,
    model_profile_path: Path,
    replications: int,
    runs_root: Path,
    campaign_id: str | None = None,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    if replications <= 0:
        raise ValueError("replications must be a positive integer")

    benchmark_manifest = read_json(benchmark_manifest_path)
    for field in ("benchmark_version", "freeze_commit"):
        if field not in benchmark_manifest:
            raise ValueError(f"benchmark manifest missing required field: {field}")

    model_profile = load_model_profile(model_profile_path)
    _require_profile_fields(model_profile)

    scenario_count = len(sorted(SCENARIOS_ROOT.glob("S-*.json")))
    mode_count = len(MODES)
    resolved_campaign_id = campaign_id or runs_root.name

    return {
        "manifest_schema_version": SCHEMA_VERSION,
        "benchmark_version": benchmark_manifest["benchmark_version"],
        "benchmark_manifest_path": ensure_relative(benchmark_manifest_path),
        "freeze_commit": benchmark_manifest["freeze_commit"],
        "generated_at": datetime.now(UTC).isoformat(),
        "campaign_id": resolved_campaign_id,
        "runs_root": ensure_relative(runs_root),
        "model_profile_path": ensure_relative(model_profile_path),
        "model_profile_hash": _sha256_file_bytes(model_profile_path),
        "profile_id": model_profile["profile_id"],
        "provider": model_profile["provider"],
        "model_id": model_profile["model_id"],
        "declared_model_version": model_profile["declared_model_version"],
        "replications": replications,
        "scenario_count": scenario_count,
        "mode_count": mode_count,
        "expected_total_runs": scenario_count * mode_count * replications,
        "generator": dict(GENERATOR),
        "notes": list(notes or []),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a post-freeze execution manifest for a benchmark campaign.")
    parser.add_argument("--benchmark-manifest", required=True)
    parser.add_argument("--model-profile", required=True)
    parser.add_argument("--replications", type=int, required=True)
    parser.add_argument("--runs-root", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--campaign-id")
    parser.add_argument("--note", action="append", default=[])
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_path = Path(args.out)
    if out_path.exists() and not args.force:
        print(f"Refusing to overwrite existing execution manifest: {args.out}. Re-run with --force.")
        return 1
    manifest = build_execution_manifest(
        benchmark_manifest_path=Path(args.benchmark_manifest),
        model_profile_path=Path(args.model_profile),
        replications=args.replications,
        runs_root=Path(args.runs_root),
        campaign_id=args.campaign_id,
        notes=list(args.note),
    )
    write_json(out_path, manifest)
    print(f"Wrote execution manifest to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
