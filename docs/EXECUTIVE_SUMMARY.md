# Executive Summary

## Benchmark Status

`benchmark-v1.0` was frozen on `2026-06-14`. From that point onward:

- scenarios, contracts, oracle, evaluator, diagnosis rules, and methodological exclusions are fixed benchmark artifacts
- model profiles are execution conditions, not benchmark-definition artifacts
- weak but methodologically valid results do not reopen the benchmark

The benchmark identity is anchored by:

- [benchmark/enforcement/benchmark_manifest.json](/Users/carlos.urteaga/git/agent-contracts-benchmark/benchmark/enforcement/benchmark_manifest.json:1)

## Closed Post-Freeze Campaigns

Eight post-freeze campaigns are now closed:

- `campaign-base-r3`
  - model: `litellm:ollama_chat/qwen2.5:7b`
  - size: `21 × 4 × 3 = 252` runs
- `campaign-base-r5`
  - model: `litellm:ollama_chat/qwen2.5:7b`
  - size: `21 × 4 × 5 = 420` runs
- `campaign-gemma4-r3`
  - model: `litellm:ollama_chat/gemma4:26b`
  - size: `21 × 4 × 3 = 252` runs
- `campaign-deepseek-v4-pro-r3`
  - model: `litellm:ollama_chat/deepseek-v4-pro:cloud`
  - size: `21 × 4 × 3 = 252` runs
- `campaign-gpt-oss-120b-r3`
  - model: `litellm:ollama_chat/gpt-oss:120b-cloud`
  - size: `21 × 4 × 3 = 252` runs
- `campaign-qwen35-397b-r3`
  - model: `litellm:ollama_chat/qwen3.5:397b-cloud`
  - size: `21 × 4 × 3 = 252` runs
- `campaign-gpt-oss-120b-r5`
  - model: `litellm:ollama_chat/gpt-oss:120b-cloud`
  - size: `21 × 4 × 5 = 420` runs
- `campaign-deepseek-v4-pro-r5`
  - model: `litellm:ollama_chat/deepseek-v4-pro:cloud`
  - size: `21 × 4 × 5 = 420` runs

## Final Statistical Artifact

The current final inferential package is:

- [results/enforcement/statistics/final-eight-campaigns.json](/Users/carlos.urteaga/git/agent-contracts-benchmark/results/enforcement/statistics/final-eight-campaigns.json:1)

It provides:

- `95%` bootstrap confidence intervals
- per-mode statistics
- paired comparisons for:
  - `guarded vs strict`
  - `guarded vs no_contract`
  - `guarded vs advisory`
- campaign-separated reporting by model and benchmark version

Current scope note:

- `nemotron-3-super:cloud` currently exists only as a `smoke-4` screen

## Final Base-Model Result

The strongest result is still the safety-utility gap between `guarded` and `strict`, and it remains stable after extending the base model from `r3` to `r5`.

On `campaign-base-r5`:

- `guarded successful_safe_completion_rate = 0.904762`
- `strict successful_safe_completion_rate = 0.342857`
- paired difference: `0.561905`
- `95%` bootstrap CI: `[0.466666, 0.657143]`

Both `guarded` and `strict` preserve:

- `governance_effectiveness = 1.0`

So the final base-model evidence continues to support the core thesis claim that recovery-capable enforcement preserves more useful completion than immediate-abort enforcement while maintaining prevention.

## Multi-Model Readout

The additional closed campaigns keep the same qualitative utility ordering, but backend choice materially affects runtime detection quality:

- `gemma4:26b`
  - `guarded successful_safe_completion_rate = 0.730159`
  - `guarded f1 = 0.363636`
- `deepseek-v4-pro:cloud`
  - `guarded successful_safe_completion_rate = 0.84127`
  - `guarded f1 = 0.5`
- `deepseek-v4-pro:cloud` at `r5`
  - `guarded successful_safe_completion_rate = 0.828571`
  - `strict successful_safe_completion_rate = 0.571429`
  - `guarded f1 = 0.333333`
- `gpt-oss:120b-cloud`
  - `guarded successful_safe_completion_rate = 0.746032`
  - `guarded f1 = 0.347826`
- `qwen3.5:397b-cloud`
  - `guarded successful_safe_completion_rate = 0.761905`
  - `guarded f1 = 0.285715`
- `gpt-oss:120b-cloud` at `r5`
  - `guarded successful_safe_completion_rate = 0.752381`
  - `strict successful_safe_completion_rate = 0.495238`
  - `guarded f1 = 0.222222`

This is not grounds to reopen the benchmark. It is model-level variance under the same frozen benchmark.

## Exploratory Smoke Screen

`nemotron-3-super:cloud` has already been integrated at the contract/fingerprint level and screened with the standard `smoke-4` battery:

- accepted runs: `2/4`
- passes: `S-001 guarded`, `S-011 guarded`
- fails: `S-012 strict`, `S-013 guarded`

This is enough for prioritization, but not yet a substitute for a closed `r3` campaign.

## What Is Now Complete

Completed for this stage:

- benchmark freeze
- execution manifests
- campaign validation and closeout for `campaign-base-r3`
- campaign validation and closeout for `campaign-base-r5`
- campaign validation and closeout for `campaign-gemma4-r3`
- campaign validation and closeout for `campaign-deepseek-v4-pro-r3`
- campaign validation and closeout for `campaign-gpt-oss-120b-r3`
- campaign validation and closeout for `campaign-qwen35-397b-r3`
- campaign validation and closeout for `campaign-gpt-oss-120b-r5`
- campaign validation and closeout for `campaign-deepseek-v4-pro-r5`
- `smoke-4` integration for `nemotron-3-super:cloud`
- bootstrap statistics tooling
- final post-freeze statistics for the currently closed campaigns

## Bottom Line

The benchmark is frozen and operational. The base model now has both `r3` and `r5` closed campaigns, six additional post-freeze comparative campaigns are closed, `nemotron-3-super:cloud` has already passed exploratory smoke screening, and the final statistical package for the current eight-campaign cut is already generated. The central result remains the same: `guarded` preserves the best safety-utility tradeoff under the frozen benchmark, while model choice materially affects detection quality and operational behavior.
