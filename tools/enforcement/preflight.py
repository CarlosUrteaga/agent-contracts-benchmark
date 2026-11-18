"""Check model admission before a campaign; prepare separate compatibility copies."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .common import (
    MODES, REPO_ROOT, compute_agent_configuration_fingerprint,
    compute_contract_fingerprint, compute_contract_semantic_fingerprint,
    load_contract, load_model_profile, write_json,
)
from .tools_runtime import build_tool_definitions
from .vogtcon_adapter import VogtconRunAdapter


def configuration_fingerprint(profile: dict[str, Any], contract: dict[str, Any]) -> str:
    """Use the same inputs as run_scenario, before scenario tampering fixtures."""
    return compute_agent_configuration_fingerprint(
        system_prompt=(REPO_ROOT / profile["system_prompt_path"]).read_text(encoding="utf-8"),
        model_profile=profile,
        tool_definitions=build_tool_definitions(),
        memory_policy=contract.get("memory_policy", "mock-memory-v1"),
        runtime_version="enforcement-runtime-v2",
    )


def check_admission(contracts_root: Path, model_profile_path: Path) -> dict[str, Any]:
    profile = load_model_profile(model_profile_path)
    modes = {}
    for mode in MODES:
        path = contracts_root / f"{mode}.yaml"
        contract = load_contract(path)
        fingerprint = configuration_fingerprint(profile, contract)
        problems = []
        if contract.get("mode") != mode:
            problems.append("contract.mode_mismatch")
        if compute_contract_fingerprint(contract) != contract.get("contract_fingerprint"):
            problems.append("contract.content_fingerprint_mismatch")
        adapter = VogtconRunAdapter(contract_path=path, mode=mode, run_id="campaign-preflight")
        violations, _ = adapter.validate_pre(fingerprint, contract["contract_fingerprint"])
        problems.extend(violation["rule"] for violation in violations)
        modes[mode] = {"agent_fingerprint": fingerprint, "problems": problems}
    return {
        "profile_id": profile["profile_id"],
        "model_id": profile["model_id"],
        "admitted": all(not item["problems"] for item in modes.values()),
        "modes": modes,
    }


def require_admission(contracts_root: Path, model_profile_path: Path) -> dict[str, Any]:
    report = check_admission(contracts_root, model_profile_path)
    if not report["admitted"]:
        problems = {mode: item["problems"] for mode, item in report["modes"].items() if item["problems"]}
        raise ValueError(
            f"Campaign preflight failed for {report['profile_id']}: {problems}. "
            "No runs started. Check the profile and prepare separate compatible contracts."
        )
    return report


def prepare_contracts(contracts_root: Path, profile_paths: list[Path], out_root: Path) -> list[dict[str, Any]]:
    """Add approved profiles in a new directory, preserving contract semantics."""
    if out_root.exists():
        raise ValueError(f"Refusing to overwrite existing directory: {out_root}")
    profiles = [load_model_profile(path) for path in profile_paths]
    prepared = {}
    sources = {}
    for mode in MODES:
        source = contracts_root / f"{mode}.yaml"
        contract = load_contract(source)
        if compute_contract_fingerprint(contract) != contract.get("contract_fingerprint"):
            raise ValueError(f"Source contract content fingerprint is inconsistent: {source}")
        before = compute_contract_semantic_fingerprint(contract)
        approved = contract["approved_agent_configurations"]
        known = {item["fingerprint"] if isinstance(item, dict) else item for item in approved}
        for profile in profiles:
            fingerprint = configuration_fingerprint(profile, contract)
            if fingerprint not in known:
                approved.append({"fingerprint": fingerprint})
                known.add(fingerprint)
        contract["contract_fingerprint"] = compute_contract_fingerprint(contract)
        if compute_contract_semantic_fingerprint(contract) != before:
            raise ValueError(f"Contract semantics changed: {source}")
        prepared[mode] = contract
        sources[mode] = {"path": str(source), "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
    out_root.mkdir(parents=True, exist_ok=False)
    for mode, contract in prepared.items():
        write_json(out_root / f"{mode}.yaml", contract)
    reports = [require_admission(out_root, path) for path in profile_paths]
    write_json(out_root / "preflight_provenance.json", {
        "source_contracts": sources,
        "profiles": [{"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in profile_paths],
        "admission": reports,
        "note": "Compatibility copies only; historical campaign artifacts were not modified.",
    })
    return reports


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["check", "prepare"])
    parser.add_argument("--contracts", type=Path, required=True)
    parser.add_argument("--model-profile", type=Path, action="append", required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        if args.out is None:
            parser.error("prepare requires --out pointing to a new directory")
        reports = prepare_contracts(args.contracts, args.model_profile, args.out)
    else:
        reports = [check_admission(args.contracts, path) for path in args.model_profile]
    print(json.dumps(reports, indent=2))
    return 0 if all(report["admitted"] for report in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
