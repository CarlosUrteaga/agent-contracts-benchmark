# Campaign admission review

The historical inventory contains **26 closed campaigns and 7,728 recorded runs**, closed by 2026-09-12. Closure and complete files establish operational completion; they do not establish that every campaign measures the intended model condition. This post hoc review, recorded at **2026-11-18T01:59:51Z** (November 17 in Mexico City), restricts current comparisons to **23 campaigns and 6,972 runs**.

The archived [26-campaign statistics](../results/enforcement/statistics/final-twenty-six-campaigns.json) remain unchanged. The current comparison artifact is [admission-reviewed-twenty-three-campaigns.json](../results/enforcement/statistics/admission-reviewed-twenty-three-campaigns.json). The dashboard retains all 26 campaigns, marks the three incidents, and excludes their values from comparisons.

## Inclusion rule and evidence

For every recorded run, compare the rules observed with `phase = pre_execution` against that scenario's `expected_pre_execution_violations`. Exclude the **entire campaign** if any observed pre-execution rule is not expected. This preserves complete four-mode comparisons rather than selectively rescuing modes or individual runs after seeing their scores. Deliberate identity-tampering scenarios such as S-018 and S-019 retain their expected violations and are not exclusion triggers by themselves.

The review inspects every `summary.json`, checks uniqueness of mode/replication/scenario keys, profile and scenario-type consistency, and complete coverage of every scenario and mode at the declared replication count. It records evidence hashes, per-campaign decisions, mode-specific counts, and source-statistics lineage in the derived JSON.

| Campaign excluded from comparisons | Recorded runs | Runs with unexpected pre-execution violations | Nominal runs aborted before execution |
| --- | ---: | ---: | ---: |
| `campaign-gemma4-r3` | 252 | 180 | 30 |
| `campaign-openai-gpt56-terra-medium-r3` | 252 | 167 | 26 |
| `campaign-openai-gpt6-astra-max-r3` | 252 | 180 | 30 |

Unexpected violations appear in advisory/guarded/strict respectively in 60/60/60 Gemma4 runs, 55/56/56 Terra runs, and 60/60/60 Astra runs. No-contract bypasses online admission checks. In strict mode, an unexpected admission failure can abort before the model is called. These outcomes must not be treated as measurements of model task-solving ability or as evidence that strict inherently sacrifices that much completion. The counts identify the admission contamination; they do not prove the exact historical configuration cause for every affected run.

## Statistical treatment

This is a post hoc quality screen, not a preregistered exclusion policy. Selection uses admission evidence rather than a score threshold. It does not certify all remaining aspects of experimental validity; the [identity audit](benchmark_identity_audit.md), small replication counts, backend conditions, and controlled-tool scope still limit interpretation.

The source artifact reports campaigns separately, not as one pooled sample. The derived artifact therefore copies each retained campaign report **exactly**, including all mode estimates, paired contrasts, bootstrap intervals, seed, sample count, and original bootstrap generation timestamp. No runs were rerun, no retained campaign was partially filtered, and no bootstrap was recomputed. Aggregate descriptive counts and ranges below were recalculated over the 23 retained reports. Their confidence intervals remain within-campaign intervals, without a new across-model or selection-adjusted inference.

| Finding | Admission-screened subset |
| --- | --- |
| H1: campaigns with defined unsafe-effect rates | 17 no-contract; 18 advisory; 19 guarded; 15 strict |
| H1: defined unsafe-effect estimates | 1.0 in no-contract/advisory; 0.0 in guarded/strict |
| H3: guarded minus strict safe-completion contrast | Positive in 23/23 campaigns; point-estimate range **0.238095–0.561905** |
| H3: paired 95% bootstrap interval | Lower bound above zero in each of the 23 campaigns; no pooled or multiplicity-adjusted claim |
| H4: guarded minus strict latency and token estimates | Positive in 23/23 campaigns; some intervals include zero |
| Monetary cost coverage | 4 campaigns with nonzero estimates; 19 report zero, which can also encode unavailable adapter cost data |

The former H3 maximum of 0.730159 included admission-contaminated Gemma4 and Astra campaigns. It is not the maximum for the reviewed comparison subset. H2 examples from the three excluded campaigns are no longer used to characterize model-dependent runtime detection. The base-r5 anchor estimates are unchanged.

## Reproduce and verify

```bash
# Verify lineage, every admission decision, evidence hashes, and derived reports.
uv run python -m tools.enforcement.admission_review --check

# Recreate the dated review from the original evidence, then regenerate the site.
uv run python -m tools.enforcement.admission_review \
  --reviewed-at 2026-11-18T01:59:51Z
uv run python scripts/build_site_data.py
```

The site generator verifies the recorded review against the run evidence before building comparison tables. A changed source, decision, retained report, or evidence digest fails verification instead of silently mixing cuts.

Source artifact SHA-256: `98fb304690c81b3f7c832244381657b801b924ffab02ce4e1ce09a7497b5376a`. Scenario evidence digest: `bfd2fa0c92cb599f9d79680ddabc2e74f6f5c9012a65a5b94625da6237f61268`. The digest algorithm hashes a sorted JSON list of repository-relative filenames and their individual SHA-256 hashes; the implementation is in [admission_review.py](../tools/enforcement/admission_review.py).

For future campaigns, use the model-admission preflight before the full matrix. Correcting current compatibility metadata does not repair historical execution conditions. Any replacement real-model campaign needs a new campaign identity and fresh evidence.
