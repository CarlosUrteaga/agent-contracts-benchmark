"""Validate the frozen oracle catalog and specification."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from .common import ORACLE_ROOT, REPO_ROOT, SCENARIOS_ROOT, ensure_relative, load_scenarios_index, read_json

STRUCTURAL_RUNTIME_EXCLUSIONS = {
    "S-016": "structural_runtime_exclusion",
}

REQUIRED_SPEC_HEADINGS = [
    "## Purpose",
    "## Oracle inputs",
    "## Oracle outputs",
    "## Success definition",
    "## Unsafe opportunity definition",
    "## Runtime violation definition",
    "## Runtime F1 participation",
    "## Structural exclusions",
    "## Oracle invariants",
]


def _required_catalog_keys() -> set[str]:
    return {
        "scenario_id",
        "scenario_type",
        "acceptable_outcomes",
        "forbidden_outcomes",
        "expected_runtime_rules",
        "expected_pre_execution_rules",
        "expected_post_execution_rules",
        "runtime_detection_target",
        "runtime_f1_participates",
        "structural_exclusion_reason",
        "expected_final_properties",
    }


def validate_oracle(
    *,
    scenario_root: Path = SCENARIOS_ROOT,
    catalog_path: Path = ORACLE_ROOT / "scenario_catalog.json",
    spec_path: Path = REPO_ROOT / "docs" / "oracle_spec.md",
) -> dict[str, Any]:
    scenarios_by_id = load_scenarios_index(scenario_root)
    catalog = read_json(catalog_path)
    spec_text = spec_path.read_text(encoding="utf-8")

    issues: list[str] = []
    catalog_rows = catalog.get("scenarios", [])
    if not isinstance(catalog_rows, list):
        raise ValueError("oracle catalog must contain a 'scenarios' array")
    catalog_by_id = {str(row["scenario_id"]): row for row in catalog_rows}

    if int(catalog.get("scenarios_total", 0)) != len(scenarios_by_id):
        issues.append(
            f"scenarios_total mismatch: catalog={catalog.get('scenarios_total')} scenarios={len(scenarios_by_id)}"
        )

    for heading in REQUIRED_SPEC_HEADINGS:
        if heading not in spec_text:
            issues.append(f"missing oracle spec heading: {heading}")

    structural_rows: dict[str, str] = {}
    for scenario_id, scenario in sorted(scenarios_by_id.items()):
        row = catalog_by_id.get(scenario_id)
        if row is None:
            issues.append(f"missing scenario in oracle catalog: {scenario_id}")
            continue
        missing_keys = sorted(_required_catalog_keys() - set(row))
        if missing_keys:
            issues.append(f"{scenario_id} missing oracle catalog keys: {', '.join(missing_keys)}")
            continue

        expected_runtime = set(scenario.get("expected_violations_if_attempted", []))
        expected_pre = set(scenario.get("expected_pre_execution_violations", []))
        expected_post = set(scenario.get("expected_post_execution_violations", []))
        scenario_overlap = (expected_runtime & expected_pre) | (expected_runtime & expected_post) | (expected_pre & expected_post)
        if scenario_overlap:
            issues.append(f"{scenario_id} overlapping runtime/pre/post rules in scenario source: {', '.join(sorted(scenario_overlap))}")

        catalog_runtime = set(row["expected_runtime_rules"])
        catalog_pre = set(row["expected_pre_execution_rules"])
        catalog_post = set(row["expected_post_execution_rules"])
        catalog_overlap = (catalog_runtime & catalog_pre) | (catalog_runtime & catalog_post) | (catalog_pre & catalog_post)
        if catalog_overlap:
            issues.append(f"{scenario_id} overlapping runtime/pre/post rules in oracle catalog: {', '.join(sorted(catalog_overlap))}")

        if catalog_runtime != expected_runtime:
            issues.append(f"{scenario_id} runtime rule mismatch between scenario and oracle catalog")
        if catalog_pre != expected_pre:
            issues.append(f"{scenario_id} pre-execution rule mismatch between scenario and oracle catalog")
        if catalog_post != expected_post:
            issues.append(f"{scenario_id} post-execution rule mismatch between scenario and oracle catalog")
        if list(row["acceptable_outcomes"]) != list(scenario["acceptable_outcomes"]):
            issues.append(f"{scenario_id} acceptable_outcomes mismatch between scenario and oracle catalog")
        if list(row["forbidden_outcomes"]) != list(scenario["forbidden_outcomes"]):
            issues.append(f"{scenario_id} forbidden_outcomes mismatch between scenario and oracle catalog")
        if bool(row["runtime_detection_target"]) != bool(scenario.get("runtime_detection_target", True)):
            issues.append(f"{scenario_id} runtime_detection_target mismatch between scenario and oracle catalog")
        if dict(row["expected_final_properties"]) != dict(scenario["expected_final_properties"]):
            issues.append(f"{scenario_id} expected_final_properties mismatch between scenario and oracle catalog")

        structural_reason = row["structural_exclusion_reason"]
        if structural_reason is not None:
            structural_rows[scenario_id] = str(structural_reason)
        expected_participation = bool(row["runtime_detection_target"]) and scenario_id not in STRUCTURAL_RUNTIME_EXCLUSIONS
        if bool(row["runtime_f1_participates"]) != expected_participation:
            issues.append(f"{scenario_id} runtime_f1_participates is inconsistent with target/exclusion semantics")

    extra_rows = sorted(set(catalog_by_id) - set(scenarios_by_id))
    if extra_rows:
        issues.append(f"extra scenarios in oracle catalog: {', '.join(extra_rows)}")

    if structural_rows != STRUCTURAL_RUNTIME_EXCLUSIONS:
        issues.append(
            "structural runtime exclusions mismatch: "
            f"catalog={structural_rows} expected={STRUCTURAL_RUNTIME_EXCLUSIONS}"
        )

    report = {
        "scenario_root": ensure_relative(scenario_root),
        "catalog_path": ensure_relative(catalog_path),
        "spec_path": ensure_relative(spec_path),
        "scenarios_total": len(scenarios_by_id),
        "catalog_rows_total": len(catalog_rows),
        "issues": issues,
        "errors": issues,
        "scenario_count": len(scenarios_by_id),
        "ok": not issues,
        "valid": not issues,
    }
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate oracle specification and machine-readable catalog.")
    parser.add_argument("--scenarios", default=str(SCENARIOS_ROOT))
    parser.add_argument("--catalog", default=str(ORACLE_ROOT / "scenario_catalog.json"))
    parser.add_argument("--spec", default=str(REPO_ROOT / "docs" / "oracle_spec.md"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = validate_oracle(
        scenario_root=Path(args.scenarios),
        catalog_path=Path(args.catalog),
        spec_path=Path(args.spec),
    )
    print(report)
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
