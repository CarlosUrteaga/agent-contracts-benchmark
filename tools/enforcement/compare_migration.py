# Copyright (c) 2026 Jorge Carlos Urteaga Reyesvera
# SPDX-License-Identifier: Apache-2.0

"""Compare two deterministic enforcement campaigns across a runner migration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ARTIFACTS = ("summary.json", "trace.jsonl", "run_ledger.json", "run_complete.json")


def _without_run_timing(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _without_run_timing(item)
            for key, item in value.items()
            if key != "completed_at" and not key.endswith("latency_ms")
        }
    if isinstance(value, list):
        return [_without_run_timing(item) for item in value]
    return value


def compare_campaigns(
    baseline: Path,
    candidate: Path,
    *,
    baseline_metrics: Path | None = None,
    candidate_metrics: Path | None = None,
) -> list[str]:
    """Return semantic differences, ignoring only measurement time and timestamps."""
    errors: list[str] = []
    baseline_runs = {p.parent.relative_to(baseline) for p in baseline.rglob("summary.json")}
    candidate_runs = {p.parent.relative_to(candidate) for p in candidate.rglob("summary.json")}
    for run in sorted(baseline_runs - candidate_runs):
        errors.append(f"missing candidate run: {run}")
    for run in sorted(candidate_runs - baseline_runs):
        errors.append(f"unexpected candidate run: {run}")
    for run in sorted(baseline_runs & candidate_runs):
        for name in ARTIFACTS:
            left, right = baseline / run / name, candidate / run / name
            if not left.is_file() or not right.is_file():
                errors.append(f"missing artifact: {run}/{name}")
                continue
            if name == "trace.jsonl":
                equal = left.read_bytes() == right.read_bytes()
            else:
                equal = _without_run_timing(json.loads(left.read_text())) == _without_run_timing(
                    json.loads(right.read_text())
                )
            if not equal:
                errors.append(f"artifact differs: {run}/{name}")
    if (baseline_metrics is None) != (candidate_metrics is None):
        raise ValueError("Provide both metrics files or neither")
    if baseline_metrics is not None and candidate_metrics is not None:
        left = _without_run_timing(json.loads(baseline_metrics.read_text()))
        right = _without_run_timing(json.loads(candidate_metrics.read_text()))
        if left != right:
            errors.append("non-latency metrics differ")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--baseline-metrics", type=Path)
    parser.add_argument("--candidate-metrics", type=Path)
    args = parser.parse_args()
    differences = compare_campaigns(
        args.baseline,
        args.candidate,
        baseline_metrics=args.baseline_metrics,
        candidate_metrics=args.candidate_metrics,
    )
    if differences:
        for difference in differences:
            print(difference)
        return 1
    count = sum(1 for _ in args.baseline.rglob("summary.json"))
    print(f"Semantically equivalent: {count} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
