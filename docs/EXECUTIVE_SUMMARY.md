# Executive Summary

## Benchmark Status

`benchmark-v1.0` was frozen on `2026-06-14`. From that point onward:

- scenarios, contracts, oracle, evaluator, diagnosis rules, and methodological exclusions are fixed benchmark artifacts
- model profiles are execution conditions, not benchmark-definition artifacts
- weak but methodologically valid results do not reopen the benchmark

The benchmark identity is anchored by:

- [benchmark/enforcement/benchmark_manifest.json](/Users/carlos.urteaga/git/agent-contracts-benchmark/benchmark/enforcement/benchmark_manifest.json:1)

## Canonical Post-Freeze Evidence

The current canonical cut contains seventeen closed campaigns:

- `campaign-base-r3`
- `campaign-base-r5`
- `campaign-gemma4-r3`
- `campaign-deepseek-v4-pro-r3`
- `campaign-gpt-oss-120b-r3`
- `campaign-qwen35-397b-r3`
- `campaign-gpt-oss-120b-r5`
- `campaign-deepseek-v4-pro-r5`
- `campaign-kimi-k26-r3`
- `campaign-kimi-k26-r5`
- `campaign-kimi-k27-code-r3`
- `campaign-kimi-k27-code-r5`
- `campaign-nemotron-3-ultra-r3`
- `campaign-nemotron-3-ultra-r5`
- `campaign-openai-direct-r3`
- `campaign-qwen35-4b-r3`
- `campaign-qwen35-4b-r5`

The current inferential artifact is:

- [results/enforcement/statistics/final-seventeen-campaigns.json](/Users/carlos.urteaga/git/agent-contracts-benchmark/results/enforcement/statistics/final-seventeen-campaigns.json:1)

It now uses `bootstrap-metrics-v2` and adds recovery and overhead metrics on top of the original prevention and detection package.

Explicitly out of scope for the canonical cut:

- `results/enforcement/smoke-gemma4-31b-cloud-rerun/`
- `results/enforcement/smoke-gemma4-31b-cloud-rerun2/`
- `results/enforcement/smoke-nemotron-3-super-cloud/`
## H1 — Blocking enforcement reduces unsafe committed side effects

Where the frozen benchmark produces blocking opportunities, `guarded` and `strict` continue to prevent unsafe committed side effects relative to `no_contract` and `advisory`.

On `campaign-base-r5`:

- `no_contract unsafe_side_effect_rate = 1.0`
- `advisory unsafe_side_effect_rate = 1.0`
- `guarded unsafe_side_effect_rate = 0.0`
- `strict unsafe_side_effect_rate = 0.0`
- `guarded governance_effectiveness = 1.0`
- `strict governance_effectiveness = 1.0`

The same pattern holds in `campaign-deepseek-v4-pro-r5`. Some backends do not surface enough opportunities to define every contrast in every mode, but that is a model-level limitation, not a benchmark inconsistency.

## H2 — Runtime detection quality is backend-sensitive

`H2` is reported descriptively, not as a formal equivalence claim.

The base model remains relatively aligned:

- `campaign-base-r5 advisory f1 = 0.714286`
- `campaign-base-r5 guarded f1 = 0.789474`
- `campaign-base-r5 strict f1 = 0.714286`

But the multi-model cut shows clear backend variance:

- `deepseek-v4-pro-r5`: `0.125001 / 0.333333 / 0.181818`
- `gpt-oss-120b-r5`: `0.4 / 0.222222 / 0.121213`
- `gemma4-r3`: `0.363636 / 0.363636 / 0.0`
- `kimi-k2.6 r3`: `0.285715 / 0.285715 / 0.285715`
- `kimi-k2.6 r5`: `0.235294 / 0.285715 / 0.285715`
- `kimi-k2.7-code r3`: `0.285715 / 0.285715 / 0.285715`
- `kimi-k2.7-code r5`: `0.285715 / 0.285715 / 0.285715`
- `nemotron-3-ultra r3`: `0.434783 / 0.5 / 0.2`
- `qwen35-r3`: `0.105264 / 0.285715 / 0.0`

The benchmark is therefore stable enough to expose runtime-detection differences, but those differences are materially model-dependent.

## H3 — `guarded` preserves more useful completion than `strict`

This remains the strongest thesis result.

On `campaign-base-r5`:

- `guarded successful_safe_completion_rate = 0.904762`
- `strict successful_safe_completion_rate = 0.342857`
- paired difference `= 0.561905`
- `95%` bootstrap CI `= [0.466666, 0.657143]`
- `guarded recovery_rate_after_block = 0.875`

The same qualitative ordering persists across the non-base campaigns. The benefit is not explained by weaker prevention, because both blocking modes retain `governance_effectiveness = 1.0` where the opportunity exists.

## H4 — Recovery-capable enforcement has measurable operational overhead

The new `v2` artifact shows that `guarded` pays an operational cost for preserving completion:

- on `campaign-base-r5`, `guarded vs strict mean_latency_ms = 72593.895325`
- on `campaign-base-r5`, `guarded vs strict mean_token_usage = 1559.047619`
- on `deepseek-v4-pro-r5`, the same differences remain positive but much smaller

The current artifact does not support a meaningful monetary comparison because the active adapters normalize missing cost to `0.0`. `H4` is therefore supported here as a latency/token/iteration result, not a cost-accounting result.

## Bottom Line

The benchmark is frozen, the seventeen-campaign cut is closed, and the post-freeze analysis now supports `H1–H4` directly from the canonical inferential artifact. The main claim remains unchanged: `guarded` preserves the best safety-utility tradeoff under the frozen benchmark, while runtime-detection quality and operational behavior vary materially by backend.
