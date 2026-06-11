# Architectural Contracts Benchmark

This repository hosts the protocol scaffold for a controlled benchmark on how architectural formalization affects change containment, rework, and traceability in agentic systems.

The scaffold defines the benchmark design, trajectory conventions, reproducibility metadata, validation checks, and branch planning workflow. It includes the minimal `T0` seed assistant used to initialize experiment branches, but it does not implement the full benchmark target system.

## Benchmark Overview

The benchmark compares four architecture arms across two development strategies:

- `base`
- `agent-card`
- `contract-first`
- `contract-flow`

Strategies:

- `evolutionary`
- `final-spec`

Each `(strategy, arm)` combination is replicated three times, yielding `24` experimental trajectories.

## Execution Order

1. scaffold benchmark protocol
2. create `t0-common`
3. create arm baselines
4. generate experiment branches
5. execute trajectories
6. aggregate metrics

## Repository Contents

- `BENCHMARK_SPEC.md`: final target system and benchmark intent
- `ARCHITECTURE_ARMS.md`: arm-specific constraints
- `CHANGE_PROTOCOL.md`: evolutionary and final-spec build rules
- `STEP_PROTOCOL.md`: operational step-by-step execution rules
- `ARM_INSTRUCTIONS.md`: operational implementation rules for each arm
- `METRICS_SPEC.md`: manifest and aggregation metrics
- `IMPLEMENTATION_PLAN.md`: protocol scaffolding milestones
- `PROMPT.md`: execution prompt for trajectory agents
- `app/`: minimal `T0` seed assistant used for branch initialization
- `tests/`: baseline validation for the `T0` assistant
- `templates/`: JSON templates for manifests and run ledgers
- `scripts/`: protocol validator and experiment branch planner

## Published Baseline

`main` is intended to stay publishable as the clean `T0` scaffold.

- The canonical benchmark corpus is materialized under `benchmark/manifests/`.
- Generated `outputs/` reports are omitted from `main`.
- Reconstruction and analysis artifacts should live on their own branches.

## Trajectory-Local Plan

`IMPLEMENTATION_PLAN.md` is trajectory-local.

- The copy on `main` is the seed version used when creating experimental branches.
- Each experimental branch updates its own copy.
- Divergence across branches is expected and valid.
- Do not merge `IMPLEMENTATION_PLAN.md` across experimental branches.

## Scripts

Validate the scaffold from the repository root:

```bash
python scripts/validate_protocol.py
```

Create the required local baseline branches from available remote refs:

```bash
python3 scripts/create_baseline_branches.py --dry-run
python3 scripts/create_baseline_branches.py --apply
```

Preview experiment branch creation without mutating Git state:

```bash
python scripts/create_experiment_branches.py
python scripts/create_experiment_branches.py --dry-run
```

Create experiment branches from existing arm baselines:

```bash
python scripts/create_experiment_branches.py --apply
```

`--apply` is the only mode that may create branches. The script never creates `benchmark-specs`, `t0-common`, or arm baseline branches.

## Fresh Workspace Guide

For a new workspace, you currently need the clean `main` scaffold plus the deterministic benchmark and reconstruction tooling shipped in this repository.

What is already on `main`

- `scripts/create_experiment_branches.py`
- `scripts/aggregate_manifests.py`
- `scripts/create_reconstruction_branches.py`
- `scripts/score_reconstruction_audits.py`
- `scripts/validate_reconstruction_branches.py`
- `templates/reconstruction_prompt.md`
- `README_RECONSTRUCTION.md`
- `tests/test_reconstruction_scaffold.py`

Fresh workspace flow

1. Clone and enter the repo:

```bash
git clone <repo-url> Architectural-Contracts
cd Architectural-Contracts
git switch main
```

2. Validate the clean scaffold:

```bash
python3 scripts/validate_protocol.py
python3 tests/test_t0_rag.py
```

3. Materialize local baseline branches:

```bash
python3 scripts/create_baseline_branches.py --dry-run
python3 scripts/create_baseline_branches.py --apply
```

This creates:

- `t0-common`
- `arm/base`
- `arm/agent-card`
- `arm/contract-first`
- `arm/contract-flow`

4. Generate experiment branches:

```bash
python3 scripts/create_experiment_branches.py --dry-run
python3 scripts/create_experiment_branches.py --apply
```

5. If historical branches are unavailable, materialize the deterministic benchmark corpus:

```bash
python3 -m tools.governor.materialize_benchmark --out .
```

This produces manifests under:

```text
benchmark/manifests/{strategy}/{arm}/{replication}/{step}/manifest.json
```

6. Run the experiment work on the `exp/...` branches if you are extending the benchmark beyond the deterministic scaffold.

7. Validate contracts:

```bash
python3 -m tools.governor.validate_all --runs benchmark/manifests --contracts contracts --out results/governor_results.jsonl
```

8. Aggregate benchmark metrics:

```bash
python3 scripts/aggregate_manifests.py --runs benchmark/manifests --out results
```

It writes:

- `results/manifest_rows.csv`
- `results/summary_by_arm_strategy_step.csv`
- `results/summary_by_arm_strategy.csv`
- `results/qc_report.json`

9. Generate reconstruction branches:

```bash
python3 scripts/create_reconstruction_branches.py --apply
```

10. Validate the prepared reconstruction branches before running the auditor:

```bash
python3 scripts/validate_reconstruction_branches.py --root benchmark/reconstruction
```

11. Run the reconstruction audit on each `recon/...` branch.
That should create:

```text
audit/{condition}/{strategy}/{arm}/{replication}/audit_result.json
```

12. Score reconstruction results:

```bash
python3 scripts/score_reconstruction_audits.py --audit-root audit --oracle benchmark/oracle/trajectory_oracles.json --out results/reconstruction_summary.json
```

## Agent Prompts

Use this short instruction when running benchmark execution on an experiment branch:

```text
Execute the benchmark work required for the current branch.

Follow PROMPT.md exactly.
```

Use this short instruction when running the reconstruction audit on a reconstruction branch:

```text
Execute the reconstruction audit required for the current branch.

Follow PROMPT.md exactly.
```
