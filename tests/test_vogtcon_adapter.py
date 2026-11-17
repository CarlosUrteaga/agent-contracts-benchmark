# Copyright (c) 2026 Jorge Carlos Urteaga Reyesvera
# SPDX-License-Identifier: Apache-2.0

"""Integration checks for the benchmark's installed vogtcon dependency."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import vogtcon

from tools.enforcement import runtime
from tools.enforcement.compare_migration import compare_campaigns
from tools.enforcement.vogtcon_adapter import VogtconRunAdapter


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts" / "enforcement"


class VogtconAdapterTests(unittest.TestCase):
    def test_campaign_comparison_ignores_time_but_detects_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            baseline = Path(directory) / "baseline"
            candidate = Path(directory) / "candidate"
            for root, latency, completed_at in ((baseline, 1.0, 1), (candidate, 2.0, 2)):
                run = root / "mock" / "strict" / "rep01" / "S-001"
                run.mkdir(parents=True)
                (run / "summary.json").write_text(json.dumps({"final_status": "completed", "total_latency_ms": latency}))
                (run / "trace.jsonl").write_text('{"event":"run_finished"}\n')
                (run / "run_ledger.json").write_text('{"actions":[]}')
                (run / "run_complete.json").write_text(json.dumps({"completed_at": completed_at}))
            self.assertEqual(compare_campaigns(baseline, candidate), [])
            (candidate / "mock" / "strict" / "rep01" / "S-001" / "trace.jsonl").write_text(
                '{"event":"action_blocked"}\n'
            )
            self.assertEqual(
                compare_campaigns(baseline, candidate),
                ["artifact differs: mock/strict/rep01/S-001/trace.jsonl"],
            )

    def test_contracts_load_from_installed_package(self) -> None:
        package_path = Path(vogtcon.__file__).resolve()
        self.assertIn("site-packages", package_path.parts)
        self.assertFalse(package_path.is_relative_to(ROOT / "integrations"))
        for mode in ("no_contract", "advisory", "guarded", "strict"):
            with self.subTest(mode=mode):
                adapter = VogtconRunAdapter(CONTRACTS / f"{mode}.yaml", mode=mode)
                self.assertEqual(adapter.contract.contract_id, f"enforcement.{mode}.v2")

    def test_runtime_gate_controls_tool_invocation_in_all_modes(self) -> None:
        for mode, expected_decision, should_execute in (
            ("no_contract", "allow", True),
            ("advisory", "allow_with_warning", True),
            ("guarded", "block", False),
            ("strict", "abort", False),
        ):
            with self.subTest(mode=mode):
                adapter = VogtconRunAdapter(CONTRACTS / f"{mode}.yaml", mode=mode)
                calls: list[dict[str, object]] = []
                outcome = adapter.execute_tool(
                    action={"tool_name": "create_ticket", "arguments": {}},
                    state={"tickets": [], "memory": [], "notifications": []},
                    available_tools=["create_ticket"],
                    tool_fn=lambda arguments: calls.append(arguments) or {"created": True},
                )
                self.assertEqual(outcome.decision, expected_decision)
                self.assertEqual(outcome.executed, should_execute)
                self.assertEqual(len(calls), int(should_execute))
                self.assertEqual(
                    [item["rule"] for item in outcome.violations],
                    [] if mode == "no_contract" else ["ticket_requires_evidence"],
                )

    def test_pre_post_and_tool_errors_preserve_contract_semantics(self) -> None:
        adapter = VogtconRunAdapter(CONTRACTS / "strict.yaml", mode="strict")
        pre, _ = adapter.validate_pre("sha256:unknown", "sha256:unknown")
        self.assertEqual(
            [item["rule"] for item in pre],
            ["agent.configuration_fingerprint_match", "contract.fingerprint_match"],
        )
        post, _ = adapter.validate_post({}, None, {}, [])
        self.assertEqual(
            [item["rule"] for item in post],
            ["response.schema_complete", "run_ledger.required"],
        )
        with self.assertRaisesRegex(RuntimeError, "tool failed"):
            adapter.execute_tool(
                action={"tool_name": "search_policy", "arguments": {}},
                state={},
                available_tools=["search_policy"],
                tool_fn=lambda arguments: (_ for _ in ()).throw(RuntimeError("tool failed")),
            )

    def test_new_runner_path_does_not_instantiate_historical_governor(self) -> None:
        scenario = next((ROOT / "benchmark" / "enforcement" / "scenarios").glob("S-001*.json"))
        profile = ROOT / "benchmark" / "enforcement" / "config" / "model_profiles" / "mock.yaml"
        with tempfile.TemporaryDirectory() as directory, patch.object(
            runtime, "GovernorRuntime", side_effect=AssertionError("historical governor used")
        ):
            summary = runtime.run_scenario(
                scenario, CONTRACTS / "strict.yaml", profile, "rep01", Path(directory)
            )
        self.assertEqual(summary["final_status"], "completed")


if __name__ == "__main__":
    unittest.main()
