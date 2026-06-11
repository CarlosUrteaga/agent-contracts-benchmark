# Evaluation Notes

## Purpose

This file records the current evaluation structure of the project so that `main` preserves not only the benchmark scaffold, but also the reasoning behind the evaluation workflow.

## Main Empirical Structure

The project should be understood as two main empirical exercises plus one complementary validation layer.

### 1. Construction Benchmark

The construction benchmark evaluates how different architectural arms affect software evolution under controlled changes.

Key factors:

- `arm`
  - `base`
  - `agent-card`
  - `contract-first`
  - `contract-flow`
- `strategy`
  - `evolutionary`
  - `final-spec`
- `replication`
  - `rep01`
  - `rep02`
  - `rep03`

Primary outputs:

```text
benchmark/manifests/{strategy}/{arm}/{replication}/{step}/manifest.json
```

Main evaluation questions:

- How much co-evolution overhead does governance introduce?
- How much does governance affect changed-file count and change spread?
- Does the benchmark remain valid under the expected protocol and oracle checks?

### 2. Reconstruction Benchmark

The reconstruction benchmark evaluates whether a later auditor can reconstruct implemented capabilities from preserved evidence.

Key factors:

- `condition`
  - `minimal`
  - `governance`
  - `code-artifacts`
- inherited benchmark factors:
  - `strategy`
  - `arm`
  - `replication`

Filesystem-first reconstruction cases:

```text
benchmark/reconstruction/{condition}/{strategy}/{arm}/{replication}
```

Primary outputs:

```text
audit/{condition}/{strategy}/{arm}/{replication}/audit_result.json
```

Main evaluation questions:

- Can the auditor correctly recover the implemented capabilities?
- How strong is the evidence used to justify each reconstruction?
- How does evidence quality change across `minimal`, `governance`, and `code-artifacts`?

### 3. Contract Audit Layer

The contract-audit layer validates benchmark manifests against explicit governance rules over structured traces.

Implementation location:

```text
contracts/
tools/governor/
tools/violation_injection/
```

Primary function:

- validate manifests against arm-specific YAML contracts
- report compliance and violations
- measure symbolic validation overhead
- evaluate injected violations with precision and recall summaries

Main evaluation questions:

- Do benchmark traces satisfy the intended governance contracts?
- Can contract mismatches be detected automatically?
- Is contract validation cheap enough to be practical?

## Recommended Interpretation

The evaluation should not be framed as three unrelated studies.

Instead:

- the construction benchmark produces the trajectories and manifests
- the reconstruction benchmark consumes preserved evidence from those trajectories
- the contract-audit layer validates whether those trajectories conform to explicit governance rules

This validation layer should not be interpreted as full live runtime enforcement inside LangGraph, CrewAI, AutoGen, or MCP.

## Results Summaries

Current narrative summaries:

- `RESULTS_ARMS.md`
- `RESULTS_AUDIT.md`
- `RESULTS_COMBINED.md`

## Fresh-Machine Expectation

From a fresh machine, `main` should preserve enough information to recover:

- how to generate construction branches
- how construction outputs are named and stored
- how reconstruction cases are derived from final manifests
- how reconstruction outputs are named and stored
- how contract validation is run over benchmark manifests

The documentation on `main` should make the full benchmark family legible:

- construction
- reconstruction
- audit
