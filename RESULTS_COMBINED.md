# Combined Results Interpretation

The repository now supports three connected empirical layers on `main`:

1. Construction traces under four governance arms
2. Reconstruction evidence bundles under three conditions
3. Post-hoc contract validation and violation detection

## Current Baseline Metrics

- Construction QC: `84` manifests and `24` trajectories, status `pass`
- Governor validation: `84 / 84` canonical manifests pass
- Governor latency: median `1.246447 ms`, p95 `2.070647 ms`
- Violation detection: precision `1.0`, recall `1.0`, F1 `1.0`
- Reconstruction baseline scoring: `72 / 72` exact matches on deterministic audit fixtures

## Thesis-Safe Reading

The current results support a narrow claim:

- contract-governed traces are machine-checkable
- injected violations are automatically detectable in the deterministic baseline
- validation overhead is low
- reconstruction evidence can be packaged and scored reproducibly

The current results do not establish live runtime enforcement or real-auditor reconstruction quality.

## Source Artifacts

- `results/governor_summary.json`
- `results/violation_detection_summary.json`
- `results/reconstruction_summary.json`
- `results/qc_report.json`
