# Executive Summary

## Benchmark Status

`benchmark-v1.0` was frozen on `2026-06-14`. From that point onward:

- scenarios, contracts, oracle, evaluator, diagnosis rules, and methodological exclusions are fixed benchmark artifacts
- model profiles are execution conditions, not benchmark-definition artifacts
- weak but methodologically valid results do not reopen the benchmark

The benchmark identity is anchored by:

- [benchmark/enforcement/benchmark_manifest.json](/Users/carlos.urteaga/git-clone/Architectural-Contracts/benchmark/enforcement/benchmark_manifest.json:1)

## Closed Post-Freeze Campaigns

Two post-freeze campaigns are already closed:

- `campaign-base-r3`
  - model: `litellm:ollama_chat/qwen2.5:7b`
  - size: `21 × 4 × 3 = 252` runs
- `campaign-gemma4-r3`
  - model: `litellm:ollama_chat/gemma4:26b`
  - size: `21 × 4 × 3 = 252` runs

The target base-model extension `campaign-base-r5` is still pending and remains part of the final closeout gate.

## Current Statistical Artifact

The current inferential package is:

- [results/enforcement/statistics/interim-base-r3-plus-gemma4-r3.json](/Users/carlos.urteaga/git-clone/Architectural-Contracts/results/enforcement/statistics/interim-base-r3-plus-gemma4-r3.json:1)

It provides:

- `95%` bootstrap confidence intervals
- per-mode statistics
- paired comparisons for:
  - `guarded vs strict`
  - `guarded vs no_contract`
  - `guarded vs advisory`
- campaign-separated reporting by model and benchmark version

## Main Interim Result

The strongest current result remains the safety-utility gap between `guarded` and `strict` on the closed base campaign:

- `guarded successful_safe_completion_rate = 0.888889`
- `strict successful_safe_completion_rate = 0.333333`
- paired difference: `0.555556`
- `95%` bootstrap CI: `[0.428572, 0.68254]`

Both `guarded` and `strict` preserve:

- `governance_effectiveness = 1.0`

So the present evidence still supports the core thesis claim that recovery-capable enforcement can preserve more useful completion than immediate-abort enforcement while maintaining prevention.

## Second-Model Readout

The closed Gemma campaign shows that post-freeze analysis is now sensitive to backend behavior rather than benchmark drift:

- `guarded governance_effectiveness = 1.0`
- `guarded precision = 1.0`
- `guarded recall = 0.222222`
- `guarded f1 = 0.363636`

This is not grounds to reopen the benchmark. It is a model-level result under the same frozen benchmark.

## What Is Final vs Interim

Final already completed:

- benchmark freeze
- execution manifests
- campaign validation and closeout for `campaign-base-r3`
- campaign validation and closeout for `campaign-gemma4-r3`
- bootstrap statistics tooling

Still pending before final post-freeze results:

- close `campaign-base-r5`
- regenerate the final statistics package including the extended base campaign
- refresh final result tables and thesis narrative from that complete set

## Bottom Line

The benchmark is frozen and operational. Post-freeze execution is underway with two closed campaigns and a working bootstrap analysis package. The evidence is already thesis-relevant, but the final statistical close for this stage still depends on `campaign-base-r5`.
