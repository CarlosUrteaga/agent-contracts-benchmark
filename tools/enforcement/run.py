"""Run a single enforcement scenario."""

from __future__ import annotations

import argparse

from .runtime import run_scenario_from_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a single enforcement scenario.")
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--mode", required=True)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--model-profile", required=True)
    parser.add_argument("--replication-id", required=True)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = run_scenario_from_paths(
        args.scenario,
        args.contract,
        args.model_profile,
        args.replication_id,
        args.out,
    )
    print(f"{summary['scenario_id']} {summary['mode']} {summary['replication_id']} -> {summary['final_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
