from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.governor.core import summarize_results, validate_manifest_against_contract
from tools.violation_injection.generate import MUTATIONS

REPO_ROOT = Path(__file__).resolve().parents[1]


def manifest_path(strategy: str, arm: str, replication: str, step: str) -> Path:
    return REPO_ROOT / "benchmark" / "manifests" / strategy / arm / replication / step / "manifest.json"


def contract_path(arm: str) -> Path:
    return REPO_ROOT / "contracts" / f"{arm.replace('-', '_')}.yaml"


class ContractBenchmarkTests(unittest.TestCase):
    def isolated_step_dir(self, strategy: str, arm: str, replication: str, step: str) -> Path:
        temp_root = Path(tempfile.mkdtemp(prefix="contract-benchmark-"))
        source_dir = manifest_path(strategy, arm, replication, step).parent
        target_dir = temp_root / step
        shutil.copytree(source_dir, target_dir)
        self.addCleanup(shutil.rmtree, temp_root, ignore_errors=True)
        return target_dir

    def test_valid_base_manifest_passes_base_contract(self) -> None:
        result = validate_manifest_against_contract(
            manifest_path("evolutionary", "base", "rep01", "C1"),
            contract_path("base"),
        )
        self.assertEqual("pass", result["verdict"])

    def test_valid_contract_first_manifest_passes_contract_first_contract(self) -> None:
        result = validate_manifest_against_contract(
            manifest_path("evolutionary", "contract-first", "rep01", "C1"),
            contract_path("contract-first"),
        )
        self.assertEqual("pass", result["verdict"])

    def test_contract_first_manifest_without_contracts_md_fails(self) -> None:
        step_dir = self.isolated_step_dir("evolutionary", "contract-first", "rep01", "C1")
        (step_dir / "CONTRACTS.md").unlink()
        result = validate_manifest_against_contract(step_dir / "manifest.json", contract_path("contract-first"))
        self.assertEqual("fail", result["verdict"])
        self.assertTrue(any(item["rule_id"] == "contracts.file_required" for item in result["violations"]))

    def test_contract_flow_manifest_without_workflow_md_fails(self) -> None:
        step_dir = self.isolated_step_dir("evolutionary", "contract-flow", "rep01", "C1")
        (step_dir / "WORKFLOW.md").unlink()
        result = validate_manifest_against_contract(step_dir / "manifest.json", contract_path("contract-flow"))
        self.assertEqual("fail", result["verdict"])
        self.assertTrue(any(item["rule_id"] == "workflow.file_required" for item in result["violations"]))

    def test_c6_manifest_without_run_ledger_fails(self) -> None:
        step_dir = self.isolated_step_dir("evolutionary", "base", "rep01", "C6")
        (step_dir / "run_ledger.json").unlink()
        result = validate_manifest_against_contract(step_dir / "manifest.json", contract_path("base"))
        self.assertEqual("fail", result["verdict"])
        self.assertTrue(any(item["rule_id"] == "ledger.artifact_exists" for item in result["violations"]))

    def test_nonzero_contract_violations_fails(self) -> None:
        step_dir = self.isolated_step_dir("evolutionary", "base", "rep01", "C2")
        manifest = step_dir / "manifest.json"
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        payload["contract_violations"] = 1
        manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        result = validate_manifest_against_contract(manifest, contract_path("base"))
        self.assertEqual("fail", result["verdict"])
        self.assertTrue(any(item["rule_id"] == "contracts.zero_violations" for item in result["violations"]))

    def test_traceability_ratio_not_one_fails(self) -> None:
        step_dir = self.isolated_step_dir("evolutionary", "base", "rep01", "C3")
        manifest = step_dir / "manifest.json"
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        payload["traceability_ratio"] = 0.5
        manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        result = validate_manifest_against_contract(manifest, contract_path("base"))
        self.assertEqual("fail", result["verdict"])
        self.assertTrue(any(item["rule_id"] == "traceability.perfect" for item in result["violations"]))

    def test_violation_injection_metadata_contract(self) -> None:
        required = {
            "missing_required_artifact",
            "missing_run_ledger",
            "wrong_traceability_ratio",
            "nonzero_contract_violations",
            "nonzero_test_failures",
            "missing_contracts_md",
            "missing_workflow_md",
            "capability_present_but_not_declared",
            "inconsistent_arm_contract",
            "fingerprint_mismatch",
        }
        self.assertEqual(required, set(MUTATIONS))

    def test_evaluation_metrics_are_computed_correctly(self) -> None:
        summary = summarize_results(
            [
                {"arm": "base", "verdict": "pass", "validation_latency_ms": 1.0},
                {"arm": "base", "verdict": "fail", "validation_latency_ms": 2.0},
                {"arm": "contract-first", "verdict": "pass", "validation_latency_ms": 3.0},
            ]
        )
        self.assertEqual(3, summary["total_manifests"])
        self.assertEqual(2, summary["pass_count"])
        self.assertEqual(1, summary["fail_count"])
        self.assertEqual(0.5, summary["compliance_rate_by_arm"]["base"])
        self.assertEqual(1.0, summary["compliance_rate_by_arm"]["contract-first"])


if __name__ == "__main__":
    unittest.main()
