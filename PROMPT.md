You are executing the benchmark work required for the current branch.

Infer trajectory metadata from the current Git branch by running:

```bash
git branch --show-current
```

Expected branch formats:

```text
exp/evolutionary/{arm}/{replication}
exp/final-spec/{arm}/{replication}
```

Parse branch parts split by `/`:

```text
parts[0] = exp
parts[1] = strategy
parts[2] = arm
parts[3] = replication
```

Set:

```text
strategy = parts[1]
arm = parts[2]
replication = parts[3]
agent_executor = codex
```

If the branch does not match one of the expected formats, stop and report the mismatch.

Read these files before acting:
- `BENCHMARK_SPEC.md`
- `CHANGE_PROTOCOL.md`
- `STEP_PROTOCOL.md`
- `ARCHITECTURE_ARMS.md`
- `ARM_INSTRUCTIONS.md`
- `METRICS_SPEC.md`
- `IMPLEMENTATION_PLAN.md`

Execution mode:
- If `strategy = evolutionary`:
  - implement only the next incomplete step in `IMPLEMENTATION_PLAN.md`
  - use that step as `step_id`
  - do not implement future steps early
  - stop after one step
- If `strategy = final-spec`:
  - implement the direct final target for that branch
  - do not replay intermediate steps
  - use `C6` as `step_id` unless `IMPLEMENTATION_PLAN.md` defines a more specific final-spec step id
  - stop after one completed final-spec build step

Arm rules:
- If `arm = base`:
  - do not add `AGENT_CARD.md`
  - do not add `CONTRACTS.md`
  - do not add `WORKFLOW.md`
- If `arm = agent-card`:
  - maintain `AGENT_CARD.md`
  - update `AGENT_CARD.md` whenever the step changes role, outputs, tools, memory, reviewer, or governance behavior
  - do not add `CONTRACTS.md` or `WORKFLOW.md`
- If `arm = contract-first`:
  - update `CONTRACTS.md` before code changes
  - do not add `WORKFLOW.md` unless explicitly required by the benchmark step
- If `arm = contract-flow`:
  - update `CONTRACTS.md` and `WORKFLOW.md` before code changes
  - keep implementation consistent with both files

General execution rules:
- run tests
- fix failures only for the current step
- write exactly one manifest at:

```text
benchmark/manifests/{strategy}/{arm}/{replication}/{step_id}/manifest.json
```

Compatibility note:

```text
runs/{strategy}/{arm}/{replication}/{step_id}/manifest.json
```

- the manifest must include:
  - `changed_files`
  - `changed_file_count`
  - normalized `change_spread`
- use:
  - `changed_file_count = len(changed_files)`
  - `total_tracked_files = count(git ls-files)` at the pre-step commit
  - `change_spread = changed_file_count / total_tracked_files`
- update `IMPLEMENTATION_PLAN.md`
- commit after the completed step
- stop
