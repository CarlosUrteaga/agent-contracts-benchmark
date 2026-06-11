# Multi-LLM Benchmark Extension Plan

This note records a future extension path for the benchmark once the single-builder scaffold is stable.

## Candidate Axes

- builder model family
- auditor model family
- contract-checker model assistance level
- temperature and retry policy

## Candidate Questions

- Do stronger governance artifacts reduce variance across different builder models?
- Does reconstruction accuracy depend more on the evidence bundle or on the auditor model?
- Can contract-governor checks remain stable when generation quality varies?

## Current Status

This extension is intentionally out of scope for the thesis-ready scaffold on `main`.

The current repository keeps a single deterministic baseline so that construction, reconstruction, and contract-audit workflows remain reproducible.
