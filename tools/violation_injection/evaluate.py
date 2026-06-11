"""Evaluate violation detection performance over mutated manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.governor.core import validate_manifest_against_contract


def contract_path(contracts_root: Path, arm: str) -> Path:
    return contracts_root / f"{arm.replace('-', '_')}.yaml"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mutated-runs", required=True)
    parser.add_argument("--contracts", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    mutated_root = Path(args.mutated_runs)
    contracts_root = Path(args.contracts)
    out_path = Path(args.out)

    manifests = sorted(mutated_root.glob("*/*/*/*/manifest.json"))
    tp = fp = tn = fn = 0
    by_mutation: dict[str, dict[str, int]] = {}
    by_arm: dict[str, dict[str, int]] = {}

    for manifest_path in manifests:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        metadata = manifest["_mutation"]
        source_arm = manifest_path.parts[-4]
        result = validate_manifest_against_contract(manifest_path, contract_path(contracts_root, source_arm))
        predicted_fail = result["verdict"] == "fail"
        expected_fail = metadata["expected_verdict"] == "fail"
        if predicted_fail and expected_fail:
            tp += 1
        elif predicted_fail and not expected_fail:
            fp += 1
        elif not predicted_fail and expected_fail:
            fn += 1
        else:
            tn += 1

        mutation_bucket = by_mutation.setdefault(metadata["mutation_type"], {"total": 0, "detected": 0})
        mutation_bucket["total"] += 1
        if predicted_fail:
            mutation_bucket["detected"] += 1

        arm_bucket = by_arm.setdefault(source_arm, {"total": 0, "detected": 0})
        arm_bucket["total"] += 1
        if predicted_fail:
            arm_bucket["detected"] += 1

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    summary = {
        "true_positives": tp,
        "false_positives": fp,
        "true_negatives": tn,
        "false_negatives": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "F1": round(f1, 4),
        "detection_rate_by_mutation_type": {
            key: round(value["detected"] / value["total"], 4) if value["total"] else 0.0
            for key, value in by_mutation.items()
        },
        "detection_rate_by_arm": {
            key: round(value["detected"] / value["total"], 4) if value["total"] else 0.0
            for key, value in by_arm.items()
        },
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote violation detection summary to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
