"""Validate all manifests under a manifest root."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .common import ARMS, contract_filename_for_arm
from .core import summarize_results, validate_manifest_against_contract


def contract_for_arm(contracts_dir: Path, arm: str) -> Path:
    return contracts_dir / contract_filename_for_arm(arm)


def iter_manifests(root: Path) -> list[Path]:
    return sorted(root.glob("*/*/*/*/manifest.json"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", required=True, help="manifest root, e.g. benchmark/manifests")
    parser.add_argument("--contracts", required=True)
    parser.add_argument("--out", required=True, help="jsonl output path")
    args = parser.parse_args()

    manifest_root = Path(args.runs)
    contracts_dir = Path(args.contracts)
    out_path = Path(args.out)
    results = []
    for manifest_path in iter_manifests(manifest_root):
        arm = manifest_path.parts[-4]
        if arm not in ARMS:
            raise ValueError(f"unexpected arm path for {manifest_path}")
        results.append(validate_manifest_against_contract(manifest_path, contract_for_arm(contracts_dir, arm)))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        "".join(json.dumps(result) + "\n" for result in results),
        encoding="utf-8",
    )
    summary_path = out_path.parent / "governor_summary.json"
    summary_path.write_text(json.dumps(summarize_results(results), indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(results)} results to {out_path}")
    print(f"Wrote summary to {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
