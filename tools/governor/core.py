"""Core contract validation logic."""

from __future__ import annotations

import json
import statistics
import time
from pathlib import Path
from typing import Any

from .common import (
    MANIFEST_FINGERPRINT_FILE,
    REQUIRED_MANIFEST_FIELDS,
    RUN_LEDGER_FILE,
    first_step_for_strategy,
    json_fingerprint,
    load_yaml_or_json,
    manifest_content_for_fingerprint,
    manifest_step,
)


def _violation(
    rule_id: str,
    severity: str,
    message: str,
    expected: Any,
    observed: Any,
) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "severity": severity,
        "message": message,
        "expected": expected,
        "observed": observed,
    }


def _artifact_exists(manifest_path: Path, artifact_name: str) -> bool:
    return (manifest_path.parent / artifact_name).is_file()


def _check_manifest_structure(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in manifest:
            violations.append(
                _violation(
                    "manifest.required_field",
                    "high",
                    f"manifest field {field} is required",
                    "present",
                    "missing",
                )
            )
    changed_files = manifest.get("changed_files")
    if "changed_files" in manifest and not isinstance(changed_files, list):
        violations.append(
            _violation(
                "manifest.changed_files_type",
                "high",
                "changed_files must be a list",
                "list",
                type(changed_files).__name__,
            )
        )
    changed_file_count = manifest.get("changed_file_count")
    if isinstance(changed_files, list) and changed_file_count != len(changed_files):
        violations.append(
            _violation(
                "manifest.changed_file_count",
                "high",
                "changed_file_count must equal len(changed_files)",
                len(changed_files),
                changed_file_count,
            )
        )
    return violations


def _check_recorded_fingerprint(manifest_path: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    fingerprint_path = manifest_path.parent / MANIFEST_FINGERPRINT_FILE
    if not fingerprint_path.is_file():
        return []
    expected = json_fingerprint(manifest_content_for_fingerprint(manifest))
    observed = fingerprint_path.read_text(encoding="utf-8").strip()
    if expected == observed:
        return []
    return [
        _violation(
            "manifest.fingerprint_match",
            "high",
            "recorded fingerprint does not match manifest contents",
            expected,
            observed,
        )
    ]


def _check_rule(
    rule: dict[str, Any],
    contract: dict[str, Any],
    manifest: dict[str, Any],
    manifest_path: Path,
) -> list[dict[str, Any]]:
    step = manifest_step(manifest)
    rule_id = str(rule["rule_id"])
    severity = str(rule.get("severity", "medium"))
    kind = str(rule["kind"])
    violations: list[dict[str, Any]] = []

    if kind == "file_exists":
        artifact = str(rule["artifact"])
        if not _artifact_exists(manifest_path, artifact):
            violations.append(
                _violation(rule_id, severity, f"required artifact {artifact} is missing", "file exists", "missing")
            )
    elif kind == "field_equals":
        field = str(rule["field"])
        expected = rule["expected"]
        observed = manifest.get(field)
        if observed != expected:
            violations.append(
                _violation(rule_id, severity, f"{field} must equal {expected!r}", expected, observed)
            )
    elif kind == "step_field_equals":
        target_step = str(rule["step"])
        if step == target_step:
            field = str(rule["field"])
            expected = rule["expected"]
            observed = manifest.get(field)
            if observed != expected:
                violations.append(
                    _violation(
                        rule_id,
                        severity,
                        f"{field} must equal {expected!r} at {target_step}",
                        expected,
                        observed,
                    )
                )
    elif kind == "step_changed_files_include":
        target_step = str(rule["step"])
        if step == target_step:
            expected_file = str(rule["artifact"])
            changed_files = manifest.get("changed_files", [])
            if expected_file not in changed_files:
                violations.append(
                    _violation(
                        rule_id,
                        severity,
                        f"changed_files must include {expected_file} at {target_step}",
                        expected_file,
                        changed_files,
                    )
                )
    elif kind == "governed_capability_introduction_changed_files_include":
        expected_file = str(rule["artifact"])
        strategy = str(manifest.get("strategy"))
        if step == first_step_for_strategy(strategy):
            changed_files = manifest.get("changed_files", [])
            if expected_file not in changed_files:
                violations.append(
                    _violation(
                        rule_id,
                        severity,
                        f"changed_files must include {expected_file} at the first step of {strategy}",
                        expected_file,
                        changed_files,
                    )
                )
    elif kind == "field_contains":
        field = str(rule["field"])
        expected = rule["expected"]
        observed = manifest.get(field, [])
        if expected not in observed:
            violations.append(
                _violation(
                    rule_id,
                    severity,
                    f"{field} must include {expected!r}",
                    expected,
                    observed,
                )
            )
    elif kind == "consistent_arm_contract":
        expected_arm = contract["applies_to_arm"]
        observed = manifest.get("arm")
        if observed != expected_arm:
            violations.append(
                _violation(
                    rule_id,
                    severity,
                    "manifest arm does not match contract arm",
                    expected_arm,
                    observed,
                )
            )
    elif kind == "capability_declared":
        capability = str(rule["capability"])
        changed_files = manifest.get("changed_files", [])
        observed_capabilities = manifest.get("capabilities_present", [])
        if capability in changed_files and capability not in observed_capabilities:
            violations.append(
                _violation(
                    rule_id,
                    severity,
                    "capability-related change is present but capability is not declared",
                    f"{capability} in capabilities_present",
                    observed_capabilities,
                )
            )
    elif kind == "ledger_required_when_flagged":
        if manifest.get("run_ledger_compliance") and not _artifact_exists(manifest_path, RUN_LEDGER_FILE):
            violations.append(
                _violation(
                    rule_id,
                    severity,
                    "run_ledger_compliance=true requires a run_ledger.json artifact",
                    "run_ledger.json exists",
                    "missing",
                )
            )
    else:
        raise ValueError(f"unsupported rule kind: {kind}")
    return violations


def validate_manifest_against_contract(
    manifest_path: Path,
    contract_path: Path,
) -> dict[str, Any]:
    started = time.perf_counter()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    contract = load_yaml_or_json(contract_path)

    violations = _check_manifest_structure(manifest)
    violations.extend(_check_recorded_fingerprint(manifest_path, manifest))
    for rule in contract.get("violation_rules", []):
        violations.extend(_check_rule(rule, contract, manifest, manifest_path))

    elapsed_ms = (time.perf_counter() - started) * 1000.0
    result = {
        "manifest_path": str(manifest_path),
        "contract_id": contract["contract_id"],
        "arm": manifest.get("arm"),
        "strategy": manifest.get("strategy"),
        "replication": manifest.get("replication"),
        "step": manifest_step(manifest),
        "verdict": "pass" if not violations else "fail",
        "violations": violations,
        "fingerprint": json_fingerprint(
            {
                "manifest": manifest_content_for_fingerprint(manifest),
                "contract_id": contract["contract_id"],
                "verdict": "pass" if not violations else "fail",
                "violations": violations,
            }
        ),
        "validation_latency_ms": round(elapsed_ms, 6),
    }
    return result


def summarize_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    latencies = [float(result["validation_latency_ms"]) for result in results]
    arm_counts: dict[str, dict[str, int]] = {}
    for result in results:
        arm = str(result["arm"])
        bucket = arm_counts.setdefault(arm, {"total": 0, "pass": 0})
        bucket["total"] += 1
        if result["verdict"] == "pass":
            bucket["pass"] += 1

    compliance_rate_by_arm = {
        arm: round(counts["pass"] / counts["total"], 4) if counts["total"] else 0.0
        for arm, counts in arm_counts.items()
    }
    quantiles = statistics.quantiles(latencies, n=100, method="inclusive") if len(latencies) > 1 else latencies
    p95 = quantiles[94] if len(latencies) > 1 else (latencies[0] if latencies else 0.0)
    return {
        "total_manifests": len(results),
        "pass_count": sum(1 for result in results if result["verdict"] == "pass"),
        "fail_count": sum(1 for result in results if result["verdict"] == "fail"),
        "compliance_rate_by_arm": compliance_rate_by_arm,
        "median_latency_ms": round(statistics.median(latencies), 6) if latencies else 0.0,
        "p95_latency_ms": round(p95, 6),
        "max_latency_ms": round(max(latencies), 6) if latencies else 0.0,
    }
