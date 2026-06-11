from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


class ReconstructionScaffoldTests(unittest.TestCase):
    def temp_dir(self) -> Path:
        root = Path(tempfile.mkdtemp(prefix="reconstruction-scaffold-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        return root

    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", *args],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_aggregate_manifests_reports_expected_counts(self) -> None:
        out_root = self.temp_dir()
        result = self.run_script("scripts/aggregate_manifests.py", "--runs", "benchmark/manifests", "--out", str(out_root))
        self.assertEqual(0, result.returncode, result.stderr)
        qc = json.loads((out_root / "qc_report.json").read_text(encoding="utf-8"))
        self.assertEqual(84, qc["total_manifests"])
        self.assertEqual(24, qc["trajectory_count"])

    def test_reconstruction_generation_creates_72_cases(self) -> None:
        case_root = self.temp_dir() / "reconstruction"
        audit_root = self.temp_dir() / "audit"
        oracle_root = self.temp_dir() / "oracle"
        result = self.run_script(
            "scripts/create_reconstruction_branches.py",
            "--source",
            "benchmark/manifests",
            "--out",
            str(case_root),
            "--audit-root",
            str(audit_root),
            "--oracle-root",
            str(oracle_root),
            "--apply",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        case_count = sum(1 for path in case_root.glob("*/*/*/*") if path.is_dir())
        self.assertEqual(72, case_count)

    def test_reconstruction_validator_rejects_missing_manifest(self) -> None:
        case_root = self.temp_dir() / "reconstruction"
        audit_root = self.temp_dir() / "audit"
        oracle_root = self.temp_dir() / "oracle"
        create = self.run_script(
            "scripts/create_reconstruction_branches.py",
            "--source",
            "benchmark/manifests",
            "--out",
            str(case_root),
            "--audit-root",
            str(audit_root),
            "--oracle-root",
            str(oracle_root),
            "--apply",
        )
        self.assertEqual(0, create.returncode, create.stderr)
        first_manifest = next(case_root.glob("*/*/*/*/evidence/manifest.json"))
        first_manifest.unlink()
        validate = self.run_script("scripts/validate_reconstruction_branches.py", "--root", str(case_root))
        self.assertNotEqual(0, validate.returncode)

    def test_reconstruction_scorer_computes_exact_match_rate(self) -> None:
        case_root = self.temp_dir() / "reconstruction"
        audit_root = self.temp_dir() / "audit"
        oracle_root = self.temp_dir() / "oracle"
        out_path = self.temp_dir() / "reconstruction_summary.json"
        create = self.run_script(
            "scripts/create_reconstruction_branches.py",
            "--source",
            "benchmark/manifests",
            "--out",
            str(case_root),
            "--audit-root",
            str(audit_root),
            "--oracle-root",
            str(oracle_root),
            "--apply",
        )
        self.assertEqual(0, create.returncode, create.stderr)
        score = self.run_script(
            "scripts/score_reconstruction_audits.py",
            "--audit-root",
            str(audit_root),
            "--oracle",
            str(oracle_root / "trajectory_oracles.json"),
            "--out",
            str(out_path),
        )
        self.assertEqual(0, score.returncode, score.stderr)
        summary = json.loads(out_path.read_text(encoding="utf-8"))
        self.assertEqual(72, summary["total_audits"])
        self.assertEqual(1.0, summary["exact_match_rate"])


if __name__ == "__main__":
    unittest.main()
