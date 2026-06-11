#!/usr/bin/env python3
"""Validate protocol scaffold files, templates, and branch-planning invariants."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from benchmark_constants import (
    AGENT_EXECUTORS,
    EXPECTED_ARM_BRANCH_COUNT,
    EXPECTED_EXPERIMENT_BRANCH_COUNT,
    README_EXECUTION_ORDER,
    REQUIRED_DOCS,
    STATUS_VALUES,
    STEPS,
    TEMPLATE_FILES,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_MANIFEST_KEYS = [
    "step_id",
    "status",
    "agent_executor",
    "prompt_hash",
    "benchmark_spec_hash",
    "commit_sha",
    "arm",
    "strategy",
    "replication",
    "changed_files",
    "changed_file_count",
    "lines_added",
    "lines_deleted",
    "change_spread",
    "test_failures",
    "rework_iterations",
    "contract_violations",
    "traceability_ratio",
    "orphan_artifacts",
    "run_ledger_compliance",
    "capabilities_present",
    "governance_artifacts_present",
]

REQUIRED_LEDGER_KEYS = [
    "run_id",
    "arm",
    "strategy",
    "replication",
    "step_id",
    "agent_executor",
    "started_at",
    "finished_at",
    "status",
    "artifacts",
    "notes",
]


def read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def validate_required_files(errors: list[str]) -> None:
    for relative_path in [*REQUIRED_DOCS, *TEMPLATE_FILES]:
        if not (REPO_ROOT / relative_path).is_file():
            errors.append(f"missing required file: {relative_path}")


def validate_readme_order(errors: list[str]) -> None:
    readme_text = read_text("README_PROTOCOL.md")
    for line in README_EXECUTION_ORDER:
        if line not in readme_text:
            errors.append(f"README_PROTOCOL.md missing execution-order line: {line}")


def validate_prompt_content(errors: list[str]) -> None:
    prompt_text = read_text("PROMPT.md")
    required_snippets = [
        "Read these files before acting:",
        "git branch --show-current",
        "exp/evolutionary/{arm}/{replication}",
        "exp/final-spec/{arm}/{replication}",
        "parts[1] = strategy",
        "parts[2] = arm",
        "parts[3] = replication",
        "agent_executor = codex",
        "If the branch does not match one of the expected formats, stop and report the mismatch.",
        "- `STEP_PROTOCOL.md`",
        "- `ARM_INSTRUCTIONS.md`",
        "implement only the next incomplete step in `IMPLEMENTATION_PLAN.md`",
        "use that step as `step_id`",
        "implement the direct final target for that branch",
        "use `C6` as `step_id` unless `IMPLEMENTATION_PLAN.md` defines a more specific final-spec step id",
        "runs/{strategy}/{arm}/{replication}/{step_id}/manifest.json",
        "`changed_file_count`",
        "normalized `change_spread`",
        "`total_tracked_files = count(git ls-files)` at the pre-step commit",
        "update `IMPLEMENTATION_PLAN.md`",
        "commit after the completed step",
        "- stop",
    ]
    for snippet in required_snippets:
        if snippet not in prompt_text:
            errors.append(f"PROMPT.md missing required text: {snippet}")


def load_json(relative_path: str) -> object:
    with (REPO_ROOT / relative_path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_manifest_template(errors: list[str]) -> None:
    manifest = load_json("templates/manifest.template.json")
    if not isinstance(manifest, dict):
        errors.append("manifest template must be a JSON object")
        return
    missing_keys = [key for key in REQUIRED_MANIFEST_KEYS if key not in manifest]
    if missing_keys:
        errors.append(f"manifest template missing keys: {', '.join(missing_keys)}")
    if manifest.get("step_id") not in STEPS:
        errors.append("manifest template has invalid default step_id")
    if manifest.get("status") not in STATUS_VALUES:
        errors.append("manifest template has invalid default status")
    if manifest.get("agent_executor") not in AGENT_EXECUTORS:
        errors.append("manifest template has invalid default agent_executor")
    if not isinstance(manifest.get("changed_files"), list):
        errors.append("manifest template changed_files must be a list")
    if not isinstance(manifest.get("capabilities_present"), list):
        errors.append("manifest template capabilities_present must be a list")
    if not isinstance(manifest.get("governance_artifacts_present"), list):
        errors.append("manifest template governance_artifacts_present must be a list")
    changed_file_count = manifest.get("changed_file_count")
    if not isinstance(changed_file_count, int) or changed_file_count < 0:
        errors.append("manifest template changed_file_count must be a non-negative integer")
    elif isinstance(manifest.get("changed_files"), list) and changed_file_count != len(
        manifest["changed_files"]
    ):
        errors.append("manifest template changed_file_count must equal len(changed_files)")
    change_spread = manifest.get("change_spread")
    if not isinstance(change_spread, (int, float)):
        errors.append("manifest template change_spread must be numeric")
    elif not 0.0 <= float(change_spread) <= 1.0:
        errors.append("manifest template change_spread must be between 0.0 and 1.0")


def validate_metrics_spec(errors: list[str]) -> None:
    metrics_text = read_text("METRICS_SPEC.md")
    required_snippets = [
        "`changed_file_count`: number of changed files",
        "`change_spread`: `changed_file_count / total_tracked_files`",
        "`runs/{strategy}/{arm}/{replication}/{step_id}/manifest.json`",
        "`total_tracked_files` is the count returned by `git ls-files` at the pre-step commit.",
    ]
    for snippet in required_snippets:
        if snippet not in metrics_text:
            errors.append(f"METRICS_SPEC.md missing required text: {snippet}")


def validate_readme_content(errors: list[str]) -> None:
    readme_text = read_text("README_PROTOCOL.md")
    required_snippets = [
        "- `STEP_PROTOCOL.md`: operational step-by-step execution rules",
        "- `ARM_INSTRUCTIONS.md`: operational implementation rules for each arm",
        "`IMPLEMENTATION_PLAN.md` is trajectory-local.",
        "Divergence across branches is expected and valid.",
        "Do not merge `IMPLEMENTATION_PLAN.md` across experimental branches.",
    ]
    for snippet in required_snippets:
        if snippet not in readme_text:
            errors.append(f"README_PROTOCOL.md missing required text: {snippet}")


def validate_run_ledger_template(errors: list[str]) -> None:
    ledger = load_json("templates/run_ledger.template.json")
    if not isinstance(ledger, dict):
        errors.append("run ledger template must be a JSON object")
        return
    missing_keys = [key for key in REQUIRED_LEDGER_KEYS if key not in ledger]
    if missing_keys:
        errors.append(f"run ledger template missing keys: {', '.join(missing_keys)}")
    if ledger.get("step_id") not in STEPS:
        errors.append("run ledger template has invalid default step_id")
    if ledger.get("status") not in STATUS_VALUES:
        errors.append("run ledger template has invalid default status")
    if ledger.get("agent_executor") not in AGENT_EXECUTORS:
        errors.append("run ledger template has invalid default agent_executor")


def validate_branch_script(errors: list[str]) -> None:
    script_path = REPO_ROOT / "scripts/create_experiment_branches.py"
    result = subprocess.run(
        [sys.executable, str(script_path), "--dry-run"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        errors.append("create_experiment_branches.py --dry-run failed")
        return
    summary = (
        f"SUMMARY arm_branches={EXPECTED_ARM_BRANCH_COUNT} "
        f"experiment_branches={EXPECTED_EXPERIMENT_BRANCH_COUNT}"
    )
    if summary not in result.stdout:
        errors.append("branch dry-run summary did not report expected 4 and 24 counts")


def main() -> int:
    errors: list[str] = []
    validate_required_files(errors)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    validate_readme_order(errors)
    validate_readme_content(errors)
    validate_prompt_content(errors)
    validate_metrics_spec(errors)
    validate_manifest_template(errors)
    validate_run_ledger_template(errors)
    validate_branch_script(errors)

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("Protocol scaffold validation passed.")
    print(
        f"SUMMARY arm_branches={EXPECTED_ARM_BRANCH_COUNT} "
        f"experiment_branches={EXPECTED_EXPERIMENT_BRANCH_COUNT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
