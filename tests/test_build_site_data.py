from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts/build_site_data.py"


def load_module():
    spec = importlib.util.spec_from_file_location("build_site_data", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class BuildSiteDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def test_build_site_data_uses_canonical_artifact(self):
        data = self.module.build_site_data(self.module.DEFAULT_STATS)
        self.assertEqual(data["campaign_count"], 26)
        self.assertEqual(data["comparison_campaign_count"], 23)
        self.assertEqual(data["comparison_run_count"], 6972)
        self.assertEqual(data["inventory_run_count"], 7728)
        self.assertEqual(data["canonical_cut_date"], "2026-09-12")
        self.assertEqual(len(data["modes"]), 4)
        self.assertEqual(data["benchmark_version"], "benchmark-v1.0")

        rows = data["campaign_rows"]
        self.assertEqual(len(rows), 23 * 4)
        excluded = {row["campaign_id"] for row in data["dashboard_campaigns"] if row["admission_issue"]}
        for key in ("campaign_rows", "guarded_backend_rows", "overhead_rows"):
            self.assertFalse(excluded & {row["campaign_id"] for row in data[key]})

        base_guarded = next(
            row for row in rows if row["campaign_id"] == "campaign-base-r5" and row["mode"] == "guarded"
        )
        self.assertAlmostEqual(
            base_guarded["successful_safe_completion_rate"]["estimate"], 0.904762, places=6
        )
        self.assertAlmostEqual(base_guarded["unsafe_side_effect_rate"]["estimate"], 0.0, places=6)
        self.assertAlmostEqual(base_guarded["f1"]["estimate"], 0.789474, places=6)

    def test_main_writes_expected_public_outputs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            data = self.module.build_site_data(self.module.DEFAULT_STATS)
            data["artifacts"] = self.module.copy_public_artifacts(out_dir)
            self.module.write_json(data, out_dir)
            self.module.write_markdown_fragments(data, out_dir)
            self.module.write_svgs(data, out_dir)

            json_path = out_dir / "src/data/canonical_results.json"
            payload = json.loads(json_path.read_text())
            self.assertEqual(payload["campaign_count"], 26)
            self.assertEqual(len(payload["artifacts"]), 20)
            self.assertTrue(any(x["label"] == "benchmark_identity_audit.md" for x in payload["artifacts"]))

            for rel_path in [
                "_generated/legacy_markdown/overview_metrics.md",
                "_generated/legacy_markdown/table_base_r5.md",
                "_generated/legacy_markdown/table_guarded_backends.md",
                "_generated/legacy_markdown/table_overhead.md",
                "_generated/legacy_markdown/artifact_links.md",
                "_generated/legacy_markdown/reference_sections.md",
                "public/assets/generated/base-r5-modes.svg",
                "public/assets/generated/guarded-backends.svg",
                "public/assets/generated/guarded-vs-strict.svg",
            ]:
                self.assertTrue((out_dir / rel_path).exists(), rel_path)

            artifact_names = sorted(path.name for path in (out_dir / "public/assets/artifacts").iterdir())
            self.assertNotIn("114.tex", artifact_names)
            self.assertFalse(any("smoke-" in name for name in artifact_names))

    def test_dashboard_uses_recorded_dates_and_flags_unexpected_admission(self):
        data = self.module.build_site_data(self.module.DEFAULT_STATS)
        campaigns = data["dashboard_campaigns"]
        self.assertEqual(26, len(campaigns))
        flagged = {row["campaign_id"] for row in campaigns if row["admission_issue"]}
        self.assertEqual({
            "campaign-gemma4-r3", "campaign-openai-gpt56-terra-medium-r3",
            "campaign-openai-gpt6-astra-max-r3",
        }, flagged)
        astra = next(row for row in campaigns if row["model_id"] == "gpt-6-astra")
        self.assertEqual(30, astra["nominal_pre_execution_aborts"])
        opus = next(row for row in campaigns if row["model_id"] == "claude-opus-5")
        self.assertFalse(opus["admission_issue"])
        self.assertEqual("2026-09-12T03:59:58.032555+00:00", opus["closed_at"])
        raw = json.loads(self.module.DEFAULT_STATS.read_text())
        original = next(row for row in raw["campaign_reports"] if row["model_id"] == "claude-opus-5")
        self.assertEqual(original["per_mode_statistics"], opus["statistics"])
        self.assertIsNone(opus["statistics"]["guarded"]["unsafe_side_effect_rate"]["estimate"])


if __name__ == "__main__":
    unittest.main()
