"""Run the full enforcement benchmark matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
from typing import Any

from .common import MODES, load_model_profile, scenario_paths
from .runtime import run_scenario
from .validate_campaign import validate_run_dir


def _replication_id(index: int) -> str:
    return f"rep{index:02d}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run all enforcement scenarios for all modes.")
    parser.add_argument("--scenarios", required=True)
    parser.add_argument("--contracts", required=True)
    parser.add_argument("--model-profile", required=True)
    parser.add_argument("--replications", type=int, default=3)
    parser.add_argument("--out", default="results/enforcement/runs")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--force-rerun", action="store_true")
    parser.add_argument("--fail-fast", action="store_true")
    return parser.parse_args()


def _target_run_dir(
    out_root: Path,
    *,
    profile_id: str,
    mode: str,
    replication_id: str,
    scenario_slug: str,
) -> Path:
    return out_root / profile_id / mode / replication_id / scenario_slug


def run_matrix(
    *,
    scenarios_root: Path,
    contracts_root: Path,
    model_profile_path: Path,
    replications: int,
    out_root: Path,
    dry_run: bool = False,
    resume: bool = False,
    force_rerun: bool = False,
    fail_fast: bool = False,
) -> dict[str, Any]:
    model_profile = load_model_profile(model_profile_path)
    scenarios = scenario_paths(scenarios_root)
    total_runs = len(scenarios) * len(MODES) * replications

    completed = 0
    pending = 0
    partial = 0
    matrix: list[tuple[Path, str, str, Path]] = []
    for replication in range(1, replications + 1):
        replication_id = _replication_id(replication)
        for scenario_path in scenarios:
            scenario_slug = scenario_path.stem.split(".", 1)[0]
            for mode in MODES:
                run_dir = _target_run_dir(
                    out_root,
                    profile_id=str(model_profile["profile_id"]),
                    mode=mode,
                    replication_id=replication_id,
                    scenario_slug=scenario_slug,
                )
                matrix.append((scenario_path, scenario_slug, mode, run_dir))
                report = validate_run_dir(
                    run_dir,
                    expected_scenario_id=scenario_slug,
                    expected_mode=mode,
                    expected_replication_id=replication_id,
                    expected_profile_id=str(model_profile["profile_id"]),
                )
                if report["complete"]:
                    completed += 1
                elif run_dir.exists():
                    partial += 1
                else:
                    pending += 1

    if dry_run:
        estimated_cost_upper_bound: float | None
        if model_profile["provider"] in {"mock", "litellm"}:
            estimated_cost_upper_bound = 0.0
        else:
            estimated_cost_upper_bound = None
        estimate = {
            "total_runs": total_runs,
            "replications": replications,
            "provider": model_profile["provider"],
            "model_id": model_profile["model_id"],
            "estimated_tokens_upper_bound": total_runs * model_profile["max_tokens"],
            "estimated_cost_upper_bound": estimated_cost_upper_bound,
            "estimated_serial_runtime_minutes": round(total_runs * 0.15, 2),
            "completed_runs": completed,
            "partial_runs": partial,
            "pending_runs": pending,
        }
        return estimate

    if force_rerun and out_root.exists():
        shutil.rmtree(out_root)

    executed = skipped = rerun_partial = 0
    for replication in range(1, replications + 1):
        replication_id = _replication_id(replication)
        for scenario_path in scenarios:
            scenario_slug = scenario_path.stem.split(".", 1)[0]
            for mode in MODES:
                run_dir = _target_run_dir(
                    out_root,
                    profile_id=str(model_profile["profile_id"]),
                    mode=mode,
                    replication_id=replication_id,
                    scenario_slug=scenario_slug,
                )
                report = validate_run_dir(
                    run_dir,
                    expected_scenario_id=scenario_slug,
                    expected_mode=mode,
                    expected_replication_id=replication_id,
                    expected_profile_id=str(model_profile["profile_id"]),
                )
                if not force_rerun and report["complete"]:
                    print(f"SKIP {scenario_slug} {mode} {replication_id}")
                    skipped += 1
                    continue
                if run_dir.exists():
                    shutil.rmtree(run_dir, ignore_errors=True)
                    if any(part.startswith(("missing:", "invalid:", "trace_", "summary_", "completion_", "ledger_")) for part in report["problems"]):
                        print(f"RERUN_PARTIAL {scenario_slug} {mode} {replication_id}")
                        rerun_partial += 1
                    elif resume:
                        print(f"RUN {scenario_slug} {mode} {replication_id}")
                else:
                    print(f"RUN {scenario_slug} {mode} {replication_id}")
                try:
                    run_scenario(
                        scenario_path,
                        contracts_root / f"{mode}.yaml",
                        model_profile_path,
                        replication_id,
                        run_dir,
                    )
                except Exception:
                    if fail_fast:
                        raise
                    continue
                executed += 1
    return {
        "total_runs": total_runs,
        "executed_runs": executed,
        "skipped_runs": skipped,
        "rerun_partial_runs": rerun_partial,
        "provider": model_profile["provider"],
        "model_id": model_profile["model_id"],
        "profile_id": model_profile["profile_id"],
    }


def main() -> int:
    args = parse_args()
    result = run_matrix(
        scenarios_root=Path(args.scenarios),
        contracts_root=Path(args.contracts),
        model_profile_path=Path(args.model_profile),
        replications=args.replications,
        out_root=Path(args.out),
        dry_run=args.dry_run,
        resume=args.resume,
        force_rerun=args.force_rerun,
        fail_fast=args.fail_fast,
    )
    if args.dry_run:
        print(json.dumps(result, indent=2))
    else:
        print(
            "Ran "
            f"{result['executed_runs']} LLM enforcement executions "
            f"({result['skipped_runs']} skipped, {result['rerun_partial_runs']} rerun partial)."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
