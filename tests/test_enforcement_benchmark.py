from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.enforcement.evaluate import evaluate_runs
from tools.enforcement.materialize import materialize
from tools.enforcement.runtime import run_scenario

REPO_ROOT = Path(__file__).resolve().parents[1]


class EnforcementBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        materialize(REPO_ROOT)

    def temp_dir(self) -> Path:
        root = Path(tempfile.mkdtemp(prefix="llm-enforcement-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        return root

    def scenario_path(self, scenario_id: str) -> Path:
        return next((REPO_ROOT / "benchmark" / "enforcement" / "scenarios").glob(f"{scenario_id}.*.json"))

    def contract_path(self, mode: str) -> Path:
        return REPO_ROOT / "contracts" / "enforcement" / f"{mode}.yaml"

    def model_profile_path(self) -> Path:
        return REPO_ROOT / "benchmark" / "enforcement" / "config" / "model_profiles" / "mock.yaml"

    def run_case(self, scenario_id: str, mode: str, replication_id: str = "rep01") -> dict[str, object]:
        out_dir = self.temp_dir() / "runs" / mode / scenario_id
        return run_scenario(
            self.scenario_path(scenario_id),
            self.contract_path(mode),
            self.model_profile_path(),
            replication_id,
            out_dir,
        )

    def test_materialize_rewrites_scenarios_with_nominal_and_adversarial_schema(self) -> None:
        scenario = json.loads(self.scenario_path("S-011").read_text(encoding="utf-8"))
        self.assertEqual("adversarial", scenario["scenario_type"])
        self.assertIn("acceptable_outcomes", scenario)
        self.assertIn("forbidden_outcomes", scenario)
        self.assertNotIn("attempted_actions", scenario)

    def test_guarded_blocks_and_replans_in_ticket_without_evidence(self) -> None:
        summary = self.run_case("S-011", "guarded")
        self.assertEqual("completed_after_replan", summary["final_status"])
        self.assertTrue(summary["actions_blocked"])
        self.assertTrue(summary["violation_opportunity_observed"])
        self.assertTrue(summary["acceptable_outcome_satisfied"])

    def test_strict_aborts_pre_execution_for_tampered_agent(self) -> None:
        summary = self.run_case("S-018", "strict")
        self.assertEqual("aborted_pre_execution", summary["final_status"])
        self.assertFalse(summary["side_effects_committed"])
        self.assertEqual("violation_detected", summary["validation_phases"]["pre_execution"])

    def test_strict_rejects_missing_ledger_in_post_execution(self) -> None:
        summary = self.run_case("S-017", "strict")
        self.assertEqual("failed_post_execution", summary["final_status"])
        self.assertFalse(summary["side_effects_committed"])
        self.assertEqual("violation_detected", summary["validation_phases"]["post_execution"])

    def test_no_contract_detection_metrics_are_null(self) -> None:
        runs_root = self.temp_dir() / "runs"
        for scenario_id in ["S-001", "S-011"]:
            run_scenario(
                self.scenario_path(scenario_id),
                self.contract_path("no_contract"),
                self.model_profile_path(),
                "rep01",
                runs_root / "mock-pilot" / "no_contract" / "rep01" / scenario_id,
            )
        summary = evaluate_runs(runs_root)
        self.assertIsNone(summary["per_mode"]["no_contract"]["precision"])
        self.assertIsNone(summary["per_mode"]["no_contract"]["recall"])
        self.assertIsNone(summary["per_mode"]["no_contract"]["f1"])

    def test_violation_opportunity_observed_requires_risky_proposal(self) -> None:
        guarded = self.run_case("S-011", "guarded")
        nominal = self.run_case("S-001", "guarded")
        self.assertTrue(guarded["violation_opportunity_observed"])
        self.assertFalse(nominal["violation_opportunity_observed"])

    def test_trace_ordering_has_proposal_before_validation_and_execution(self) -> None:
        out_dir = self.temp_dir() / "run"
        run_scenario(
            self.scenario_path("S-001"),
            self.contract_path("guarded"),
            self.model_profile_path(),
            "rep01",
            out_dir,
        )
        events = [json.loads(line) for line in (out_dir / "trace.jsonl").read_text(encoding="utf-8").splitlines()]
        proposed = next(i for i, row in enumerate(events) if row["event"] == "action_proposed")
        validated = next(i for i, row in enumerate(events) if row["event"] == "action_validated")
        executed = next(i for i, row in enumerate(events) if row["event"] == "action_executed")
        self.assertLess(proposed, validated)
        self.assertLess(validated, executed)

    def test_run_all_supports_replications_and_dry_run(self) -> None:
        out_root = self.temp_dir() / "runs"
        dry_run = subprocess.run(
            [
                "python3",
                "-m",
                "tools.enforcement.run_all",
                "--scenarios",
                "benchmark/enforcement/scenarios",
                "--contracts",
                "contracts/enforcement",
                "--model-profile",
                "benchmark/enforcement/config/model_profiles/mock.yaml",
                "--replications",
                "1",
                "--dry-run",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, dry_run.returncode, dry_run.stderr)
        result = subprocess.run(
            [
                "python3",
                "-m",
                "tools.enforcement.run_all",
                "--scenarios",
                "benchmark/enforcement/scenarios",
                "--contracts",
                "contracts/enforcement",
                "--model-profile",
                "benchmark/enforcement/config/model_profiles/mock.yaml",
                "--replications",
                "1",
                "--out",
                str(out_root),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        summaries = list(out_root.glob("**/summary.json"))
        self.assertEqual(84, len(summaries))


if __name__ == "__main__":
    unittest.main()
