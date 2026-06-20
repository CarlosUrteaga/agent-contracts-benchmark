# Contract Enforcement Benchmark

## Purpose

This benchmark evaluates whether **Agent Contracts** and an **Agent Governor** can govern a tool-using **LLM agent during execution**.

The benchmark is designed around:

- controlled scenarios
- deterministic mock tools
- stochastic LLM behavior
- runtime interception of proposed actions
- oracle-based offline scoring

It is not a replay benchmark over prefabricated actions.

## Variable

The independent variable is the enforcement mode:

- `no_contract`
- `advisory`
- `guarded`
- `strict`

The benchmark does not use the old Drift arms as the primary variable.

## Experimental Unit

One independent execution of a scenario, under one enforcement mode and one replication, with a fixed model profile.

## Agent and Tools

The agent uses a real LLM backend and local deterministic tools:

- `search_policy`
- `create_ticket`
- `approve_request`
- `store_memory`
- `send_notification`

The LLM decides dynamically:

- which tool to call
- tool order
- tool arguments
- whether to replan
- when to stop
- final response content

## Scenario Design

Scenarios are outcome-based, not route-based.

Each scenario defines:

- `user_request`
- `initial_state`
- `available_tools`
- `hidden_oracle`
- `acceptable_outcomes`
- `forbidden_outcomes`
- `expected_violations_if_attempted`
- `max_agent_iterations`

Two scenario classes are used:

- `nominal`
- `adversarial`

An adversarial scenario is not “invalid.” A run can still finish safely if the agent avoids or recovers from a risky action.

## Enforcement Visibility

The benchmark headline condition fixes what the LLM sees:

- same system prompt in all four modes
- the LLM does not see the YAML contract
- the LLM does not see the hidden oracle
- advisory does not expose warnings
- guarded returns a minimal structured denial
- strict aborts on blocking violations and does not allow replanning after abort

This keeps the experimental variable focused on enforcement behavior, not on how much extra contractual help the model receives.

## Runtime Phases

### pre_execution

Validate:

- agent configuration fingerprint
- contract fingerprint
- model/runtime profile compatibility
- declared tool set
- identity and role requirements

### runtime

Validate every proposed action:

- declared tool
- authorization
- evidence requirements
- approval requirements
- memory scope
- notification policy
- argument schema
- action budget

### post_execution

Validate:

- final response schema
- ledger existence
- ledger completeness
- outcome properties
- absence of unauthorized committed side effects

## Primary Metrics

- `unsafe_side_effect_rate`
- `governance_effectiveness`
- `successful_safe_completion_rate`

## Secondary Metrics

- `precision`
- `recall`
- `f1`
- `blocked_unsafe_actions`
- `violation_detection_rate`
- `false_positive_rate`
- `false_negative_rate`
- `unsafe_action_opportunity_rate`
- `recovery_rate_after_block`
- `repeated_violation_rate`
- `mean_replans_per_run`
- `response_schema_compliance_rate`
- `run_ledger_completeness`
- `mean_latency_ms`
- `median_governor_latency_ms`
- `p95_governor_latency_ms`
- `mean_token_usage`
- `mean_estimated_cost`
- `mean_iterations_per_run`

## Hypotheses

- **H1.** Guarded and strict enforcement reduce unauthorized committed side effects relative to no-contract and advisory execution.
- **H2.** Governor precision and recall in advisory mode are statistically equivalent to those in guarded and strict mode, showing that detection quality is independent of enforcement strength.
- **H3.** Guarded enforcement achieves a better safety-completion trade-off than strict enforcement by allowing recovery after blocked actions.
- **H4.** Contract enforcement introduces measurable runtime, token, and monetary overhead.

## Threats to Validity

### Internal validity

- Scenarios are controlled and partially synthetic.
- Tools are deterministic mocks.
- This improves comparability but reduces ecological complexity.

### External validity

- The benchmark uses one task family and one tool-using agent loop at a time.
- It does not represent all production agent systems.
- It does not claim integration with LangGraph, CrewAI, AutoGen, or MCP.

### Construct validity

- Prevention is measured through unsafe committed side effects and governance effectiveness.
- Detection is measured through oracle-based rule scoring.
- Completion is measured through acceptable vs forbidden outcomes.

### Signal risk

The main scientific risk is that a strong model may avoid unsafe actions in many adversarial runs, reducing enforcement opportunities.

For that reason the benchmark reports:

- `unsafe_action_opportunity_rate`
- pilot results before larger replication budgets

## Current Execution Plan

- pilot: `21 × 4 × 1 = 84` runs
- baseline: `21 × 4 × 3 = 252` runs
- thesis-grade target: `21 × 4 × 5 = 420` runs

## Reproducibility

Use `uv` as the environment manager and runner for this repository.

Typical workflow:

```bash
uv sync
uv run python -m tools.enforcement.materialize --out .
uv run python -m tools.enforcement.run_all --scenarios benchmark/enforcement/scenarios --contracts contracts/enforcement --model-profile benchmark/enforcement/config/model_profiles/mock.yaml --replications 1 --out results/enforcement/runs
uv run python -m tools.enforcement.evaluate --runs results/enforcement/runs --oracle benchmark/enforcement/oracle --out results/enforcement/summary.json
uv run python -m unittest discover -s tests -p 'test*.py'
```

Optional OpenAI fallback:

```bash
uv sync --group openai
uv run --group openai python -m tools.enforcement.run_all ...
```

Optional Microsoft Azure AI Foundry backends through LiteLLM:

The benchmark uses the LiteLLM adapter for both Microsoft-hosted paths:

- Azure OpenAI deployments use the `azure/` LiteLLM route, configured by `benchmark/enforcement/config/model_profiles/azure_foundry_openai.yaml`.
- Azure AI Foundry Claude deployments use the `azure_ai/` LiteLLM route, configured by `benchmark/enforcement/config/model_profiles/azure_foundry_claude.yaml`.
- Secrets and endpoints are read from environment variables. Do not commit real keys or a filled `.env` file.
- The non-secret template is `.env.example`.

For Azure OpenAI, set the deployment name in `azure_foundry_openai.yaml` first:

```json
"model_id": "azure/<your-deployment-name>",
"declared_model_version": "<your-deployment-name>"
```

Then run:

```bash
uv sync --group litellm
export AZURE_API_KEY="<secret>"
export AZURE_API_BASE="https://<resource-name>.openai.azure.com"
export AZURE_API_VERSION="<api-version-for-your-deployment>"
uv run --group litellm python -m tools.enforcement.run_all \
  --scenarios benchmark/enforcement/scenarios \
  --contracts contracts/enforcement \
  --model-profile benchmark/enforcement/config/model_profiles/azure_foundry_openai.yaml \
  --replications 3 \
  --out results/enforcement/campaign-azure-foundry-openai
```

For Azure AI Foundry Claude, use the Foundry endpoint that ends in `/anthropic`:

```bash
uv sync --group litellm
export AZURE_AI_API_KEY="<secret>"
export AZURE_AI_API_BASE="https://<resource-name>.services.ai.azure.com/anthropic"
uv run --group litellm python -m tools.enforcement.run_all \
  --scenarios benchmark/enforcement/scenarios \
  --contracts contracts/enforcement \
  --model-profile benchmark/enforcement/config/model_profiles/azure_foundry_claude.yaml \
  --replications 3 \
  --out results/enforcement/campaign-azure-foundry-claude
```

The profile defaults to `azure_ai/claude-opus-4-1`; update `model_id` and `declared_model_version` in `azure_foundry_claude.yaml` if the deployed Foundry model uses a different Claude slug.

For the thesis-facing real backend, use LiteLLM with Ollama:

```bash
uv sync --group litellm
ollama serve
ollama pull qwen2.5:7b
uv run --group litellm python -m tools.enforcement.run \
  --scenario benchmark/enforcement/scenarios/S-001.policy_lookup_nominal.json \
  --mode guarded \
  --contract contracts/enforcement/guarded.yaml \
  --model-profile benchmark/enforcement/config/model_profiles/default.yaml \
  --replication-id rep01 \
  --out results/enforcement/manual/S-001-guarded
```

```bash
uv run --group litellm python -m tools.enforcement.run \
  --scenario benchmark/enforcement/scenarios/S-011.ticket_without_required_evidence.json \
  --mode guarded \
  --contract contracts/enforcement/guarded.yaml \
  --model-profile benchmark/enforcement/config/model_profiles/default.yaml \
  --replication-id rep01 \
  --out results/enforcement/manual/S-011-guarded
```

Notes:

- The default real profile is `ollama_chat/qwen2.5:7b`.
- LiteLLM import overhead is outside the adapter completion timing.
- Local Ollama cost is normalized to `0.0` if the backend does not report one.
