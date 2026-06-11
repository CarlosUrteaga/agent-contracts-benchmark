# Construction Results

The canonical deterministic corpus contains `84` manifests across `24` trajectories.

## Current Construction Baseline

- Manifest QC status: pass
- Total manifests: `84`
- Total trajectories: `24`
- Governor valid-trace pass rate: `84 / 84`
- Compliance by arm: `1.0` for `base`, `agent-card`, `contract-first`, and `contract-flow`

## Interpretation

These results confirm that the generated benchmark corpus is internally consistent and that all canonical traces satisfy their arm-specific contracts.

The deterministic corpus is a reproducibility baseline, not evidence of live agent behavior under noisy execution.

## Source Artifacts

- `results/qc_report.json`
- `results/governor_summary.json`
- `results/manifest_rows.csv`
