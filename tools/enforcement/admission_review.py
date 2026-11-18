"""Derive an admission-screened comparison subset without changing run statistics."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path("results/enforcement/statistics/final-twenty-six-campaigns.json")
OUTPUT = Path("results/enforcement/statistics/admission-reviewed-twenty-three-campaigns.json")
MODES = ("no_contract", "advisory", "guarded", "strict")


def evidence_digest(paths: list[Path], root: Path) -> str:
    """Hash an ordered manifest of relative names and SHA-256 content digests."""
    manifest = [[p.relative_to(root).as_posix(), hashlib.sha256(p.read_bytes()).hexdigest()]
                for p in sorted(paths)]
    return hashlib.sha256(json.dumps(manifest, separators=(",", ":")).encode()).hexdigest()


def load_scenarios(root: Path) -> dict[str, Any]:
    return {s["scenario_id"]: s for p in sorted((root / "benchmark/enforcement/scenarios").glob("S-*.json"))
            for s in [json.loads(p.read_text())]}


def audit_campaign(report: dict[str, Any], scenarios: dict[str, Any], root: Path = REPO_ROOT) -> dict[str, Any]:
    run_root = root / report["runs_root"]
    paths = sorted(run_root.glob("*/*/rep*/S-*/summary.json"))
    unexpected = Counter({mode: 0 for mode in MODES})
    nominal_aborts = 0
    cells: Counter = Counter()
    runs = set()
    for path in paths:
        run = json.loads(path.read_text())
        key = (run["mode"], run["replication_id"], run["scenario_id"])
        if key in runs or run["profile_id"] != report["profile_id"]:
            raise ValueError(f"Duplicate run or mismatched profile: {path}")
        runs.add(key)
        cells[(run["mode"], run["scenario_id"])] += 1
        scenario = scenarios[run["scenario_id"]]
        if run["scenario_type"] != scenario["scenario_type"]:
            raise ValueError(f"Scenario type mismatch: {path}")
        expected = set(scenario.get("expected_pre_execution_violations", []))
        observed = {v["rule"] for v in run["violations"] if v["phase"] == "pre_execution"}
        if observed - expected:
            unexpected[run["mode"]] += 1
        if run["scenario_type"] == "nominal" and run["final_status"] == "aborted_pre_execution":
            nominal_aborts += 1
    expected_cells = Counter({(mode, scenario): report["replications"] for mode in MODES for scenario in scenarios})
    if cells != expected_cells or len(paths) != report["runs_total"]:
        raise ValueError(f"Incomplete admission evidence: {report['campaign_id']}")
    count = sum(unexpected.values())
    return {
        "campaign_id": report["campaign_id"], "runs_root": report["runs_root"],
        "runs_inspected": len(paths), "included": count == 0,
        "unexpected_pre_execution_runs": count,
        "unexpected_pre_execution_runs_by_mode": dict(unexpected),
        "nominal_pre_execution_aborts": nominal_aborts,
        "summary_evidence_sha256": evidence_digest(paths, root),
    }


def summarize(reports: list[dict[str, Any]]) -> dict[str, Any]:
    paired = [r["paired_mode_differences"]["guarded_vs_strict"] for r in reports]
    deltas = [p["successful_safe_completion_rate"]["difference_estimate"] for p in paired]
    return {
        "unsafe_rate_defined_campaigns_by_mode": {
            mode: sum(r["per_mode_statistics"][mode]["unsafe_side_effect_rate"]["defined"] for r in reports)
            for mode in MODES
        },
        "guarded_minus_strict_safe_completion_range": [min(deltas), max(deltas)],
        "guarded_minus_strict_safe_completion_positive_campaigns": sum(d > 0 for d in deltas),
        "guarded_minus_strict_safe_completion_ci_above_zero_campaigns": sum(
            p["successful_safe_completion_rate"]["ci_95"][0] > 0 for p in paired),
        "guarded_minus_strict_latency_positive_campaigns": sum(p["mean_latency_ms"]["difference_estimate"] > 0 for p in paired),
        "guarded_minus_strict_tokens_positive_campaigns": sum(p["mean_token_usage"]["difference_estimate"] > 0 for p in paired),
        "campaigns_with_nonzero_estimated_cost": sum(
            any(r["per_mode_statistics"][mode]["mean_estimated_cost"]["estimate"] not in (None, 0) for mode in MODES)
            for r in reports),
    }


def build_review(reviewed_at: str, root: Path = REPO_ROOT) -> dict[str, Any]:
    source_bytes = (root / SOURCE).read_bytes()
    original = json.loads(source_bytes)
    reports = original["campaign_reports"]
    scenarios = load_scenarios(root)
    decisions = [audit_campaign(r, scenarios, root) for r in reports]
    included = {d["campaign_id"] for d in decisions if d["included"]}
    retained = [r for r in reports if r["campaign_id"] in included]
    return {
        **original,
        "analysis_stage": "admission_reviewed",
        "campaign_reports": retained,
        "source_notes": original.get("notes", []),
        "notes": [
            "Derived admission-screened subset of the archived 26-campaign artifact.",
            "Every retained campaign report is copied unchanged, including its bootstrap estimates and intervals.",
            "generated_at records the original bootstrap generation; admission_review.reviewed_at dates this review.",
            "Campaigns remain separate; no pooled model estimate or new bootstrap computation is introduced.",
        ],
        "admission_review": {
            "schema_version": "campaign-admission-review-v1", "reviewed_at": reviewed_at,
            "source_artifact": SOURCE.as_posix(),
            "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
            "scenario_evidence_sha256": evidence_digest(list((root / "benchmark/enforcement/scenarios").glob("S-*.json")), root),
            "inclusion_rule": "Retain the entire campaign only if every recorded pre-execution violation is expected by its scenario.",
            "scope": "Post hoc admission screen; not a certification of freeze identity or general experimental validity. No bootstrap estimates or intervals were recomputed.",
            "inventory_campaign_count": len(reports), "inventory_run_count": sum(r["runs_total"] for r in reports),
            "included_campaign_count": len(retained), "included_run_count": sum(r["runs_total"] for r in retained),
            "campaign_decisions": decisions,
        },
        "reviewed_subset_summary": summarize(retained),
    }


def load_verified_review(path: Path = REPO_ROOT / OUTPUT, root: Path = REPO_ROOT) -> dict[str, Any]:
    stored = json.loads(path.read_text())
    if stored != build_review(stored["admission_review"]["reviewed_at"], root):
        raise ValueError("Admission review is stale or inconsistent; regenerate it from the recorded evidence.")
    return stored


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=REPO_ROOT / OUTPUT)
    parser.add_argument("--reviewed-at", help="UTC timestamp for this post hoc review; required when writing")
    parser.add_argument("--check", action="store_true", help="Verify existing review against source statistics and run evidence")
    args = parser.parse_args()
    if args.check:
        payload = load_verified_review(args.out)
    else:
        if not args.reviewed_at:
            parser.error("--reviewed-at is required when writing")
        payload = build_review(args.reviewed_at)
        args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"review": str(args.out), "summary": payload["reviewed_subset_summary"]}, indent=2))


if __name__ == "__main__":
    main()
