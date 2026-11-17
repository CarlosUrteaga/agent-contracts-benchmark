# Executive Summary

## Benchmark Status

`benchmark-v1.0` was frozen on `2026-06-14`. From that point onward:

- the 21 scenarios, contract semantics, evaluator, and diagnosis rules stay constant across model conditions; the later oracle documentation and manifest discrepancies are recorded in the identity audit
- model profiles are execution conditions, not benchmark-definition artifacts
- weak but methodologically valid results do not reopen the benchmark

The benchmark identity is anchored by:

- [benchmark/enforcement/benchmark_manifest.json](../benchmark/enforcement/benchmark_manifest.json), with its provenance and limits explained in the [identity audit](benchmark_identity_audit.md)

## Canonical Post-Freeze Evidence

The current canonical cut contains 26 closed historical-runner campaigns (7,728 valid runs):

- `campaign-base-r3`
- `campaign-base-r5`
- `campaign-claude-opus-48-r3`
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
- `campaign-openai-xhigh-r3`
- `campaign-qwen35-4b-r3`
- `campaign-qwen35-4b-r5`
- `campaign-openai-gpt56-luna-low-r3`
- `campaign-openai-gpt56-terra-medium-r3`
- `campaign-openai-gpt56-sol-max-r3`
- `campaign-openai-gpt6-astra-max-r3`
- `campaign-anthropic-claude-haiku-45-moon-r3`
- `campaign-anthropic-claude-sonnet-5-terra-r3`
- `campaign-anthropic-claude-opus-5-sol-r3`

The current inferential artifact is:

- [results/enforcement/statistics/final-twenty-six-campaigns.json](../results/enforcement/statistics/final-twenty-six-campaigns.json)

It uses `bootstrap-metrics-v2` and includes recovery and overhead metrics alongside prevention and detection. The 26 campaigns predate the `vogtcon` runner integration; the new library is not the implementation that generated these historical results.

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

The same pattern holds in `campaign-deepseek-v4-pro-r5`. Across the 26 campaigns, unsafe-effect rates are defined for 19 `no_contract`, 19 `advisory`, 21 `guarded`, and 15 `strict` conditions. Every defined baseline/advisory rate is `1.0`; every defined guarded/strict rate is `0.0`. Undefined cells have no observed opportunity and must not be reported as zero.

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
- `claude-opus-4-8 r3`: `0.0 / 0.0 / 0.0`
- `qwen35-r3`: `0.105264 / 0.285715 / 0.0`

The seven added GPT-5.6, GPT-6, and Claude campaigns extend that variation: guarded F1 is `0.105264` for GPT-5.6 Luna and Terra, `0.285715` for GPT-5.6 Sol, and `0.0` for GPT-6 Astra and the three newer Claude profiles. These values describe observed runtime signal, not a ranking of overall model quality.

`claude-opus-4-8 r3` is best read as a conservative backend rather than a broken one: it preserves nominal completion reasonably well, but it rarely produces the runtime violation opportunities that let `advisory` or `guarded` demonstrate detection behavior.

The benchmark is therefore stable enough to expose runtime-detection differences, but those differences are materially model-dependent.

## H3 — `guarded` preserves more useful completion than `strict`

This remains the strongest thesis result.

On `campaign-base-r5`:

- `guarded successful_safe_completion_rate = 0.904762`
- `strict successful_safe_completion_rate = 0.342857`
- paired difference `= 0.561905`
- `95%` bootstrap CI `= [0.466666, 0.657143]`
- `guarded recovery_rate_after_block = 0.875`

The guarded safe-completion point estimate exceeds strict in all 26 campaigns; the differences range from `0.238095` to `0.730159`. The benefit is not explained by weaker prevention, because both blocking modes retain `governance_effectiveness = 1.0` where the opportunity exists.

## H4 — Recovery-capable enforcement has measurable operational overhead

The new `v2` artifact shows that `guarded` pays an operational cost for preserving completion:

- on `campaign-base-r5`, `guarded vs strict mean_latency_ms = 72593.895325`
- on `campaign-base-r5`, `guarded vs strict mean_token_usage = 1559.047619`
- on `deepseek-v4-pro-r5`, the same differences remain positive but much smaller

Guarded has higher latency and token-usage point estimates than strict in all 26 campaigns; this does not mean every individual contrast has a confidence interval excluding zero. Only four campaigns have nonzero estimated monetary cost; the other 22 report `0.0`, which can reflect absent cost data in some adapters. Cross-provider monetary comparisons are therefore not supported. `H4` is supported as a latency and token result; iteration differences are not positive in every campaign.

## Bottom Line

The 26-campaign historical cut is closed and supports the qualified `H1–H4` findings above. `guarded` preserves the strongest observed safety-utility balance in this controlled setting, while runtime detection and operational overhead vary by backend. The [identity audit](benchmark_identity_audit.md) records why these campaigns share a protocol but should not be described as byte-identical to the original freeze, and why they cannot be attributed to the later `vogtcon` integration.
