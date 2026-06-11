# Step Protocol

This document defines the operational rules for each benchmark step. It is the authoritative step-by-step protocol for coding agents.

## Global Rules

- Implement only the assigned step.
- Do not implement future capabilities early.
- Preserve previous behavior unless the current step explicitly changes it.
- Run tests after each step.
- Fix failures only for the current step.
- Write exactly one manifest at:

`benchmark/manifests/{strategy}/{arm}/{replication}/{step}/manifest.json`

- Update `IMPLEMENTATION_PLAN.md` after completing the step.
- Commit after each completed step.
- Stop after one step.

## T0 — Basic RAG Assistant

### Add

- fixed policy document corpus
- simple deterministic retrieval
- grounded answer generation

### Do not add

- confidence
- sources
- tools
- approval workflow
- memory
- reviewer
- run ledger

## C1 — Structured Response

### Add

- `confidence: float`
- `sources: list` of source references

### Preserve

- answer
- basic RAG behavior

### Do not add

- tools
- approval workflow
- memory
- reviewer
- run ledger

## C2 — Ticket Tool

### Add

- `create_ticket(category, description, priority)`
- support and equipment request detection
- ticket payload in the response

### Preserve

- C1 structured response
- normal policy lookup behavior

### Do not add

- approval workflow
- memory
- reviewer
- run ledger

## C3 — Approval Workflow

### Add

- approval workflow for sensitive requests
- approval payload in the response
- pause-before-ticket behavior for sensitive requests

### Sensitive Requests

- equipment requests are cost-sensitive
- support requests are access-sensitive only when they involve:
  - `vpn`
  - `unlock`
  - `admin`
  - `permissions`
  - `privileged access`
  - `security exception`

### Preserve

- non-sensitive support tickets
- policy lookup behavior
- fallback behavior

### Do not add

- memory
- reviewer
- run ledger
- approval decision API
- persistence

## C4 — In-Memory User Profiles

### Add

- explicit in-memory user profiles
- `update_user_profile(...)`
- `get_user_profile(...)`
- optional `user_id` in `answer(...)`
- profile lookup responses for fixed profile queries

### Profile Fields

- `user_id`
- `name`
- `department`
- `work_mode`

### Preserve

- RAG behavior
- ticket behavior
- approval behavior

### Do not add

- natural-language profile extraction
- personalization of RAG, ticket, or approval outputs
- reviewer
- run ledger
- persistence
- approval decision API

## C5 — Reviewer/Critic

### Add

- deterministic internal reviewer
- invariant-based validation before returning responses

### Reviewer Checks

- response schema validity
- document grounding for policy answers
- ticket category correctness
- approval-gated requests do not create tickets
- profile data is not exposed in unrelated flows

### Preserve

- public response shape
- RAG behavior
- ticket behavior
- approval behavior
- memory behavior

### Do not add

- run ledger
- persistence
- approval decision API
- reviewer metadata in `AssistantResponse`

## C6 — Run Ledger

### Add

- mandatory in-memory run ledger
- exactly one ledger entry per successful `answer()` call
- `get_run_ledger()`

### Ledger Behavior

- success-only
- assistant-instance-local
- in-memory only
- no external persistence

### Required Ledger Fields

- `run_id`
- `user_query`
- `user_id`
- `classification`
- `documents_used`
- `tools_called`
- `approval_required`
- `approval_reason`
- `reviewer_decision`
- `final_status`

### Preserve

- public `AssistantResponse` behavior
- RAG behavior
- ticket behavior
- approval behavior
- memory behavior
- reviewer behavior

### Do not add

- external persistence
- approval decision API
- ledger data inside `AssistantResponse`

## Final-Spec Trajectories

- `final-spec` branches target the final `C6` system directly.
- They do not replay the intermediate `C1` to `C5` step implementations.
