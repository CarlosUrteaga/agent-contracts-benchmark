from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.enforcement.common import MODES, compute_contract_semantic_fingerprint
from tools.enforcement.materialize import materialize
from tools.enforcement.preflight import check_admission, prepare_contracts
from tools.enforcement.run_all import run_matrix
from tools.enforcement.runtime import run_scenario


class CampaignPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        materialize(self.root)
        self.contracts = self.root / "contracts/enforcement"
        self.scenarios = self.root / "benchmark/enforcement/scenarios"
        self.profile = self.root / "benchmark/enforcement/config/model_profiles/mock.yaml"

    def alter_profile(self):
        profile = json.loads(self.profile.read_text())
        profile["max_tokens"] += 1
        self.profile.write_text(json.dumps(profile))

    def test_nominal_admitted_and_intentional_tampering_preserved(self):
        self.assertTrue(check_admission(self.contracts, self.profile)["admitted"])
        for scenario, status in [("S-001", "completed"), ("S-018", "aborted_pre_execution"), ("S-019", "aborted_pre_execution")]:
            with self.subTest(scenario=scenario):
                result = run_scenario(
                    next(self.scenarios.glob(f"{scenario}.*.json")),
                    self.contracts / "strict.yaml", self.profile, "rep01", self.root / scenario,
                )
                self.assertEqual(status, result["final_status"])

    def test_changed_profile_stops_before_calls_or_force_rerun_deletion(self):
        self.alter_profile()
        history = self.root / "history"
        history.mkdir()
        sentinel = history / "preserve.txt"
        sentinel.write_text("historical evidence")
        for dry_run in [False, True]:
            with self.subTest(dry_run=dry_run), patch("tools.enforcement.run_all.run_scenario") as run:
                with self.assertRaisesRegex(ValueError, "Campaign preflight failed"):
                    run_matrix(
                        scenarios_root=self.scenarios, contracts_root=self.contracts,
                        model_profile_path=self.profile, replications=1,
                        out_root=history, dry_run=dry_run, force_rerun=True,
                    )
                run.assert_not_called()
                self.assertEqual("historical evidence", sentinel.read_text())

    def test_separate_compatibility_copy_preserves_source_and_semantics(self):
        self.alter_profile()
        originals = {mode: (self.contracts / f"{mode}.yaml").read_bytes() for mode in MODES}
        target = self.root / "compatible"
        reports = prepare_contracts(self.contracts, [self.profile], target)
        self.assertTrue(reports[0]["admitted"])
        for mode in MODES:
            self.assertEqual(originals[mode], (self.contracts / f"{mode}.yaml").read_bytes())
            self.assertEqual(
                compute_contract_semantic_fingerprint(json.loads(originals[mode])),
                compute_contract_semantic_fingerprint(json.loads((target / f"{mode}.yaml").read_text())),
            )
        with self.assertRaisesRegex(ValueError, "Refusing to overwrite"):
            prepare_contracts(self.contracts, [self.profile], target)

    def test_stale_contract_content_fingerprint_is_rejected(self):
        path = self.contracts / "guarded.yaml"
        contract = json.loads(path.read_text())
        contract["memory_policy"] = "changed-without-updating-fingerprint"
        path.write_text(json.dumps(contract))
        report = check_admission(self.contracts, self.profile)
        self.assertFalse(report["admitted"])
        self.assertIn("contract.content_fingerprint_mismatch", report["modes"]["guarded"]["problems"])


if __name__ == "__main__":
    unittest.main()
