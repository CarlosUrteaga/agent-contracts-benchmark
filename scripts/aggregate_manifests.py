#!/usr/bin/env python3
"""Aggregate canonical benchmark manifests into CSV and QC summaries."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def manifest_paths(root: Path) -> list[Path]:
    return sorted(root.glob("*/*/*/*/manifest.json"))


def average(values: list[float]) -> float:
    return round(sum(values) / len(values), 6) if values else 0.0


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "manifest_count": len(rows),
        "avg_changed_file_count": average([float(row["changed_file_count"]) for row in rows]),
        "avg_change_spread": average([float(row["change_spread"]) for row in rows]),
        "avg_traceability_ratio": average([float(row["traceability_ratio"]) for row in rows]),
        "avg_test_failures": average([float(row["test_failures"]) for row in rows]),
        "avg_contract_violations": average([float(row["contract_violations"]) for row in rows]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", default="benchmark/manifests")
    parser.add_argument("--out", default="results")
    args = parser.parse_args()

    runs_root = Path(args.runs)
    out_root = Path(args.out)
    manifests = manifest_paths(runs_root)

    rows: list[dict[str, Any]] = []
    by_arm_strategy_step: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    by_arm_strategy: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    trajectories: set[tuple[str, str, str]] = set()

    for manifest_path in manifests:
        manifest = load_manifest(manifest_path)
        row = {
            "manifest_path": str(manifest_path),
            "strategy": manifest["strategy"],
            "arm": manifest["arm"],
            "replication": manifest["replication"],
            "step": manifest.get("step", manifest.get("step_id")),
            "changed_file_count": manifest["changed_file_count"],
            "change_spread": manifest["change_spread"],
            "traceability_ratio": manifest["traceability_ratio"],
            "test_failures": manifest["test_failures"],
            "contract_violations": manifest["contract_violations"],
            "run_ledger_compliance": manifest["run_ledger_compliance"],
        }
        rows.append(row)
        by_arm_strategy_step[(row["arm"], row["strategy"], row["step"])].append(row)
        by_arm_strategy[(row["arm"], row["strategy"])].append(row)
        trajectories.add((row["strategy"], row["arm"], row["replication"]))

    write_csv(
        out_root / "manifest_rows.csv",
        rows,
        [
            "manifest_path",
            "strategy",
            "arm",
            "replication",
            "step",
            "changed_file_count",
            "change_spread",
            "traceability_ratio",
            "test_failures",
            "contract_violations",
            "run_ledger_compliance",
        ],
    )

    step_summary_rows: list[dict[str, Any]] = []
    for (arm, strategy, step), grouped_rows in sorted(by_arm_strategy_step.items()):
        step_summary_rows.append(
            {
                "arm": arm,
                "strategy": strategy,
                "step": step,
                **summarize_group(grouped_rows),
            }
        )
    write_csv(
        out_root / "summary_by_arm_strategy_step.csv",
        step_summary_rows,
        [
            "arm",
            "strategy",
            "step",
            "manifest_count",
            "avg_changed_file_count",
            "avg_change_spread",
            "avg_traceability_ratio",
            "avg_test_failures",
            "avg_contract_violations",
        ],
    )

    strategy_summary_rows: list[dict[str, Any]] = []
    for (arm, strategy), grouped_rows in sorted(by_arm_strategy.items()):
        strategy_summary_rows.append(
            {
                "arm": arm,
                "strategy": strategy,
                **summarize_group(grouped_rows),
            }
        )
    write_csv(
        out_root / "summary_by_arm_strategy.csv",
        strategy_summary_rows,
        [
            "arm",
            "strategy",
            "manifest_count",
            "avg_changed_file_count",
            "avg_change_spread",
            "avg_traceability_ratio",
            "avg_test_failures",
            "avg_contract_violations",
        ],
    )

    qc_report = {
        "manifest_root": str(runs_root),
        "total_manifests": len(rows),
        "expected_total_manifests": 84,
        "trajectory_count": len(trajectories),
        "expected_trajectory_count": 24,
        "status": "pass" if len(rows) == 84 and len(trajectories) == 24 else "fail",
    }
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "qc_report.json").write_text(json.dumps(qc_report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote manifest aggregation to {out_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
