# Contract Experiment

## Research Question

Can a minimal benchmark scaffold be extended into an empirical evaluation of Agent Contracts and an Agent Governor without redesigning the benchmark family?

This repository clone does not contain the historical experiment branches, so the empirical layer here materializes a deterministic benchmark dataset with the same canonical shape: four arms, two strategies, three replications, 24 trajectories, and 84 manifests.

## Hypotheses

- H1: Contract-governed trajectories produce higher direct audit evidence than no-contract and documentation-only trajectories.
- H2: The Agent Governor detects injected contract violations with high precision and recall.
- H3: Contract-governed trajectories introduce measurable co-evolution overhead.
- H4: Contract validation has low symbolic overhead over structured execution traces.

## Experimental Design

The benchmark retains the existing interpretation but renames the empirical framing:

- `base`: no-contract baseline
- `agent-card`: documentation-only governance
- `contract-first`: contract-governed evolution
- `contract-flow`: contract + workflow-governed evolution

Strategies:

- `evolutionary`: six step manifests per trajectory from `C1` through `C6`
- `final-spec`: one `C6` manifest per trajectory

Replications:

- `rep01`
- `rep02`
- `rep03`

The materialized benchmark structure is:

```text
benchmark/
  baseline/
  prompts/
  arms/
  manifests/
  oracle/
contracts/
tools/governor/
tools/violation_injection/
results/
docs/
```

## Contracts

Each arm has one executable contract in `contracts/`:

- `base.yaml`
- `agent_card.yaml`
- `contract_first.yaml`
- `contract_flow.yaml`

Each contract specifies:

- `contract_id`
- `applies_to_arm`
- `required_artifacts`
- `required_manifest_fields`
- `preconditions`
- `invariants`
- `postconditions`
- `violation_rules`

The rules support the thesis claim that Agent Contracts do not primarily reduce change spread. Instead, they make evolution contract-checkable, violation-detectable, and auditable, while exposing governance overhead and validation cost.

## Governor

The Agent Governor is a post-hoc validator over structured traces. It loads a contract YAML file and a benchmark manifest, checks required fields and artifact conditions, and emits a structured JSON verdict with violations, a deterministic fingerprint, and validation latency.

CLI entry points:

```bash
python -m tools.governor.materialize_benchmark --out .
python -m tools.governor.validate --manifest benchmark/manifests/evolutionary/base/rep01/C1/manifest.json --contract contracts/base.yaml
python -m tools.governor.validate_all --runs benchmark/manifests --contracts contracts --out results/governor_results.jsonl
```

## Valid-Trace Validation

The canonical generated manifests are the valid-trace dataset. They are expected to pass contract validation:

- `traceability_ratio = 1.0`
- `contract_violations = 0`
- `test_failures = 0`
- `C6` manifests require `run_ledger_compliance = true`
- governed arms require the appropriate governance artifacts and evidence in `changed_files`

## Violation-Injection Validation

The injected-violation dataset is generated from valid traces:

```bash
python -m tools.violation_injection.generate --input-runs benchmark/manifests --out mutated_runs
python -m tools.violation_injection.evaluate --mutated-runs mutated_runs --contracts contracts --out results/violation_detection_summary.json
```

Supported mutation types:

- `missing_required_artifact`
- `missing_run_ledger`
- `wrong_traceability_ratio`
- `nonzero_contract_violations`
- `nonzero_test_failures`
- `missing_contracts_md`
- `missing_workflow_md`
- `capability_present_but_not_declared`
- `inconsistent_arm_contract`
- `fingerprint_mismatch`

Each mutated manifest stores `_mutation` metadata with a mutation identifier, source manifest, expected verdict, and expected rule ID.

## Metrics

Governor summary metrics:

- total manifests
- pass count
- fail count
- compliance rate by arm
- median latency
- p95 latency
- max latency

Violation-detection metrics:

- true positives
- false positives
- true negatives
- false negatives
- precision
- recall
- F1
- detection rate by mutation type
- detection rate by arm

## Expected Interpretation

The intended interpretation is deliberately narrow:

- the benchmark demonstrates post-hoc contract-governor checking over structured traces
- the benchmark does not demonstrate full live runtime enforcement in LangGraph, CrewAI, AutoGen, or MCP
- the benchmark does not claim production readiness
- Agent Types remain conceptual or classification-oriented in this repository

This makes the empirical contribution suitable for a thesis or paper section focused on Agent Contracts and the Agent Governor as auditable governance instrumentation rather than comprehensive runtime control.
