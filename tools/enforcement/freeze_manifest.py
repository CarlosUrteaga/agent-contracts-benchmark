"""Generate a reproducible manifest for the frozen enforcement benchmark."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

from .common import BENCHMARK_ROOT, CONTRACTS_ROOT, REPO_ROOT, write_json


def _sha256_bytes(parts: Iterable[bytes]) -> str:
    hasher = hashlib.sha256()
    for part in parts:
        hasher.update(part)
    return f"sha256:{hasher.hexdigest()}"


def _hash_files(paths: list[Path]) -> str:
    chunks: list[bytes] = []
    for path in sorted(paths):
        rel = path.relative_to(REPO_ROOT).as_posix().encode("utf-8")
        chunks.append(rel + b"\n")
        chunks.append(path.read_bytes())
        chunks.append(b"\n")
    return _sha256_bytes(chunks)


def _git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def build_manifest() -> dict[str, object]:
    scenario_paths = sorted((BENCHMARK_ROOT / "scenarios").glob("S-*.json"))
    contract_paths = sorted(CONTRACTS_ROOT.glob("*.yaml"))
    oracle_paths = sorted(
        [
            REPO_ROOT / "docs" / "oracle_spec.md",
            BENCHMARK_ROOT / "oracle" / "scenario_catalog.json",
        ]
    )
    evaluator_paths = [REPO_ROOT / "tools" / "enforcement" / "evaluate.py"]
    diagnose_paths = [REPO_ROOT / "tools" / "enforcement" / "diagnose_f1.py"]

    return {
        "benchmark_version": "v1.0-pre-freeze",
        "freeze_commit": _git_head(),
        "generated_at": datetime.now(UTC).isoformat(),
        "frozen_artifacts": {
            "scenarios_hash": _hash_files(scenario_paths),
            "contracts_hash": _hash_files(contract_paths),
            "oracle_hash": _hash_files(oracle_paths),
            "evaluator_hash": _hash_files(evaluator_paths),
            "diagnose_f1_hash": _hash_files(diagnose_paths),
        },
        "notes": [
            "This manifest identifies the current benchmark-only freeze candidate.",
            "Model profiles are execution conditions and are not part of the benchmark identity.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the frozen enforcement benchmark manifest.")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_json(Path(args.out), build_manifest())
    print(f"Wrote benchmark freeze manifest to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
