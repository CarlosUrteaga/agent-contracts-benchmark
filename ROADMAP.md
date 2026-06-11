# Thesis-Readiness Roadmap

This roadmap defines the work required to make `main` defense-ready as a complete, reproducible empirical benchmark.

## Milestone 1: Repo Hardening

- Add `pyproject.toml` and preserve stdlib-only runtime execution.
- Remove broken documentation references and make `README.md` the clear human entry point.
- Ensure tests do not mutate tracked benchmark artifacts in place.
- Keep generated artifacts and caches clearly separated from canonical source files.

## Milestone 2: Shared Benchmark Spec

- Maintain one canonical `benchmark/step_capabilities.yaml` file for step semantics.
- Convert contract files to real YAML while preserving current keys and behavior.
- Refactor benchmark materialization, validation, and mutation tooling to consume the shared spec.
- Keep manifest semantics aligned across docs, templates, and code.

## Milestone 3: Reconstruction Pipeline

- Add manifest aggregation over `benchmark/manifests`.
- Add filesystem-first reconstruction case generation under `benchmark/reconstruction/`.
- Add reconstruction validation, scoring, oracle data, prompt template, and tests.
- Keep branch-based reconstruction as a documented extension rather than the canonical workflow on `main`.

## Milestone 4: Results Narrative

- Add missing results files and the multi-LLM planning note.
- Write the narratives from current generated outputs and documented limitations.
- Preserve a narrow empirical claim: cheap post-hoc contract validation over structured traces, not live runtime enforcement.

## Milestone 5: Empirical Strengthening

- Add CI for protocol validation, tests, and governor runs.
- Add subtler mutation scenarios and, if needed later, imperfect real-trace fixtures.
- Treat this milestone as journal-strengthening work, not a blocker for thesis readiness.

## Defense Gate

The repository is defense-ready when all of the following are true:

- The protocol validator passes.
- The canonical benchmark corpus regenerates deterministically.
- Governor and violation-injection results reproduce current baseline behavior.
- Reconstruction runs end to end from filesystem artifacts.
- All referenced files on `main` exist and are internally consistent.
