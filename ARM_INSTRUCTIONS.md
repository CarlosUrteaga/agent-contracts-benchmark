# Arm Instructions

This document defines operational rules for each architecture arm.

## base

The base arm represents the no-contract baseline.

### Rules

- Do not add `AGENT_CARD.md`.
- Do not add `CONTRACTS.md`.
- Do not add `WORKFLOW.md`.
- Implement functionality directly and straightforwardly.
- Preserve the required benchmark behavior.
- Do not introduce extra structural artifacts unless required by the step.

## agent-card

The agent-card arm represents documentation-only governance.

### Rules

- Maintain `AGENT_CARD.md`.
- Update `AGENT_CARD.md` whenever the system role, inputs, outputs, tools, memory, reviewer, or governance behavior changes.
- `AGENT_CARD.md` must reflect the implemented system.
- Do not add `CONTRACTS.md`.
- Do not add `WORKFLOW.md`.
- Do not implement formal preconditions, postconditions, or flow constraints unless required by functionality.

## contract-first

The contract-first arm represents contract-governed evolution.

### Rules

- Maintain `CONTRACTS.md`.
- Update `CONTRACTS.md` before code changes in each step.
- `CONTRACTS.md` must define relevant schemas, interfaces, preconditions, postconditions, and invariants.
- Implementation must conform to `CONTRACTS.md`.
- Do not add `WORKFLOW.md` unless explicitly required by the benchmark step.
- If behavior changes, update contracts in the same step commit.

## contract-flow

The contract-flow arm represents contract plus workflow-governed evolution.

### Rules

- Maintain `CONTRACTS.md`.
- Maintain `WORKFLOW.md`.
- Update `CONTRACTS.md` and `WORKFLOW.md` before code changes in each step.
- `CONTRACTS.md` must define schemas, interfaces, preconditions, postconditions, and invariants.
- `WORKFLOW.md` must define states, transitions, routing rules, approval paths, reviewer paths, and ledger paths as applicable.
- Implementation must conform to both `CONTRACTS.md` and `WORKFLOW.md`.
- If behavior or routing changes, update both documents in the same step commit.
