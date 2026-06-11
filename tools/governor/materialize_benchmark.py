"""Create a deterministic minimal benchmark dataset."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .common import (
    MANIFEST_FINGERPRINT_FILE,
    REPLICATIONS,
    RUN_LEDGER_FILE,
    STRATEGIES,
    all_steps,
    capabilities_for_step,
    capability_id_for_step,
    capability_label,
    governance_artifacts_for_arm,
    json_fingerprint,
    load_step_spec,
    reconstruction_conditions,
    strategy_steps,
)


def changed_files_for(arm: str, strategy: str, step: str) -> list[str]:
    files = [f"app/{capability_id_for_step(step)}.py", "tests/test_contract_benchmark.py"]
    if step == strategy_steps(strategy)[0]["step"]:
        files.extend(governance_artifacts_for_arm(arm))
    if step == "C6":
        files.append(RUN_LEDGER_FILE)
    return files


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_manifest(arm: str, strategy: str, replication: str, step: str) -> dict[str, object]:
    changed_files = changed_files_for(arm, strategy, step)
    governance_artifacts = governance_artifacts_for_arm(arm)
    manifest = {
        "step_id": step,
        "step": step,
        "status": "completed",
        "agent_executor": "codex",
        "arm": arm,
        "strategy": strategy,
        "replication": replication,
        "changed_files": changed_files,
        "changed_file_count": len(changed_files),
        "change_spread": round(len(changed_files) / 20.0, 4),
        "traceability_ratio": 1.0,
        "test_failures": 0,
        "contract_violations": 0,
        "run_ledger_compliance": step == "C6",
        "capabilities_present": capabilities_for_step(step),
        "governance_artifacts_present": governance_artifacts,
    }
    return manifest


def materialize_dataset(output_root: Path) -> int:
    manifest_root = output_root / "benchmark" / "manifests"
    if manifest_root.exists():
        shutil.rmtree(manifest_root)
    count = 0
    spec = load_step_spec()
    for arm in spec["arms"]:
        for strategy in STRATEGIES:
            for replication in REPLICATIONS:
                for step_info in strategy_steps(strategy):
                    step = step_info["step"]
                    step_dir = manifest_root / strategy / arm / replication / step
                    manifest = build_manifest(arm, strategy, replication, step)
                    write_json(step_dir / "manifest.json", manifest)
                    write_text(step_dir / MANIFEST_FINGERPRINT_FILE, json_fingerprint(manifest) + "\n")
                    write_text(
                        step_dir / "STEP_NOTE.md",
                        f"# {step}\n\nCapability: {capability_label(step)}\n",
                    )
                    for artifact in governance_artifacts_for_arm(arm):
                        write_text(step_dir / artifact, f"# {artifact}\n\nArm: {arm}\nStep: {step}\n")
                    if step == "C6":
                        write_json(
                            step_dir / RUN_LEDGER_FILE,
                            {
                                "run_id": f"{strategy}-{arm}-{replication}-{step}",
                                "arm": arm,
                                "strategy": strategy,
                                "replication": replication,
                                "step": step,
                                "status": "completed",
                            },
                        )
                    count += 1
    return count


def materialize_supporting_structure(output_root: Path) -> None:
    benchmark_root = output_root / "benchmark"
    write_text(
        benchmark_root / "baseline" / "README.md",
        "# Baseline\n\nThis clone materializes a minimal reproducible benchmark scaffold derived from the T0 seed assistant.\n",
    )
    write_text(
        benchmark_root / "prompts" / "README.md",
        "# Prompts\n\nThe prompt protocol for benchmark execution remains documented in `PROMPT.md`.\n",
    )
    for arm in load_step_spec()["arms"]:
        write_text(
            benchmark_root / "arms" / arm / "README.md",
            f"# {arm}\n\nGenerated experimental configuration for the `{arm}` arm.\n",
        )
    write_text(
        benchmark_root / "oracle" / "README.md",
        "# Oracle\n\nThis directory stores deterministic trajectory expectations and reconstruction scoring inputs.\n",
    )
    oracle_payload = {
        "steps": all_steps(),
        "conditions": sorted(reconstruction_conditions()),
    }
    write_json(benchmark_root / "oracle" / "benchmark_oracle.json", oracle_payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=".", help="repository root or target directory")
    args = parser.parse_args()

    output_root = Path(args.out).resolve()
    materialize_supporting_structure(output_root)
    count = materialize_dataset(output_root)
    print(f"Materialized {count} manifests under {output_root / 'benchmark' / 'manifests'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
