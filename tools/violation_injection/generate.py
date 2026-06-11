"""Generate controlled invalid manifest copies."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from tools.governor.common import (
    AGENT_CARD_FILE,
    CONTRACTS_FILE,
    MANIFEST_FINGERPRINT_FILE,
    RUN_LEDGER_FILE,
    WORKFLOW_FILE,
    json_fingerprint,
)

MUTATIONS = {
    "missing_required_artifact": "artifact.required",
    "missing_run_ledger": "ledger.required_at_c6",
    "wrong_traceability_ratio": "traceability.perfect",
    "nonzero_contract_violations": "contracts.zero_violations",
    "nonzero_test_failures": "tests.zero_failures",
    "missing_contracts_md": "contracts.file_required",
    "missing_workflow_md": "workflow.file_required",
    "capability_present_but_not_declared": "capability.declared",
    "inconsistent_arm_contract": "contract.arm_match",
    "fingerprint_mismatch": "manifest.fingerprint_match",
}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def pick_mutation(arm: str, step: str, index: int) -> str:
    preferred = {
        "base": [
            "wrong_traceability_ratio",
            "nonzero_contract_violations",
            "nonzero_test_failures",
            "fingerprint_mismatch",
        ],
        "agent-card": [
            "missing_required_artifact",
            "capability_present_but_not_declared",
            "fingerprint_mismatch",
        ],
        "contract-first": (
            ["missing_contracts_md", "inconsistent_arm_contract", "fingerprint_mismatch"]
            if step != "C6"
            else ["missing_run_ledger", "missing_contracts_md", "inconsistent_arm_contract"]
        ),
        "contract-flow": (
            ["missing_workflow_md", "fingerprint_mismatch", "inconsistent_arm_contract"]
            if step != "C6"
            else ["missing_run_ledger", "missing_workflow_md", "fingerprint_mismatch"]
        ),
    }
    options = preferred[arm]
    return options[index % len(options)]


def mutate_manifest(manifest: dict[str, Any], mutation_type: str) -> tuple[dict[str, Any], list[str]]:
    manifest = json.loads(json.dumps(manifest))
    removed_artifacts: list[str] = []
    if mutation_type == "missing_required_artifact":
        manifest["governance_artifacts_present"] = []
        removed_artifacts.append(AGENT_CARD_FILE)
    elif mutation_type == "missing_run_ledger":
        removed_artifacts.append(RUN_LEDGER_FILE)
    elif mutation_type == "wrong_traceability_ratio":
        manifest["traceability_ratio"] = 0.75
    elif mutation_type == "nonzero_contract_violations":
        manifest["contract_violations"] = 1
    elif mutation_type == "nonzero_test_failures":
        manifest["test_failures"] = 1
    elif mutation_type == "missing_contracts_md":
        manifest["governance_artifacts_present"] = [item for item in manifest["governance_artifacts_present"] if item != CONTRACTS_FILE]
        removed_artifacts.append(CONTRACTS_FILE)
    elif mutation_type == "missing_workflow_md":
        manifest["governance_artifacts_present"] = [item for item in manifest["governance_artifacts_present"] if item != WORKFLOW_FILE]
        removed_artifacts.append(WORKFLOW_FILE)
    elif mutation_type == "capability_present_but_not_declared":
        if manifest["changed_files"]:
            manifest["changed_files"][0] = "structured_response"
            manifest["changed_file_count"] = len(manifest["changed_files"])
        manifest["capabilities_present"] = []
    elif mutation_type == "inconsistent_arm_contract":
        manifest["arm"] = "base"
    elif mutation_type == "fingerprint_mismatch":
        pass
    else:
        raise ValueError(f"unsupported mutation_type: {mutation_type}")
    return manifest, removed_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-runs", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    source_root = Path(args.input_runs)
    out_root = Path(args.out)
    if out_root.exists():
        shutil.rmtree(out_root)

    manifests = sorted(source_root.glob("*/*/*/*/manifest.json"))
    for index, manifest_path in enumerate(manifests):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        arm = manifest["arm"]
        step = manifest["step"]
        mutation_type = pick_mutation(arm, step, index)
        mutated_manifest, removed_artifacts = mutate_manifest(manifest, mutation_type)
        metadata = {
            "mutation_id": f"{arm}-{manifest['strategy']}-{manifest['replication']}-{step}-{mutation_type}",
            "source_manifest": str(manifest_path),
            "mutation_type": mutation_type,
            "expected_verdict": "fail",
            "expected_rule_id": MUTATIONS[mutation_type],
        }
        mutated_manifest["_mutation"] = metadata
        destination_dir = out_root / manifest_path.relative_to(source_root).parent
        destination_dir.mkdir(parents=True, exist_ok=True)
        write_json(destination_dir / "manifest.json", mutated_manifest)
        fingerprint = json_fingerprint({key: value for key, value in mutated_manifest.items() if key != "_mutation"})
        if mutation_type == "fingerprint_mismatch":
            fingerprint = "sha256:deadbeef"
        (destination_dir / MANIFEST_FINGERPRINT_FILE).write_text(fingerprint + "\n", encoding="utf-8")

        for sibling in manifest_path.parent.iterdir():
            if sibling.name in {"manifest.json", MANIFEST_FINGERPRINT_FILE}:
                continue
            if sibling.name in removed_artifacts:
                continue
            if mutation_type == "missing_run_ledger" and sibling.name == RUN_LEDGER_FILE:
                continue
            shutil.copy2(sibling, destination_dir / sibling.name)

    print(f"Generated {len(manifests)} mutated manifests in {out_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
