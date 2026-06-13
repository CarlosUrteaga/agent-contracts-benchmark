"""Run the full enforcement benchmark matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

from .common import MODES, load_model_profile, scenario_paths
from .runtime import run_scenario


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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scenarios_root = Path(args.scenarios)
    contracts_root = Path(args.contracts)
    out_root = Path(args.out)
    model_profile = load_model_profile(Path(args.model_profile))
    scenarios = scenario_paths(scenarios_root)
    total_runs = len(scenarios) * len(MODES) * args.replications
    if args.dry_run:
        estimated_cost_upper_bound: float | None
        if model_profile["provider"] in {"mock", "litellm"}:
            estimated_cost_upper_bound = 0.0
        else:
            estimated_cost_upper_bound = None
        estimate = {
            "total_runs": total_runs,
            "replications": args.replications,
            "provider": model_profile["provider"],
            "model_id": model_profile["model_id"],
            "estimated_tokens_upper_bound": total_runs * model_profile["max_tokens"],
            "estimated_cost_upper_bound": estimated_cost_upper_bound,
            "estimated_serial_runtime_minutes": round(total_runs * 0.15, 2),
        }
        print(json.dumps(estimate, indent=2))
        return 0

    if out_root.exists():
        shutil.rmtree(out_root)
    count = 0
    for replication in range(1, args.replications + 1):
        replication_id = _replication_id(replication)
        for scenario_path in scenarios:
            scenario_slug = scenario_path.stem.split(".", 1)[0]
            for mode in MODES:
                run_scenario(
                    scenario_path,
                    contracts_root / f"{mode}.yaml",
                    Path(args.model_profile),
                    replication_id,
                    out_root / model_profile["profile_id"] / mode / replication_id / scenario_slug,
                )
                count += 1
    print(f"Ran {count} LLM enforcement executions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
