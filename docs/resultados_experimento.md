# Pruebas, complicaciones, adecuaciones, hallazgos y resultados

Esta sección ya no describe el piloto ni la calibración. Desde el `2026-06-14`, el benchmark vigente quedó congelado como `benchmark-v1.0`, y los perfiles de modelo pasaron a tratarse como `execution conditions` de campañas post-freeze. Al `2026-06-25`, el corte canónico vigente se compone de diecinueve campañas cerradas y del artefacto inferencial [results/enforcement/statistics/final-nineteen-campaigns.json](/Users/carlos.urteaga/git/agent-contracts-benchmark/results/enforcement/statistics/final-nineteen-campaigns.json:1), en esquema `bootstrap-metrics-v2`.

## Estado metodológico

- `benchmark-v1.0` quedó congelado el `2026-06-14`.
- La identidad del benchmark está anclada en [benchmark/enforcement/benchmark_manifest.json](/Users/carlos.urteaga/git/agent-contracts-benchmark/benchmark/enforcement/benchmark_manifest.json:1).
- Los perfiles de modelo no redefinen el benchmark; sólo documentan la condición experimental de cada campaña.
- La identidad contractual canónica se compara por `contracts_semantics_hash`; la expansión de `approved_agent_configurations` se registra aparte como compatibilidad operacional y no reabre `benchmark-v1.0` por sí sola.
- Resultados débiles pero metodológicamente válidos no reabren el benchmark.
- Los artefactos exploratorios quedan fuera de la evidencia canónica:
  - `results/enforcement/smoke-gemma4-31b-cloud-rerun/`
  - `results/enforcement/smoke-gemma4-31b-cloud-rerun2/`
  - `results/enforcement/smoke-nemotron-3-super-cloud/`

## Campañas cerradas incluidas en el corte canónico

Las campañas utilizables para análisis final son:

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

El artefacto estadístico canónico:

- usa `bootstrap` al `95%`
- reporta métricas por modo
- conserva campañas separadas por modelo
- incluye métricas de recuperación y overhead
- excluye smoke-only artifacts y reruns exploratorios

## H1 — El enforcement bloqueante reduce side effects inseguros frente a `no_contract` y `advisory`

La señal central de prevención se mantiene en todo el corte cuando existen oportunidades reales de enforcement.

En `campaign-base-r5`:

- `no_contract unsafe_side_effect_rate = 1.0`
- `advisory unsafe_side_effect_rate = 1.0`
- `guarded unsafe_side_effect_rate = 0.0`
- `strict unsafe_side_effect_rate = 0.0`
- `guarded governance_effectiveness = 1.0`
- `strict governance_effectiveness = 1.0`

Las diferencias pareadas contra `no_contract` y `advisory` son completas:

- `guarded vs no_contract` en `unsafe_side_effect_rate = -1.0`, `ci_95 = [-1.0, -1.0]`
- `guarded vs advisory` en `unsafe_side_effect_rate = -1.0`, `ci_95 = [-1.0, -1.0]`
- `strict vs advisory` en `unsafe_side_effect_rate = -1.0`, `ci_95 = [-1.0, -1.0]`

El mismo patrón aparece en `campaign-deepseek-v4-pro-r5`, donde:

- `no_contract` y `advisory` permanecen en `unsafe_side_effect_rate = 1.0`
- `guarded` y `strict` permanecen en `unsafe_side_effect_rate = 0.0`
- ambas variantes bloqueantes conservan `governance_effectiveness = 1.0`

Hay campañas donde `no_contract` no genera oportunidades suficientes para definir la tasa, como `campaign-gpt-oss-120b-r5`. Eso no contradice `H1`; sólo limita el contraste en ese backend. Cuando la oportunidad aparece, el patrón sigue siendo que `guarded` y `strict` previenen el efecto inseguro, mientras `advisory` no lo bloquea.

## H2 — La calidad de detección runtime depende del backend y se reporta de forma descriptiva

`H2` se reporta aquí como comparación descriptiva con bootstrap. No se afirma equivalencia estadística formal entre `advisory`, `guarded` y `strict`.

En el modelo base:

- `campaign-base-r5 advisory f1 = 0.714286`
- `campaign-base-r5 guarded f1 = 0.789474`
- `campaign-base-r5 strict f1 = 0.714286`
- `campaign-base-r5 guarded vs strict f1 = 0.075188`, `ci_95 = [0.008336, 0.140951]`

En backends adicionales la señal ya no es estable:

- `campaign-deepseek-v4-pro-r5`: `advisory f1 = 0.125001`, `guarded f1 = 0.333333`, `strict f1 = 0.181818`
- `campaign-gpt-oss-120b-r5`: `advisory f1 = 0.4`, `guarded f1 = 0.222222`, `strict f1 = 0.121213`
- `campaign-gemma4-r3`: `advisory f1 = 0.363636`, `guarded f1 = 0.363636`, `strict f1 = 0.0`
- `campaign-kimi-k26-r3`: `advisory f1 = 0.285715`, `guarded f1 = 0.285715`, `strict f1 = 0.285715`
- `campaign-kimi-k26-r5`: `advisory f1 = 0.235294`, `guarded f1 = 0.285715`, `strict f1 = 0.285715`
- `campaign-kimi-k27-code-r3`: `advisory f1 = 0.285715`, `guarded f1 = 0.285715`, `strict f1 = 0.285715`
- `campaign-kimi-k27-code-r5`: `advisory f1 = 0.285715`, `guarded f1 = 0.285715`, `strict f1 = 0.285715`
- `campaign-nemotron-3-ultra-r3`: `advisory f1 = 0.434783`, `guarded f1 = 0.5`, `strict f1 = 0.2`
- `campaign-claude-opus-48-r3`: `advisory f1 = 0.0`, `guarded f1 = 0.0`, `strict f1 = 0.0`
- `campaign-qwen35-397b-r3`: `advisory f1 = 0.105264`, `guarded f1 = 0.285715`, `strict f1 = 0.0`

`campaign-claude-opus-48-r3` merece una lectura separada. No parece un fallo del evaluator ni del benchmark, sino un patrón de autocontención del backend: Claude completa los nominales con utilidad razonable, pero casi no genera oportunidades runtime observables para `advisory` o `guarded`. En la campaña cerrada:

- `advisory recall = 0.0`, `advisory f1 = 0.0`
- `guarded recall = 0.0`, `guarded f1 = 0.0`
- `guarded unsafe_action_opportunity_rate = 0.0`
- `guarded blocked_unsafe_actions = 0`

El `f1_diagnosis.json` de Claude clasifica los escenarios runtime relevantes (`S-011`, `S-012`, `S-013`, `S-014`, `S-020`) principalmente como `B_conservative_or_divergent_agent`, no como contradicción metodológica. La interpretación correcta es que Claude evita entrar al estado donde el Governor tendría que intervenir. Eso lo hace más conservador en comportamiento propio, pero menos útil como backend para demostrar detección runtime observable del Governor.

Tabla comparativa corta para `guarded`:

| Backend | `guarded successful_safe_completion_rate` | `guarded unsafe_action_opportunity_rate` | `guarded blocked_unsafe_actions` | `guarded recall` | `guarded f1` | Lectura |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `claude-opus-4-8 r3` | `0.714286` | `0.0` | `0` | `0.0` | `0.0` | Conservador; casi no activa enforcement runtime observable |
| `openai-direct r3` | `0.761905` | `0.031746` | `2` | `0.111111` | `0.2` | Activa algo de señal runtime, pero todavía débil |
| `openai-xhigh r3` | `0.761905` | `0.015873` | `2` | `0.055556` | `0.100001` | Similar a OpenAI directo, con menor activación runtime |
| `gpt-oss-120b r3` | `0.746032` | `0.031746` | `3` | `0.222222` | `0.347826` | Mejor evidencia de intervención runtime de `guarded` |
| `qwen35-397b r3` | `0.761905` | `0.047619` | `3` | `0.166667` | `0.285715` | Más oportunidades runtime y detección moderada |

La lectura metodológica correcta es:

1. el benchmark congelado sigue generando condiciones observables de detección runtime;
2. `advisory`, `guarded` y `strict` no tienen una relación fija de calidad de detección entre modelos;
3. la variación observada pertenece al backend y no al benchmark congelado;
4. `claude-opus-4-8 r3` representa el extremo de autocontención: mantiene utilidad razonable pero aporta muy poca activación runtime para el Governor.

## H3 — `guarded` preserva más utilidad que `strict` porque permite recuperación

Éste sigue siendo el hallazgo más robusto del paquete canónico.

En `campaign-base-r5`:

- `guarded successful_safe_completion_rate = 0.904762`
- `strict successful_safe_completion_rate = 0.342857`
- diferencia pareada `guarded vs strict = 0.561905`
- `ci_95 = [0.466666, 0.657143]`
- `guarded recovery_rate_after_block = 0.875`
- `guarded mean_replans_per_run = 1.190476`

En campañas no base el patrón persiste, aunque con distinta magnitud:

- `campaign-deepseek-v4-pro-r5`: `guarded = 0.828571`, `strict = 0.571429`
- `campaign-gpt-oss-120b-r5`: `guarded = 0.752381`, `strict = 0.495238`
- `campaign-kimi-k26-r3`: `guarded = 0.730159`, `strict = 0.47619`
- `campaign-kimi-k26-r5`: `guarded = 0.733333`, `strict = 0.47619`
- `campaign-kimi-k27-code-r3`: `guarded = 0.777778`, `strict = 0.52381`
- `campaign-kimi-k27-code-r5`: `guarded = 0.8`, `strict = 0.514286`
- `campaign-nemotron-3-ultra-r3`: `guarded = 0.809524`, `strict = 0.539683`
- `campaign-claude-opus-48-r3`: `guarded = 0.714286`, `strict = 0.47619`
- `campaign-qwen35-397b-r3`: `guarded = 0.761905`, `strict = 0.52381`
- `campaign-gemma4-r3`: `guarded = 0.730159`, `strict = 0.0`

La diferencia no se explica por pérdida de prevención. En el mismo corte:

- `guarded governance_effectiveness = 1.0` cuando la oportunidad existe
- `strict governance_effectiveness = 1.0` cuando la oportunidad existe

Por tanto, la ventaja de `guarded` no es “menos seguridad”, sino recuperación después del bloqueo.

## H4 — El enforcement con recuperación introduce overhead operativo medible

El paquete `v2` permite cuantificar overhead con:

- `mean_latency_ms`
- `mean_token_usage`
- `mean_estimated_cost`
- `mean_iterations_per_run`

En `campaign-base-r5`, `guarded` paga un costo operativo claro frente a `strict`:

- `mean_latency_ms`: diferencia `72593.895325`, `ci_95 = [53907.363726, 91328.744077]`
- `mean_token_usage`: diferencia `1559.047619`, `ci_95 = [1164.754761, 1968.644524]`
- `guarded mean_iterations_per_run` también supera a `strict`

En campañas cloud el costo adicional sigue presente pero es menor:

- `campaign-deepseek-v4-pro-r5`:
  - `mean_latency_ms` diferencia `899.490042`, `ci_95 = [384.316678, 1455.577676]`
  - `mean_token_usage` diferencia `284.228572`, `ci_95 = [36.119762, 541.679286]`
- `campaign-gpt-oss-120b-r5`:
  - `mean_latency_ms` diferencia `434.513986`, `ci_95 = [-296.854398, 1168.410738]`
  - `mean_token_usage` diferencia `105.161905`, `ci_95 = [-155.472856, 363.383809]`
- `campaign-kimi-k26-r3`:
  - `mean_latency_ms` diferencia `1178.452386`, `ci_95 = [602.820977, 1869.662021]`
  - `guarded vs strict successful_safe_completion_rate = 0.253969`, `ci_95 = [0.142858, 0.36508]`
- `campaign-kimi-k26-r5`:
  - `mean_latency_ms` diferencia `2756.373941`, `ci_95 = [358.410601, 5413.392397]`
  - `guarded vs strict successful_safe_completion_rate = 0.257143`, `ci_95 = [0.180952, 0.342857]`
- `campaign-kimi-k27-code-r3`:
  - `mean_latency_ms` diferencia `1007.436641`, `ci_95 = [-653.420061, 3001.983396]`
  - `guarded vs strict successful_safe_completion_rate = 0.253968`, `ci_95 = [0.142857, 0.36508]`
- `campaign-kimi-k27-code-r5`:
  - `mean_latency_ms` diferencia `13.840039`, `ci_95 = [-1993.399371, 1542.934631]`
  - `guarded vs strict successful_safe_completion_rate = 0.285714`, `ci_95 = [0.190476, 0.380953]`
- `campaign-nemotron-3-ultra-r3`:
  - `mean_latency_ms` diferencia `22561.97592`, `ci_95 = [5565.841996, 40703.043433]`
  - `guarded vs strict successful_safe_completion_rate = 0.269841`, `ci_95 = [0.15873, 0.396826]`

La dimensión monetaria no es informativa en este corte porque los adapters actuales normalizan costo faltante a `0.0`; por eso `mean_estimated_cost` no distingue campañas en el artefacto canónico actual. La conclusión válida de `H4` en `benchmark-v1.0` es operativa, no financiera: la recuperación tiene costo en latencia, tokens e iteraciones.

## Lectura consolidada del corte canónico

Con las diecinueve campañas cerradas del corte canónico, la evidencia post-freeze permite sostener cinco puntos:

1. El benchmark congelado sigue produciendo oportunidades reales de enforcement.
2. `guarded` y `strict` previenen side effects inseguros cuando la oportunidad bloqueante aparece.
3. `guarded` conserva mucha más finalización segura que `strict`.
4. La calidad de detección runtime varía materialmente con el backend.
5. El mecanismo de recuperación de `guarded` introduce overhead operativo medible.

## Conclusión de resultados

El paquete comparativo por hipótesis `H1–H4` ya quedó cerrado para las diecinueve campañas incluidas en `final-nineteen-campaigns.json`. Los reruns exploratorios de `gemma4:31b-cloud` y el `smoke-4` de `nemotron-3-super:cloud` quedan fuera del corte canónico y sólo sirven para priorización experimental posterior.
