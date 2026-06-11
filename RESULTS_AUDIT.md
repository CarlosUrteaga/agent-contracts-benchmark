# Reconstruction Results

The filesystem-first reconstruction scaffold generates `72` cases:

- `24` trajectories
- `3` conditions: `minimal`, `governance`, `code-artifacts`

## Deterministic Baseline Audit Fixtures

The baseline audit fixtures score as exact matches for all cases:

- Total audits: `72`
- Exact-match count: `72`
- Exact-match rate: `1.0`
- Exact-match rate by condition: `1.0` for `minimal`, `governance`, and `code-artifacts`

## Interpretation

These scores validate the reconstruction packaging and scoring pipeline on `main`.

They should be interpreted as deterministic scaffold behavior, not as independent evidence of human or live-LLM auditor performance.

## Source Artifacts

- `benchmark/reconstruction/`
- `audit/`
- `results/reconstruction_summary.json`
