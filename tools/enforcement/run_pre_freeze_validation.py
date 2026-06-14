"""Run the official pre-freeze validation campaign."""

from __future__ import annotations

import argparse
from pathlib import Path

from .run_all import run_matrix


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the official pre-freeze validation campaign.")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--force-rerun", action="store_true")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--scenarios", default="benchmark/enforcement/scenarios")
    parser.add_argument("--contracts", default="contracts/enforcement")
    parser.add_argument("--model-profile", default="benchmark/enforcement/config/model_profiles/default.yaml")
    parser.add_argument("--replications", type=int, default=1)
    parser.add_argument("--out", default="results/enforcement/pre-freeze-validation")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_matrix(
        scenarios_root=Path(args.scenarios),
        contracts_root=Path(args.contracts),
        model_profile_path=Path(args.model_profile),
        replications=args.replications,
        out_root=Path(args.out),
        resume=args.resume,
        force_rerun=args.force_rerun,
        fail_fast=args.fail_fast,
    )
    print(
        "Pre-freeze campaign complete: "
        f"{result['executed_runs']} executed, "
        f"{result['skipped_runs']} skipped, "
        f"{result['rerun_partial_runs']} rerun partial."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
