"""Validate and finalize pre-freeze campaign outputs."""

from __future__ import annotations

import argparse
from pathlib import Path

from .common import write_json
from .diagnose_f1 import build_report
from .evaluate import evaluate_runs
from .validate_campaign import validate_campaign


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Finalize the official pre-freeze validation campaign.")
    parser.add_argument("--runs", default="results/enforcement/pre-freeze-validation")
    parser.add_argument("--oracle", default="benchmark/enforcement/oracle")
    parser.add_argument("--expected-runs", type=int, default=84)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    runs_root = Path(args.runs)
    report = validate_campaign(runs_root, expected_runs=args.expected_runs)
    if not report["is_complete"]:
        print("Pre-freeze validation campaign is incomplete or corrupt.")
        return 1
    diagnosis = build_report(runs_root)
    write_json(runs_root / "f1_diagnosis.json", diagnosis)
    summary = evaluate_runs(runs_root)
    write_json(runs_root / "summary.json", summary)
    print("Pre-freeze validation finalized. Freeze-ready prerequisites satisfied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
