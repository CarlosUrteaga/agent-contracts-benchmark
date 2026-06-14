"""Diagnose runtime F1 degradation on enforcement benchmark runs."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .common import SCENARIOS_ROOT, load_scenarios_index, read_json, run_summary_paths, write_json
from .evaluate import run_has_violation_opportunity, runtime_detection_target, runtime_observed_rules

PRE_EXECUTION_RULES = {
    "agent.configuration_fingerprint_match",
    "contract.fingerprint_match",
}

POST_EXECUTION_RULES = {
    "forbidden.outcome_triggered",
    "response.schema_complete",
    "run_ledger.complete",
    "run_ledger.required",
}

def _scenario_expectations(summary: dict[str, Any], scenarios_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    scenario_id = summary.get("scenario_id")
    if scenario_id is None:
        return summary
    return scenarios_by_id.get(str(scenario_id), summary)


def _expected_runtime_rules(summary: dict[str, Any], scenarios_by_id: dict[str, dict[str, Any]]) -> set[str]:
    return set(_scenario_expectations(summary, scenarios_by_id).get("expected_violations_if_attempted", []))


def _expected_pre_rules(summary: dict[str, Any], scenarios_by_id: dict[str, dict[str, Any]]) -> set[str]:
    return set(_scenario_expectations(summary, scenarios_by_id).get("expected_pre_execution_violations", []))


def _expected_post_rules(summary: dict[str, Any], scenarios_by_id: dict[str, dict[str, Any]]) -> set[str]:
    return set(_scenario_expectations(summary, scenarios_by_id).get("expected_post_execution_violations", []))


def _phase_mixing_rules(summary: dict[str, Any], scenarios_by_id: dict[str, dict[str, Any]]) -> set[str]:
    expected_runtime = _expected_runtime_rules(summary, scenarios_by_id)
    return {
        rule
        for rule in expected_runtime
        if rule in PRE_EXECUTION_RULES or rule in POST_EXECUTION_RULES
    }


def classify_run(summary: dict[str, Any], scenarios_by_id: dict[str, dict[str, Any]] | None = None) -> str:
    scenarios_by_id = scenarios_by_id or {}
    if not runtime_detection_target(summary, scenarios_by_id):
        return "excluded_runtime_detection"
    expected_runtime = _expected_runtime_rules(summary, scenarios_by_id)
    detected_runtime = runtime_observed_rules(summary)
    if _phase_mixing_rules(summary, scenarios_by_id):
        return "D_phase_mixing"
    if expected_runtime and detected_runtime and not (expected_runtime & detected_runtime):
        return "A_oracle_misalignment"
    if expected_runtime and not run_has_violation_opportunity(summary, scenarios_by_id):
        return "B_conservative_or_divergent_agent"
    suspicious_outcome = bool(summary.get("unsafe_side_effects_committed")) or bool(summary.get("forbidden_outcome_triggered"))
    if expected_runtime and suspicious_outcome and not (expected_runtime & detected_runtime):
        return "C_candidate"
    return "none"


def build_report(runs_root: Path, scenario_root: Path | None = None) -> dict[str, Any]:
    summaries = [read_json(path) for path in run_summary_paths(runs_root)]
    if not summaries:
        raise ValueError(f"no summary files found under {runs_root}")
    scenarios_by_id = load_scenarios_index(scenario_root or SCENARIOS_ROOT)

    rows: list[dict[str, Any]] = []
    counts_by_mode: dict[str, Counter[str]] = defaultdict(Counter)
    counts_by_scenario: dict[str, Counter[str]] = defaultdict(Counter)

    for summary in summaries:
        expected_runtime = sorted(_expected_runtime_rules(summary, scenarios_by_id))
        detected_runtime = sorted(runtime_observed_rules(summary))
        expected_pre = sorted(_expected_pre_rules(summary, scenarios_by_id))
        expected_post = sorted(_expected_post_rules(summary, scenarios_by_id))
        tp_rules = sorted(set(expected_runtime) & set(detected_runtime))
        fp_rules = sorted(set(detected_runtime) - set(expected_runtime))
        fn_rules = sorted(set(expected_runtime) - set(detected_runtime))
        cause = classify_run(summary, scenarios_by_id)
        row = {
            "scenario_id": summary["scenario_id"],
            "mode": summary["mode"],
            "final_status": summary["final_status"],
            "expected_runtime_rules": expected_runtime,
            "expected_pre_execution_rules": expected_pre,
            "expected_post_execution_rules": expected_post,
            "detected_runtime_rules": detected_runtime,
            "tp_rules": tp_rules,
            "fp_rules": fp_rules,
            "fn_rules": fn_rules,
            "violation_opportunity_observed": bool(summary.get("violation_opportunity_observed")),
            "phase_mixing_rules": sorted(_phase_mixing_rules(summary, scenarios_by_id)),
            "runtime_detection_target": runtime_detection_target(summary, scenarios_by_id),
            "preliminary_cause": cause,
        }
        if expected_runtime or detected_runtime or expected_pre or expected_post:
            rows.append(row)
        counts_by_mode[str(summary["mode"])][cause] += 1
        counts_by_scenario[str(summary["scenario_id"])][cause] += 1

    return {
        "runs_total": len(summaries),
        "report_rows": rows,
        "counts_by_mode": {mode: dict(counter) for mode, counter in sorted(counts_by_mode.items())},
        "counts_by_scenario": {
            scenario_id: dict(counter) for scenario_id, counter in sorted(counts_by_scenario.items())
        },
        "notes": [
            "Runtime F1 diagnosis uses expected_violations_if_attempted as runtime-only expectations.",
            "Pre- and post-execution expectations are reported separately and do not participate in runtime TP/FP/FN.",
            "C_candidate requires manual trace review before changing Governor logic.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diagnose runtime F1 degradation on enforcement runs.")
    parser.add_argument("--runs", required=True)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(Path(args.runs))
    write_json(Path(args.out), report)
    print(f"Diagnosed {report['runs_total']} enforcement runs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
