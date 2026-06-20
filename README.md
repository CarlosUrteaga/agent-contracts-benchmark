# Agent Contracts Benchmark

This repository hosts an enforcement-first benchmark for evaluating **Agent Contracts + Agent Governor** over a **tool-using LLM agent**.

The benchmark does **not** treat the old Drift arms as the primary experiment. The independent variable in this repository is:

- `no_contract`
- `advisory`
- `guarded`
- `strict`

The benchmark studies a controlled setting with:

- stochastic LLM decisions
- deterministic local mock tools
- runtime contract interception before side effects
- oracle-based offline evaluation

## Research Question

Can Agent Contracts govern the runtime behavior of a tool-using LLM agent?

## Experimental System

The agent has access to five local deterministic tools:

- `search_policy`
- `create_ticket`
- `approve_request`
- `store_memory`
- `send_notification`

The environment, tool behavior, contracts, oracle labels, and evaluator are controlled and reproducible.

The agent behavior is not predetermined. The LLM decides dynamically:

- which tool to call
- in what order
- with what arguments
- whether to replan after a denial
- when to stop
- what final response to return

## Repository Map

Core benchmark artifacts:

- `benchmark/enforcement/scenarios/`
- `benchmark/enforcement/fixtures/`
- `benchmark/enforcement/fixtures/tampered/`
- `benchmark/enforcement/oracle/`
- `benchmark/enforcement/config/model_profiles/`
- `contracts/enforcement/`
- `tools/enforcement/`
- `results/enforcement/`
- `docs/contract_enforcement_benchmark.md`

The legacy Drift benchmark is not part of the main execution path of this repository.

## Benchmark Flow

1. Materialize the benchmark scaffold:

```bash
uv sync
uv run python -m tools.enforcement.materialize --out .
```

2. Dry-run the budget and run-count estimate:

```bash
uv run python -m tools.enforcement.run_all \
  --scenarios benchmark/enforcement/scenarios \
  --contracts contracts/enforcement \
  --model-profile benchmark/enforcement/config/model_profiles/default.yaml \
  --replications 3 \
  --dry-run
```

3. Run the benchmark:

```bash
uv sync --group litellm
ollama serve
ollama pull qwen2.5:7b
uv run --group litellm python -m tools.enforcement.run_all \
  --scenarios benchmark/enforcement/scenarios \
  --contracts contracts/enforcement \
  --model-profile benchmark/enforcement/config/model_profiles/default.yaml \
  --replications 3 \
  --out results/enforcement/runs
```

4. Evaluate the runs:

```bash
uv run python -m tools.enforcement.evaluate \
  --runs results/enforcement/runs \
  --oracle benchmark/enforcement/oracle \
  --out results/enforcement/summary.json
```

5. Run the test suite:

```bash
uv run python -m unittest discover -s tests -p 'test*.py'
```

## Scenarios

The initial corpus contains `21` scenarios:

- `S-001` to `S-010`: nominal scenarios
- `S-011` to `S-021`: adversarial scenarios

Scenarios define:

- user request
- initial state
- available tools
- hidden oracle
- acceptable outcomes
- forbidden outcomes
- expected violations if a risky action is attempted
- maximum iteration budget

They do **not** prescribe a fixed tool-call sequence.

## Enforcement Semantics

- `no_contract`
  no online contract checks; actions still logged for offline scoring
- `advisory`
  violations are detected and logged, but actions execute
- `guarded`
  invalid actions are blocked; the agent can replan
- `strict`
  precondition and runtime violations abort the run; postcondition failures mark the run as failed; protected side effects are buffered and committed only on success

## Main Metrics

Primary metrics:

- `unsafe_side_effect_rate`
- `governance_effectiveness`
- `successful_safe_completion_rate`

Secondary metrics:

- `precision`
- `recall`
- `f1`
- `blocked_unsafe_actions`
- `unsafe_action_opportunity_rate`
- `recovery_rate_after_block`
- `mean_replans_per_run`
- `response_schema_compliance_rate`
- `run_ledger_completeness`
- `mean_latency_ms`
- `median_governor_latency_ms`
- `p95_governor_latency_ms`
- `mean_token_usage`
- `mean_estimated_cost`

## Important Limits

- This is an LLM-based agent execution benchmark, not a production deployment.
- Tools are controlled local mocks.
- The benchmark does not validate Agent Types.
- The benchmark does not claim integration with LangGraph, CrewAI, AutoGen, or MCP.
- The benchmark does not claim that remote model weights are cryptographically verified; the recorded fingerprint is the fingerprint of the deployed agent configuration.

## Real Backend Notes

- The thesis-facing default real backend is **LiteLLM + Ollama** with `ollama_chat/qwen2.5:7b`.
- Local Ollama runs are treated as **zero-cost** by default unless the backend explicitly reports a usable cost value.
- For Microsoft Azure AI Foundry through LiteLLM, use:
  - `benchmark/enforcement/config/model_profiles/azure_foundry_openai.yaml` for Azure OpenAI deployments.
  - `benchmark/enforcement/config/model_profiles/azure_foundry_claude.yaml` for Azure AI Foundry Claude.
- Keep keys out of git. Copy `.env.example` values into your shell or local secret manager, then run with `uv run --group litellm`.
- The shipped fallback direct OpenAI SDK profile is `benchmark/enforcement/config/model_profiles/openai_chat.yaml`, but it is not the primary path.

Azure Foundry smoke test:

```bash
uv sync --group litellm
export AZURE_AI_API_KEY="<secret>"
export AZURE_AI_API_BASE="https://<resource-name>.services.ai.azure.com/anthropic"
uv run --group litellm python -m tools.enforcement.run \
  --scenario benchmark/enforcement/scenarios/S-001.policy_lookup_nominal.json \
  --mode guarded \
  --contract contracts/enforcement/guarded.yaml \
  --model-profile benchmark/enforcement/config/model_profiles/azure_foundry_claude.yaml \
  --replication-id rep01 \
  --out results/enforcement/manual/azure-foundry-claude-S-001-guarded
```

Full campaign:

```bash
uv run --group litellm python -m tools.enforcement.run_all \
  --scenarios benchmark/enforcement/scenarios \
  --contracts contracts/enforcement \
  --model-profile benchmark/enforcement/config/model_profiles/azure_foundry_claude.yaml \
  --replications 3 \
  --out results/enforcement/campaign-azure-foundry-claude
```
