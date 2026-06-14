# Contract Audit Matrix

This matrix records the declarative integrity audit of the frozen contract YAML artifacts for `benchmark-v1.0`.

| contract | validation_phases | runtime_rules | postconditions | declared_tools | agent_feedback | mode_semantics | decision | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `no_contract` | `ok` | `ok` | `ok` | `ok` | `document_as_limitation` | `ok` | `ok` | Uses `validation_phases = not_enforced`, `runtime_rules = []`, `postconditions = []`, and `declared_tools = ["*"]`. Audit note: absence of contractual postconditions does not suppress experimental artifacts such as `summary.json`, `trace.jsonl`, or `run_ledger.json`. `agent_feedback` keys are retained as inert metadata in `benchmark-v1.0`. |
| `advisory` | `ok` | `ok` | `ok` | `ok` | `document_as_limitation` | `ok` | `ok` | Contract declares the frozen runtime rule and postcondition sets without blocking semantics drift. `agent_feedback` keys are present but are not consumed by runtime behavior in `benchmark-v1.0`; advisory semantics are implemented by mode, not by these keys. |
| `guarded` | `ok` | `ok` | `ok` | `ok` | `document_as_limitation` | `ok` | `ok` | Contract declares the frozen runtime rule and postcondition sets. Guarded recovery semantics are implemented in runtime via mode-specific block and replan behavior. `agent_feedback` remains declarative metadata in the current frozen benchmark. |
| `strict` | `ok` | `ok` | `ok` | `ok` | `document_as_limitation` | `ok` | `ok` | Contract declares the frozen runtime rule and postcondition sets. Strict runtime and pre-execution abort semantics are preserved. `agent_feedback` keys are retained as inert metadata and do not currently enable recovery behavior. |

## Contract audit conclusions

- No contract YAML changes were required during this audit.
- No new rule families were introduced.
- All declared runtime rules and postconditions remain aligned with the frozen runtime implementation.
- `declared_tools` remains aligned with the runtime tool registry and scenario-exposed tools.
- `agent_feedback` is documented as inert declarative metadata in `benchmark-v1.0`, not as active runtime configuration.
