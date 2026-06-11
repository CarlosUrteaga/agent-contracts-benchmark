# Architecture Arms

## Arm A: `base`

Interpretation: no-contract baseline.

Implement the system functionally. Do not add explicit architectural contracts beyond what is strictly necessary for code correctness.

## Arm B: `agent-card`

Interpretation: documentation-only governance.

Maintain an `AGENT_CARD.md` that documents:

- role
- inputs
- outputs
- tools
- memory
- limits
- monitoring expectations

The implementation may evolve freely, but the card must be updated to preserve traceability.

## Arm C: `contract-first`

Interpretation: contract-governed evolution.

Define explicit schemas, interfaces, preconditions, postconditions, and tool contracts before implementation. The benchmark should measure whether these contracts make evolution contract-checkable, violation-detectable, and auditable.

## Arm D: `contract-flow`

Interpretation: contract + workflow-governed evolution.

Define the same contracts as `contract-first`, plus an explicit workflow or state graph governing execution transitions. This arm adds control-flow formalization on top of contract discipline.

## Arm Baseline Rule

Each arm baseline is derived from `t0-common` and then used as the parent for all experiment branches in that arm.
