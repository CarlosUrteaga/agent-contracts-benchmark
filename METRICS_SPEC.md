# Metrics Specification

## Manifest Metrics

Each trajectory step records the following fields in its manifest:

- `step_id`
- `status`
- `agent_executor`
- `prompt_hash`
- `benchmark_spec_hash`
- `commit_sha`
- `arm`
- `strategy`
- `replication`
- `changed_files`
- `changed_file_count`
- `lines_added`
- `lines_deleted`
- `change_spread`
- `test_failures`
- `rework_iterations`
- `contract_violations`
- `traceability_ratio`
- `orphan_artifacts`
- `run_ledger_compliance`
- `capabilities_present`
- `governance_artifacts_present`

## Enumerated Fields

- `step_id`: `T0 | C1 | C2 | C3 | C4 | C5 | C6`
- `status`: `pending | completed | failed`
- `agent_executor`: `ralph-loop | codex`

## Metric Intent

- `changed_files`: file paths touched by the step
- `changed_file_count`: number of changed files
- `lines_added`: total inserted lines
- `lines_deleted`: total removed lines
- `change_spread`: `changed_file_count / total_tracked_files`
- `test_failures`: failing tests after implementation or repair attempts
- `rework_iterations`: fix loops required before step completion
- `contract_violations`: contract mismatches detected during execution
- `traceability_ratio`: fraction of changed artifacts linked back to benchmark intent
- `orphan_artifacts`: artifacts with no justified linkage
- `run_ledger_compliance`: whether ledger recording is complete and valid

## Manifest Path

Each benchmark step writes exactly one manifest to:

`benchmark/manifests/{strategy}/{arm}/{replication}/{step}/manifest.json`

Compatibility note for older branch-local runs:

`runs/{strategy}/{arm}/{replication}/{step_id}/manifest.json`

## Change Spread Denominator

`total_tracked_files` is the count returned by `git ls-files` at the pre-step commit.

## Template Requirement

The protocol scaffold provides JSON templates for manifests and run ledgers. Execution scripts may instantiate these templates per run directory without changing the schema.
