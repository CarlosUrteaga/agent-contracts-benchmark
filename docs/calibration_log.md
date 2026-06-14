# Calibration Log

## Purpose

This document records the changes applied during the pre-freeze calibration stage. Its role is to distinguish legitimate methodological stabilization from post-freeze benchmark drift.

## Entry template

### Change

- **Component:**
- **Issue detected:**
- **Change applied:**
- **Methodological reason:**
- **Expected impact:**

## Recorded entries

### Change

- **Component:** Evaluator
- **Issue detected:** Early metric computation mixed action-level counts with run-level denominators, producing invalid rates above `1.0`.
- **Change applied:** Prevention metrics were redefined at the run level and runtime detection was separated from pre/post expectations.
- **Methodological reason:** Headline metrics must be bounded and interpretable.
- **Expected impact:** Stable and valid prevention metrics.

### Change

- **Component:** Scenarios and runtime expectations
- **Issue detected:** Runtime expectations initially mixed with pre/post expectations, reducing interpretability of runtime F1.
- **Change applied:** Runtime expectations were separated from pre-execution and post-execution expectations.
- **Methodological reason:** Runtime F1 must measure runtime detection only.
- **Expected impact:** Cleaner TP/FP/FN accounting and more meaningful F1.

### Change

- **Component:** Guarded recovery behavior
- **Issue detected:** Guarded runs could block unsafe actions but fail to recover into a valid completion path.
- **Change applied:** Structured governor feedback, recovery-ready signaling, and terminal-success handling were introduced.
- **Methodological reason:** Guarded mode is intended to represent recoverable enforcement rather than immediate abort.
- **Expected impact:** Higher valid safe completion under guarded enforcement.

## Freeze rule

After the benchmark is frozen, no methodological change may be applied without:

- creating a new benchmark version
- updating the manifest
- and rerunning the affected experiment campaign
