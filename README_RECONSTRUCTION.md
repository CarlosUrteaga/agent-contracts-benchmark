# Reconstruction Benchmark

The reconstruction benchmark evaluates whether preserved evidence from completed construction trajectories is sufficient for a later auditor to recover implemented capabilities.

## Canonical Layout

Filesystem-first reconstruction cases are generated under:

```text
benchmark/reconstruction/{condition}/{strategy}/{arm}/{replication}/
```

Deterministic baseline audit fixtures are generated under:

```text
audit/{condition}/{strategy}/{arm}/{replication}/audit_result.json
```

## Commands

Generate reconstruction cases and deterministic baseline audit fixtures:

```bash
python3 scripts/create_reconstruction_branches.py --apply
```

Validate the generated cases:

```bash
python3 scripts/validate_reconstruction_branches.py --root benchmark/reconstruction
```

Score the audit results:

```bash
python3 scripts/score_reconstruction_audits.py --audit-root audit --oracle benchmark/oracle/trajectory_oracles.json --out results/reconstruction_summary.json
```

## Conditions

- `minimal`: manifest plus step note only
- `governance`: minimal evidence plus governance artifacts and run ledger
- `code-artifacts`: governance evidence plus selected repo artifacts

## Scope

This reconstruction pipeline is a deterministic scaffold on `main`. It validates evidence packaging and scoring behavior. It does not claim that the included baseline audit fixtures represent independent live auditor performance.
