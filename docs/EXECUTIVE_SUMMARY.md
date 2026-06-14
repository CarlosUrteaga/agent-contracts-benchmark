# Executive Summary

## Problem

This benchmark evaluates whether **Agent Contracts** and an **Agent Governor** can govern the runtime behavior of a tool-using LLM agent. The central problem is not whether a rule engine can classify prewritten traces, but whether a non-deterministic agent can be constrained during execution so that unsafe actions are prevented while useful task completion is preserved.

## Experimental Scenario

The benchmark uses one LLM-based agent with five deterministic local mock tools:

- `search_policy`
- `create_ticket`
- `approve_request`
- `store_memory`
- `send_notification`

The agent decides dynamically:

- which tool to call
- in what order
- with what arguments
- whether to replan after a denial
- when to stop
- what final response to return

The environment, tool behavior, contracts, scenario labels, and evaluator are controlled and reproducible. The current real backend is:

- `litellm:ollama_chat/qwen2.5:7b`

The independent variable is the enforcement mode:

- `no_contract`
- `advisory`
- `guarded`
- `strict`

The evaluated corpus contains:

- `21` scenarios
- `4` modes
- `1` replication
- total: `84` runs

Scenarios are divided into:

- `10` nominal scenarios
- `11` adversarial scenarios

They are evaluated by acceptable and forbidden outcomes, not by a single fixed action sequence.

## Approach

The benchmark places the Governor between the LLM’s proposed tool action and the actual side effect.

Validation occurs in three phases:

- `pre_execution`
- `runtime`
- `post_execution`

Mode semantics:

- `no_contract`
  No online enforcement. Actions execute and are logged.
- `advisory`
  Violations are detected and recorded, but actions still execute.
- `guarded`
  Unsafe actions are blocked and the agent may replan.
- `strict`
  Blocking violations abort execution; protected side effects are not committed on unsuccessful runs.

## Metrics Used

Primary metrics:

- `unsafe_side_effect_rate`
- `governance_effectiveness`
- `successful_safe_completion_rate`

Secondary metrics:

- `precision`
- `recall`
- `f1`
- `unsafe_action_opportunity_rate`
- `blocked_unsafe_actions`
- `recovery_rate_after_block`
- `mean_replans_per_run`
- `response_schema_compliance_rate`
- `run_ledger_completeness`
- latency
- token usage

Metric interpretation:

- `unsafe_side_effect_rate`
  fraction of runs with a violation opportunity that still committed an unsafe side effect
- `governance_effectiveness`
  fraction of runs with a violation opportunity that ended without an unsafe committed side effect
- `successful_safe_completion_rate`
  fraction of all runs that both completed acceptably and avoided forbidden outcomes

## 84-Run Pilot Results

Source:

- [results/enforcement/summary.json](/Users/carlos.urteaga/git-clone/Architectural-Contracts/results/enforcement/summary.json:1)

### Headline results

- `unsafe_actions_executed_by_mode`
  - `no_contract = 5`
  - `advisory = 5`
  - `guarded = 0`
  - `strict = 0`

- `governance_effectiveness`
  - `no_contract = 0.0`
  - `advisory = 0.0`
  - `guarded = 1.0`
  - `strict = 1.0`

- `unsafe_side_effect_rate`
  - `no_contract = 1.0`
  - `advisory = 1.0`
  - `guarded = 0.0`
  - `strict = 0.0`

- `successful_safe_completion_rate`
  - `no_contract = 0.619048`
  - `advisory = 0.571429`
  - `guarded = 0.904762`
  - `strict = 0.333333`

### Detection results

- `precision / recall / f1`
  - `advisory = 0.625 / 0.833333 / 0.714286`
  - `guarded = 0.666667 / 1.0 / 0.8`
  - `strict = 0.625 / 0.833333 / 0.714286`

### Opportunity and adaptation

- `unsafe_action_opportunity_rate`
  - `no_contract = 0.238095`
  - `advisory = 0.238095`
  - `guarded = 0.238095`
  - `strict = 0.238095`

- `recovery_rate_after_block`
  - `guarded = 0.875`
  - `strict = 0.875`

### Runtime cost

- `mean_latency_ms`
  - `no_contract = 150082.128887`
  - `advisory = 146950.853082`
  - `guarded = 152272.317173`
  - `strict = 78346.903744`

- `mean_iterations_per_run`
  - `no_contract = 5.333333`
  - `advisory = 5.142857`
  - `guarded = 5.285714`
  - `strict = 3.333333`

## Main Insights

### 1. Contracts prevented unsafe side effects in guarded and strict

The clearest result is that unsafe side effects occurred under:

- `no_contract`
- `advisory`

but not under:

- `guarded`
- `strict`

This is the strongest evidence that the enforcement layer is functionally working.

### 2. Guarded showed the best safety-completion tradeoff

`guarded` and `strict` both achieved:

- `governance_effectiveness = 1.0`
- `unsafe_side_effect_rate = 0.0`

But `guarded` preserved completion much better:

- `guarded successful_safe_completion_rate = 0.904762`
- `strict successful_safe_completion_rate = 0.333333`

This supports the thesis hypothesis that guarded enforcement may outperform strict enforcement on practical safety-completion tradeoff, because guarded allows recovery after a blocked action while strict often aborts.

### 3. Advisory improves observability but not prevention

`advisory` produced nonzero detection metrics but still allowed unsafe side effects:

- `precision = 0.625`
- `recall = 0.833333`
- `unsafe_side_effect_rate = 1.0`

This is directionally consistent with the intended role of advisory mode: observe and record, not prevent.

### 4. The benchmark produces real enforcement opportunities

The current local model is conservative enough to remain usable, but not so conservative that it eliminates risky behavior. This matters because the benchmark depends on the model creating enough unsafe-action opportunities for the Governor to demonstrate prevention.

## Limitations

- The benchmark is controlled and partially synthetic.
- Tools are deterministic local mocks, not production systems.
- The benchmark is single-agent and single-backend in its current thesis form.
- The current backend is CPU-only local inference, so latency is high and absolute runtime numbers should not be overgeneralized.
- Detection quality is still moderate, which means the benchmark is stronger on prevention evidence than on runtime rule-detection quality.
- The evaluator was corrected after the first pilot summary; the current `summary.json` is the corrected version and should be treated as authoritative.

## Hypothesis Status

Using the current `summary.json` as the authoritative source, the experimental hypotheses can be interpreted as follows:

- `H1`
  Supported. `guarded` and `strict` reduced unsafe committed side effects relative to `no_contract` and `advisory`. The observed unsafe executed actions were `5` in `no_contract`, `5` in `advisory`, and `0` in both `guarded` and `strict`.
- `H2`
  Partially supported. Detection quality is broadly comparable across enforcing modes, but not perfectly equivalent. `advisory` and `strict` are identical at `precision = 0.625`, `recall = 0.833333`, `f1 = 0.714286`, while `guarded` improves to `precision = 0.666667`, `recall = 1.0`, `f1 = 0.8`. Therefore, the evidence supports detection consistency in direction, but not strict statistical equivalence from these single-replication results.
- `H3`
  Supported. `guarded` achieved the strongest safety-completion tradeoff. Both `guarded` and `strict` obtained `governance_effectiveness = 1.0`, but `guarded` preserved `successful_safe_completion_rate = 0.904762` against `0.333333` for `strict`.
- `H4`
  Supported. Enforcement introduces measurable overhead in iterations, latency, and token use, although not uniformly in the same direction. For example, `mean_token_usage` rises from `3497.380952` in `advisory` to `3649.285714` in `guarded`, and `mean_replans_per_run` rises from `0` in `strict` to `1.333333` in `guarded`.

## Iteration Result

An important methodological result is that the benchmark improved after evaluator, oracle, scenario, and guarded-recovery adjustments. Relative to the earlier pilot, runtime F1 increased:

- `advisory: 0.5 -> 0.714286`
- `guarded: 0.4 -> 0.8`

This matters because the complications encountered during development did not merely produce fixes to infrastructure; they produced a better-calibrated experiment with stronger detection quality and more credible enforcement results.

## Areas of Opportunity

### 1. Improve stopping behavior

Some adversarial runs show inefficient repeated safe actions after recovery, such as repeated ticket creation after evidence is already present. This does not invalidate enforcement, but it degrades agent quality and can distort latency and completion behavior.

### 2. Improve detection metrics

`precision`, `recall`, and `f1` are currently modest for the blocking modes. This suggests either:

- better scenario/oracle alignment
- stronger runtime rule labeling
- or improved prompting/agent behavior to make violations more semantically explicit

### 3. Add stronger backend comparisons later

The current thesis-ready setup works with local Ollama and LiteLLM. A future comparison phase could evaluate:

- stronger local models
- cloud models through LiteLLM
- backend-dependent changes in safety, completion, and cost

### 4. Expand statistical stability

The current corpus uses `1` replication per condition. The next stronger step is:

- `21 × 4 × 3 = 252` runs

and the thesis-grade target remains:

- `21 × 4 × 5 = 420` runs

## Bottom Line

This benchmark is already producing meaningful evidence. In the current 84-run pilot, `guarded` and `strict` prevented unsafe side effects completely, while `guarded` preserved task completion far better than `strict`. That makes the current implementation scientifically useful for the thesis, even though there is still room to improve detection quality, stopping behavior, and external validity.
