#!/usr/bin/env python3
"""Validate filesystem reconstruction cases."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="benchmark/reconstruction")
    args = parser.parse_args()

    root = Path(args.root)
    case_dirs = sorted(path for path in root.glob("*/*/*/*") if path.is_dir())
    errors: list[str] = []

    for case_dir in case_dirs:
        metadata_path = case_dir / "metadata.json"
        evidence_root = case_dir / "evidence"
        manifest_path = evidence_root / "manifest.json"
        if not metadata_path.is_file():
            errors.append(f"missing metadata: {metadata_path}")
            continue
        if not manifest_path.is_file():
            errors.append(f"missing evidence manifest: {manifest_path}")
            continue
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        expected_files = set(metadata["evidence_files"]) | {"metadata.json"}
        observed_files = {
            str(path.relative_to(case_dir)) for path in case_dir.rglob("*") if path.is_file()
        }
        if expected_files != observed_files:
            errors.append(f"evidence inventory mismatch: {case_dir}")

    expected_cases = 72
    if len(case_dirs) != expected_cases:
        errors.append(f"expected {expected_cases} reconstruction cases, found {len(case_dirs)}")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"Validated {len(case_dirs)} reconstruction cases.")
    print("SUMMARY reconstruction_cases=72")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
