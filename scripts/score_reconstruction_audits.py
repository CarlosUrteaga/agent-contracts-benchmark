#!/usr/bin/env python3
"""Score reconstruction audit outputs against the canonical oracle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_oracle(path: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {item["trajectory_key"]: item for item in payload["trajectories"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-root", default="audit")
    parser.add_argument("--oracle", default="benchmark/oracle/trajectory_oracles.json")
    parser.add_argument("--out", default="results/reconstruction_summary.json")
    args = parser.parse_args()

    audit_root = Path(args.audit_root)
    oracle = load_oracle(Path(args.oracle))
    out_path = Path(args.out)
    audits = sorted(audit_root.glob("*/*/*/*/audit_result.json"))

    exact_matches = 0
    by_condition: dict[str, dict[str, int]] = {}
    detailed: list[dict[str, Any]] = []

    for audit_path in audits:
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        key = f"{audit['strategy']}/{audit['arm']}/{audit['replication']}"
        expected = oracle[key]["expected_capabilities"]
        recovered = audit["recovered_capabilities"]
        missing = sorted(set(expected) - set(recovered))
        spurious = sorted(set(recovered) - set(expected))
        exact_match = not missing and not spurious
        if exact_match:
            exact_matches += 1
        bucket = by_condition.setdefault(audit["condition"], {"total": 0, "exact_matches": 0})
        bucket["total"] += 1
        if exact_match:
            bucket["exact_matches"] += 1
        detailed.append(
            {
                "audit_path": str(audit_path),
                "trajectory_key": key,
                "condition": audit["condition"],
                "missing_capabilities": missing,
                "spurious_capabilities": spurious,
                "exact_match": exact_match,
            }
        )

    summary = {
        "total_audits": len(audits),
        "exact_match_count": exact_matches,
        "exact_match_rate": round(exact_matches / len(audits), 4) if audits else 0.0,
        "by_condition": {
            condition: {
                "total": values["total"],
                "exact_match_count": values["exact_matches"],
                "exact_match_rate": round(values["exact_matches"] / values["total"], 4) if values["total"] else 0.0,
            }
            for condition, values in sorted(by_condition.items())
        },
        "details": detailed,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote reconstruction scoring summary to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
