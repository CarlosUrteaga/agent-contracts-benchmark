# Benchmark Specification

## Research Objective

Evaluate how architectural formalization interacts with development strategy in governed agentic systems. The primary comparison is whether explicit contracts and workflow structure make software evolution contract-checkable, violation-detectable, and auditable, while exposing governance overhead, under:

- incremental evolution from `T0` through `C6`
- direct implementation from the final `C6` specification

## Benchmark Target

The target product is an `Enterprise Policy Assistant`.

Required final capabilities:

1. RAG over fixed policy documents.
2. Structured response schema with confidence and sources.
3. `create_ticket` tool.
4. Approval workflow for sensitive requests.
5. User memory.
6. Reviewer or critic role.
7. Mandatory run ledger.

## Experimental Factors

Architecture arms:

- `base`: no-contract baseline
- `agent-card`: documentation-only governance
- `contract-first`: contract-governed evolution
- `contract-flow`: contract + workflow-governed evolution

Development strategies:

- `evolutionary`
- `final-spec`

Replications:

- `rep01`
- `rep02`
- `rep03`

## Branch Lineage

The intended lineage is:

`main -> benchmark-specs -> t0-common -> arm/{arm} -> exp/{strategy}/{arm}/repXX`

`benchmark-specs` denotes the initial protocol branch or commit. It does not need to remain a permanent branch after the scaffold is established.

## Current Scope

This scaffold phase defines only protocol assets, templates, validation checks, and branch-planning logic.

Out of scope for this phase:

- full live runtime enforcement in LangGraph, CrewAI, AutoGen, or MCP
- production-readiness claims
- full Agent Types enforcement
