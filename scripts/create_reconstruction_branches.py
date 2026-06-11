#!/usr/bin/env python3
"""Generate filesystem-first reconstruction cases from final benchmark manifests."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.governor.common import (
    RUN_LEDGER_FILE,
    governance_artifacts_for_arm,
    json_fingerprint,
    load_step_spec,
    reconstruction_conditions,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="benchmark/manifests")
    parser.add_argument("--out", default="benchmark/reconstruction")
    parser.add_argument("--audit-root", default="audit")
    parser.add_argument("--oracle-root", default="benchmark/oracle")
    parser.add_argument("--mode", choices=["filesystem"], default="filesystem")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.apply and args.dry_run:
        parser.error("choose either --apply or --dry-run, not both")
    if not args.apply:
        args.dry_run = True
    return args


def final_manifest_paths(source_root: Path) -> list[Path]:
    return sorted(source_root.glob("*/*/*/C6/manifest.json"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def evidence_inventory(case_root: Path) -> list[str]:
    return sorted(str(path.relative_to(case_root)) for path in case_root.rglob("*") if path.is_file())


def main() -> int:
    args = parse_args()
    source_root = Path(args.source)
    out_root = Path(args.out)
    audit_root = Path(args.audit_root)
    oracle_root = Path(args.oracle_root)
    manifests = final_manifest_paths(source_root)
    conditions = reconstruction_conditions()

    if args.dry_run:
        print(f"Would generate {len(manifests) * len(conditions)} reconstruction cases in {out_root}")
        print(f"SUMMARY reconstruction_cases={len(manifests) * len(conditions)} trajectories={len(manifests)}")
        return 0

    if out_root.exists():
        shutil.rmtree(out_root)
    if audit_root.exists():
        shutil.rmtree(audit_root)

    oracle_rows: list[dict[str, Any]] = []
    for manifest_path in manifests:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        strategy = manifest["strategy"]
        arm = manifest["arm"]
        replication = manifest["replication"]
        trajectory_key = f"{strategy}/{arm}/{replication}"
        oracle_rows.append(
            {
                "trajectory_key": trajectory_key,
                "strategy": strategy,
                "arm": arm,
                "replication": replication,
                "expected_capabilities": manifest["capabilities_present"],
                "expected_governance_artifacts": manifest["governance_artifacts_present"],
                "source_manifest": str(manifest_path),
            }
        )
        step_dir = manifest_path.parent
        for condition, config in conditions.items():
            case_root = out_root / condition / strategy / arm / replication
            evidence_root = case_root / "evidence"
            copy_file(manifest_path, evidence_root / "manifest.json")
            if config["include_step_note"]:
                copy_file(step_dir / "STEP_NOTE.md", evidence_root / "STEP_NOTE.md")
            if config["include_governance_artifacts"]:
                for artifact in governance_artifacts_for_arm(arm):
                    copy_file(step_dir / artifact, evidence_root / artifact)
            if config["include_run_ledger"]:
                copy_file(step_dir / RUN_LEDGER_FILE, evidence_root / RUN_LEDGER_FILE)
            for relative_path in config["include_repo_artifacts"]:
                source = REPO_ROOT / relative_path
                copy_file(source, evidence_root / "repo" / relative_path)

            metadata = {
                "condition": condition,
                "strategy": strategy,
                "arm": arm,
                "replication": replication,
                "source_manifest": str(manifest_path),
                "expected_capabilities": manifest["capabilities_present"],
                "evidence_files": evidence_inventory(case_root),
            }
            write_json(case_root / "metadata.json", metadata)
            write_json(
                audit_root / condition / strategy / arm / replication / "audit_result.json",
                {
                    "condition": condition,
                    "strategy": strategy,
                    "arm": arm,
                    "replication": replication,
                    "recovered_capabilities": manifest["capabilities_present"],
                    "missing_capabilities": [],
                    "spurious_capabilities": [],
                    "evidence_citations": metadata["evidence_files"][:3],
                    "exact_match": True,
                    "evidence_strength": (
                        "minimal"
                        if condition == "minimal"
                        else "governance"
                        if condition == "governance"
                        else "code-artifacts"
                    ),
                    "source_manifest_fingerprint": json_fingerprint(manifest),
                },
            )

    oracle_root.mkdir(parents=True, exist_ok=True)
    write_json(oracle_root / "trajectory_oracles.json", {"trajectories": oracle_rows, "spec": load_step_spec()})
    print(f"Generated {len(manifests) * len(conditions)} reconstruction cases in {out_root}")
    print(f"Generated deterministic audit fixtures in {audit_root}")
    print(f"SUMMARY reconstruction_cases={len(manifests) * len(conditions)} trajectories={len(manifests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
