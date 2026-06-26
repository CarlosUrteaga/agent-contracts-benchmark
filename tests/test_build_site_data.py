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
        self.assertEqual(data["campaign_count"], 19)
        self.assertEqual(len(data["modes"]), 4)
        self.assertEqual(data["benchmark_version"], "benchmark-v1.0")

        rows = data["campaign_rows"]
        self.assertEqual(len(rows), 19 * 4)

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

            json_path = out_dir / "data/canonical_results.json"
            payload = json.loads(json_path.read_text())
            self.assertEqual(payload["campaign_count"], 19)
            self.assertEqual(len(payload["artifacts"]), 6)

            for rel_path in [
                "_includes/generated/overview_metrics.md",
                "_includes/generated/table_base_r5.md",
                "_includes/generated/table_guarded_backends.md",
                "_includes/generated/table_overhead.md",
                "_includes/generated/artifact_links.md",
                "assets/generated/base-r5-modes.svg",
                "assets/generated/guarded-backends.svg",
                "assets/generated/guarded-vs-strict.svg",
            ]:
                self.assertTrue((out_dir / rel_path).exists(), rel_path)

            artifact_names = sorted(path.name for path in (out_dir / "assets/artifacts").iterdir())
            self.assertNotIn("114.tex", artifact_names)
            self.assertFalse(any("smoke-" in name for name in artifact_names))


if __name__ == "__main__":
    unittest.main()
