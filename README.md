# Architectural Contracts Benchmark

This repository is the replication scaffold for a benchmark family about architectural governance in agentic systems.

It is organized around three connected activities:

1. `construction`
   Build benchmark trajectories under different architectural arms and record per-step manifests.

2. `reconstruction`
   Repackage completed trajectories under controlled evidence conditions and ask an auditor to reconstruct the implemented capabilities.

3. `contract audit`
   Validate benchmark manifests against explicit governance contracts using a post-hoc Agent Governor prototype.

The goal of `main` is to preserve enough code, protocol, and documentation for a fresh machine to understand the experiment and reproduce it phase by phase.

For the validator-facing protocol version of the repository description, see `README_PROTOCOL.md`. The tutorial in `README.md` is optimized for replication guidance, while `README_PROTOCOL.md` preserves the stricter scaffold wording expected by `scripts/validate_protocol.py`.

## What This Repository Measures

The benchmark asks two main empirical questions:

1. During construction, how does stronger architectural formalization affect change spread, rework, traceability, and co-evolution overhead?
2. During reconstruction, how much does preserved governance and implementation evidence improve later auditability?

A complementary contract-audit layer checks whether benchmark traces satisfy explicit arm-specific governance rules.

## Benchmark Design

### Architecture arms

- `base`
- `agent-card`
- `contract-first`
- `contract-flow`

### Construction strategies

- `evolutionary`
- `final-spec`

### Replications

- `rep01`
- `rep02`
- `rep03`

This yields `24` canonical construction trajectories.

### Construction outputs

- `evolutionary` trajectories emit one manifest per step `C1` to `C6`
- `final-spec` trajectories emit one manifest for `C6`

The complete canonical construction benchmark therefore contains `84` manifests.

### Reconstruction conditions

- `minimal`
- `governance`
- `code-artifacts`

These conditions are applied over the completed construction trajectories, yielding `72` canonical reconstruction branches.

## Repository Map

Core benchmark protocol:

- `BENCHMARK_SPEC.md`
- `ARCHITECTURE_ARMS.md`
- `CHANGE_PROTOCOL.md`
- `STEP_PROTOCOL.md`
- `ARM_INSTRUCTIONS.md`
- `METRICS_SPEC.md`
- `PROMPT.md`

Seed implementation:

- `app/`
- `tests/`
- `templates/`

Construction tooling:

- `scripts/create_baseline_branches.py`
- `scripts/validate_protocol.py`
- `scripts/create_experiment_branches.py`

Evaluation notes and summaries:

- `EVALUATION_NOTES.md`
- `README_RECONSTRUCTION.md`
- `RESULTS_ARMS.md`
- `RESULTS_AUDIT.md`
- `RESULTS_COMBINED.md`

Generated benchmark and contract tooling:

- `benchmark/`
- `contracts/`
- `tools/governor/`
- `tools/violation_injection/`
- `results/`
- `docs/contract_experiment.md`

Planning note for a future multi-LLM extension:

- `MULTI_LLM_BENCHMARK_PLAN.md`

## Replication Tutorial

This section is the intended start point for a fresh machine.

### Step 0: Understand what `main` contains

`main` is intended to remain a publishable scaffold centered on the clean `T0` benchmark setup and a deterministic benchmark materialization.

That means:

- the protocol and naming conventions should live on `main`
- the seed assistant and baseline tests should live on `main`
- branch-generation logic should live on `main`
- the canonical benchmark corpus lives under `benchmark/manifests/`
- generated `outputs/` reports are normally omitted from `main`

So `main` is the reproducibility anchor, not the place where all branch-local results are permanently materialized.

### Step 1: Clone and validate the scaffold

```bash
git clone <repo-url> Architectural-Contracts
cd Architectural-Contracts
git switch main
python3 scripts/validate_protocol.py
python3 tests/test_t0_rag.py
```

At this point you should have:

- the benchmark protocol docs
- the `T0` seed assistant
- branch-generation logic
- baseline validation passing

### Step 2: Materialize the benchmark corpus

If historical experiment branches are not present in the clone, generate the minimal reproducible benchmark dataset:

```bash
python3 -m tools.governor.materialize_benchmark --out .
```

This creates:

```text
benchmark/
  baseline/
  prompts/
  arms/
  manifests/
  oracle/
```

The canonical corpus contains `24` trajectories and `84` manifests under:

```text
benchmark/manifests/{strategy}/{arm}/{replication}/{step}/manifest.json
```

### Step 3: Generate construction branches

Before generating `exp/...` branches, materialize the local baseline branches required by the planner.

Preview the baseline branch plan:

```bash
python3 scripts/create_baseline_branches.py --dry-run
```

Create the local baseline branches:

```bash
python3 scripts/create_baseline_branches.py --apply
```

This creates the local branches required by the experiment planner:

```text
t0-common
arm/base
arm/agent-card
arm/contract-first
arm/contract-flow
```

These local branches are created from the matching `origin/*` baseline refs when available.

### Step 4: Generate experiment branches

Preview the branch plan:

```bash
python3 scripts/create_experiment_branches.py --dry-run
```

Apply the branch plan:

```bash
python3 scripts/create_experiment_branches.py --apply
```

This creates canonical experiment branches under the conceptual family:

```text
exp/{strategy}/{arm}/{replication}
```

### Step 5: Execute construction trajectories

On each `exp/...` branch, run the benchmark work using the prompt in `PROMPT.md`.

Short execution prompt:

```text
Execute the benchmark work required for the current branch.

Follow PROMPT.md exactly.
```

Each completed step should produce or update:

```text
benchmark/manifests/{strategy}/{arm}/{replication}/{step}/manifest.json
```

These manifests are the primary evidence for the construction benchmark.

### Step 6: Validate contracts over valid traces

Run the Agent Governor over the canonical manifests:

```bash
python3 -m tools.governor.validate_all \
  --runs benchmark/manifests \
  --contracts contracts \
  --out results/governor_results.jsonl
```

This writes:

- `results/governor_results.jsonl`
- `results/governor_summary.json`

### Step 7: Evaluate injected violations

Generate controlled invalid copies:

```bash
python3 -m tools.violation_injection.generate \
  --input-runs benchmark/manifests \
  --out mutated_runs
```

Evaluate violation detection:

```bash
python3 -m tools.violation_injection.evaluate \
  --mutated-runs mutated_runs \
  --contracts contracts \
  --out results/violation_detection_summary.json
```

### Step 8: Aggregate construction metrics

The aggregation step is:

```bash
python3 scripts/aggregate_manifests.py --runs benchmark/manifests --out results
```

Expected outputs:

- `results/manifest_rows.csv`
- `results/summary_by_arm_strategy_step.csv`
- `results/summary_by_arm_strategy.csv`
- `results/qc_report.json`

### Step 9: Prepare reconstruction branches

The canonical reconstruction generator on `main` is filesystem-first:

```bash
python3 scripts/create_reconstruction_branches.py --apply
```

Reconstruction cases follow:

```text
benchmark/reconstruction/{condition}/{strategy}/{arm}/{replication}
```

### Step 10: Validate reconstruction branches

Validate the generated reconstruction cases:

```bash
python3 scripts/validate_reconstruction_branches.py --root benchmark/reconstruction
```

### Step 11: Run reconstruction audits

The deterministic scaffold also materializes baseline audit fixtures for scoring.

Short execution prompt:

```text
Execute the reconstruction audit required for the current branch.

Follow PROMPT.md exactly.
```

Baseline audit fixtures are written to:

```text
audit/{condition}/{strategy}/{arm}/{replication}/audit_result.json
```

Within each reconstruction case:

- preserved evidence is packaged under `evidence/`
- the baseline audit result is written under `audit/...`

### Step 12: Score reconstruction audits

The scoring step is:

```bash
python3 scripts/score_reconstruction_audits.py \
  --audit-root audit \
  --oracle benchmark/oracle/trajectory_oracles.json \
  --out results/reconstruction_summary.json
```

### Step 13: Run the contract audit layer

The repository includes a complementary post-hoc contract-governor workflow in:

```text
contracts/
tools/governor/
tools/violation_injection/
```

This layer validates manifests against executable YAML contracts and reports:

- pass/fail verdicts
- violation counts
- provenance-aware fingerprints
- symbolic validation latency

Typical validation flow:

```bash
python3 -m tools.governor.validate_all \
  --runs benchmark/manifests \
  --contracts contracts \
  --out results/governor_results.jsonl
```

This prototype is intended as a validation layer over structured traces, not as a full live runtime mediator.

## What Is Already on `main`

Present today:

- benchmark specification and protocol docs
- `T0` seed assistant
- baseline tests
- baseline-branch materialization script
- experiment branch generator
- evaluation summaries
- contract-governor tooling

Also present on `main`:

- manifest aggregation
- filesystem-first reconstruction generation
- reconstruction validation and scoring
- reconstruction prompt and documentation
- reconstruction scaffold tests

## Interpretation of the Three Parts

### Construction

Measures the structural cost of governance during system evolution.

Primary evidence:

```text
benchmark/manifests/{strategy}/{arm}/{replication}/{step}/manifest.json
```

### Reconstruction

Measures the auditability value created by the evidence preserved during construction.

Primary evidence:

```text
benchmark/reconstruction/{condition}/{strategy}/{arm}/{replication}
audit/{condition}/{strategy}/{arm}/{replication}/audit_result.json
```

### Contract audit

Measures whether benchmark traces satisfy explicit governance rules.

Primary implementation:

```text
tools/governor/
```

## Related Notes

- `EVALUATION_NOTES.md`
  Overview of how construction, reconstruction, and contract audit fit together.

- `RESULTS_ARMS.md`
  Construction benchmark summary.

- `RESULTS_AUDIT.md`
  Reconstruction benchmark summary.

- `RESULTS_COMBINED.md`
  Combined interpretation of both exercises.

- `MULTI_LLM_BENCHMARK_PLAN.md`
  Planning note for a future extension with explicit builder/auditor model factors.
