# Execution Plan

## Objetivo

Este documento define el plan operativo para ejecutar el experimento doctoral sin seguir modificando el benchmark durante la fase de evaluación. Su propósito es convertir el estado actual del proyecto en una secuencia de corridas reproducibles, con puntos de control claros y artefactos verificables.

La regla central es:

> primero se congela el benchmark, después se ejecuta, y sólo al final se analiza.

Estado actual:

- el benchmark quedó formalmente congelado como `benchmark-v1.0` el `2026-06-14`
- los `model profiles` no forman parte del freeze metodológico; se tratan como execution conditions documentadas por campaña
- el bloque activo ya no es calibración, sino ejecución replicada y análisis post-freeze

## Supuestos

Este plan asume lo siguiente:

- el benchmark actual ya funciona end-to-end
- el perfil por defecto usa Ollama vía LiteLLM
- el corpus base es:
  - `21` escenarios
  - `4` modos
- el resultado actual del piloto se considera evidencia de señal, no evidencia final doctoral

## Artefactos fuente

Antes de correr cualquier lote final, deben considerarse como artefactos de referencia:

- [benchmark/enforcement/scenarios](/Users/carlos.urteaga/git-clone/Architectural-Contracts/benchmark/enforcement/scenarios:1)
- [contracts/enforcement](/Users/carlos.urteaga/git-clone/Architectural-Contracts/contracts/enforcement:1)
- [benchmark/enforcement/oracle/scenario_catalog.json](/Users/carlos.urteaga/git-clone/Architectural-Contracts/benchmark/enforcement/oracle/scenario_catalog.json:1)
- [docs/oracle_spec.md](/Users/carlos.urteaga/git-clone/Architectural-Contracts/docs/oracle_spec.md:1)
- [tools/enforcement/evaluate.py](/Users/carlos.urteaga/git-clone/Architectural-Contracts/tools/enforcement/evaluate.py:1)
- [tools/enforcement/diagnose_f1.py](/Users/carlos.urteaga/git-clone/Architectural-Contracts/tools/enforcement/diagnose_f1.py:1)
- [tools/enforcement/validate_oracle.py](/Users/carlos.urteaga/git-clone/Architectural-Contracts/tools/enforcement/validate_oracle.py:1)
- [benchmark/enforcement/config/model_profiles/default.yaml](/Users/carlos.urteaga/git-clone/Architectural-Contracts/benchmark/enforcement/config/model_profiles/default.yaml:1)

## Gate adicional de integridad del oracle

Si el oracle catalog o la oracle spec cambian en una rama de trabajo, debe correrse este gate antes de cualquier campaña:

```bash
python3 -m tools.enforcement.materialize --out .
python3 -m tools.enforcement.validate_oracle
python3 -m unittest tests.test_enforcement_benchmark.EnforcementBenchmarkTests.test_validate_oracle_accepts_current_catalog -v
```

Este gate valida que:

- el catálogo cubre los `21` escenarios
- runtime, pre-execution y post-execution permanecen separados
- `S-016` sigue siendo la única exclusión estructural de runtime F1
- la spec y el catálogo no derivan silenciosamente

Si este gate falla, no se lanza ninguna campaña nueva hasta decidir si el cambio es sólo documental o si abre un nuevo benchmark versionado.

## Fase 0. Freeze operacional

Estado:
- completada el `2026-06-14` con `benchmark-v1.0`

### Objetivo

Dejar trazado el gate metodológico que ya se cerró antes de la corrida doctoral.

### Freeze readiness criteria

El benchmark sólo puede congelarse si:

- todos los escenarios tienen schema completo
- no existen reglas runtime huérfanas
- no existen reglas declaradas en contratos que el runtime no use
- todas las exclusiones de runtime F1 están justificadas
- `evaluate.py` y `diagnose_f1.py` producen diagnósticos consistentes
- el pre-freeze audit no tiene issues en estado `needs_fix`
- el calibration log documenta todos los cambios aplicados
- la validación pre-freeze ejecuta sin errores

### Checklist histórico

- no cambiar escenarios
- no cambiar contratos
- no cambiar evaluator
- no cambiar diagnosis
- no cambiar semántica terminal
- no cambiar execution conditions mientras se estaba cerrando el freeze metodológico

### Evidencia registrada

- hash del commit congelado
- copia del `summary.json` del piloto previo
- nota de freeze con fecha

### Comandos de verificación histórica

Verificar estado actual:

```bash
git rev-parse HEAD
git status --short
```

Verificar que el benchmark materializa correctamente:

```bash
python3 -m tools.enforcement.materialize --out .
git diff -- benchmark/enforcement/scenarios contracts/enforcement
```

Todo cambio producido por `materialize` debe revisarse explícitamente antes de aceptarse en el freeze.

Verificar pruebas:

```bash
python3 -m unittest discover -s tests -p 'test*.py'
```

### Criterio de salida

El benchmark ya quedó declarado como versión congelada para evaluación. A partir de este punto no se hacen cambios metodológicos sobre `benchmark-v1.0`; sólo se ejecutan campañas post-freeze bajo execution conditions documentadas.

## Fase 1. Validación de entorno

### Objetivo

Confirmar que el entorno de ejecución real está listo antes de lanzar lotes largos.

### Checklist

- `uv` sincronizado
- grupo `litellm` instalado
- Ollama activo
- modelo disponible en local

### Comandos

```bash
uv sync --group litellm
ollama list
```

Verificar el perfil de modelo:

```bash
sed -n '1,200p' benchmark/enforcement/config/model_profiles/default.yaml
```

### Smoke test mínimo

Nominal:

```bash
uv run --group litellm python -m tools.enforcement.run \
  --scenario benchmark/enforcement/scenarios/S-001.policy_lookup_nominal.json \
  --mode guarded \
  --contract contracts/enforcement/guarded.yaml \
  --model-profile benchmark/enforcement/config/model_profiles/default.yaml \
  --replication-id rep01 \
  --out results/enforcement/smoke/S-001-guarded
```

Adversarial:

```bash
uv run --group litellm python -m tools.enforcement.run \
  --scenario benchmark/enforcement/scenarios/S-011.ticket_without_required_evidence.json \
  --mode guarded \
  --contract contracts/enforcement/guarded.yaml \
  --model-profile benchmark/enforcement/config/model_profiles/default.yaml \
  --replication-id rep01 \
  --out results/enforcement/smoke/S-011-guarded
```

### Criterio de salida

El modelo responde, el runtime produce `summary.json` y el Governor interviene correctamente en el escenario adversarial.

## Fase 1.5. Campaña overnight pre-freeze

Estado:
- completada el `2026-06-14` como evidencia final de freeze

### Objetivo

Dejar documentada la campaña de validación que cerró el freeze de `benchmark-v1.0`.

### Regla operativa histórica

- no borrar el árbol de resultados por defecto
- no reejecutar runs ya completos y válidos
- reejecutar automáticamente runs parciales o corruptos
- no marcar freeze-ready sólo por haber terminado la ejecución; también deben correr la validación y el postproceso

### Comando oficial para arrancar o reanudar

```bash
uv run --group litellm python -m tools.enforcement.run_pre_freeze_validation --resume
```

### Comando oficial para reiniciar desde cero

```bash
uv run --group litellm python -m tools.enforcement.run_pre_freeze_validation --force-rerun
```

### Validación de completitud

```bash
python3 -m tools.enforcement.validate_campaign \
  --runs results/enforcement/pre-freeze-validation \
  --expected-runs 84 \
  --strict
```

### Postproceso oficial

```bash
python3 -m tools.enforcement.finalize_pre_freeze_validation
```

### Criterio de salida

El benchmark quedó **freeze-ready** y posteriormente `frozen` sólo si:

- la campaña completa tiene `84` runs válidos
- cada run tiene `summary.json`
- cada run tiene `trace.jsonl`
- cada run tiene `run_ledger.json`
- cada run tiene `run_complete.json`
- no existen directorios parciales o corruptos contados como completos
- `f1_diagnosis.json` se genera correctamente
- `summary.json` se genera correctamente

### Regla anti-retuning

Resultados peores pero metodológicamente válidos no reabren el benchmark. Un rerun post-freeze sólo justifica reabrir `benchmark-v1.0` si aparece una inconsistencia metodológica real, no si cambian las métricas headline.

## Fase 2. Corrida base replicada del modelo actual

### Objetivo

Ejecutar el benchmark completo sobre el modelo base congelado.

Los lotes de esta fase corren sobre `benchmark-v1.0` sin modificar escenarios, contratos, oracle, evaluator o diagnosis. Los `model profiles` usados aquí son execution conditions y deben registrarse por campaña.

### Lote mínimo doctoral

- `21 × 4 × 3 = 252` corridas

### Lote objetivo

- `21 × 4 × 5 = 420` corridas

### Organización recomendada

Usar carpetas separadas por campaña:

- `results/enforcement/campaign-base-r3/`
- `results/enforcement/campaign-base-r5/`

### Execution manifest obligatorio

Toda campaña post-freeze debe tener su propio `execution_manifest.json`.

Ese artefacto registra:

- el benchmark congelado de referencia
- el model profile usado
- el número de réplicas
- el tamaño esperado de la matriz de ejecución
- la carpeta raíz de resultados

El benchmark identity sigue estando en:

- `benchmark/enforcement/benchmark_manifest.json`

El execution manifest identifica la campaña, no el benchmark.

Para campañas frontier o cloud, la comprobación canónica del benchmark debe tratar los contratos así:

- `contracts_semantics_hash`
  - debe permanecer igual al manifest congelado para que la campaña siga perteneciendo a `benchmark-v1.0`
- `contract_compatibility_hash`
  - puede cambiar cuando sólo se amplían `approved_agent_configurations` o cambia el `contract_fingerprint` derivado
  - ese drift debe documentarse, pero no reabre el benchmark si la semántica contractual permanece igual

Antes de correr una campaña, el manifest debe validarse explícitamente contra:

- `--runs-root`
- `--model-profile`
- `--replications`
- el benchmark manifest congelado

Preflight para `3` réplicas:

```bash
python3 -m tools.enforcement.validate_execution_manifest \
  --manifest results/enforcement/campaign-base-r3/execution_manifest.json \
  --benchmark-manifest benchmark/enforcement/benchmark_manifest.json \
  --model-profile benchmark/enforcement/config/model_profiles/default.yaml \
  --replications 3 \
  --runs-root results/enforcement/campaign-base-r3
```

Para `3` réplicas:

```bash
python3 -m tools.enforcement.execution_manifest \
  --benchmark-manifest benchmark/enforcement/benchmark_manifest.json \
  --model-profile benchmark/enforcement/config/model_profiles/default.yaml \
  --replications 3 \
  --runs-root results/enforcement/campaign-base-r3 \
  --out results/enforcement/campaign-base-r3/execution_manifest.json
```

Para `5` réplicas:

```bash
python3 -m tools.enforcement.execution_manifest \
  --benchmark-manifest benchmark/enforcement/benchmark_manifest.json \
  --model-profile benchmark/enforcement/config/model_profiles/default.yaml \
  --replications 5 \
  --runs-root results/enforcement/campaign-base-r5 \
  --out results/enforcement/campaign-base-r5/execution_manifest.json
```

### Regla de no-overwrite

- no borrar ni reemplazar runs completos válidos
- sólo rerunear runs faltantes, parciales o corruptos
- usar `--resume` como modo normal de ejecución de campaña

### Clasificación de fallos

| Tipo de problema | Acción |
| --- | --- |
| `uv` cache / permisos / sandbox | bloqueo operacional |
| Ollama no disponible | bloqueo operacional |
| timeout aislado | rerun con `--resume` |
| run corrupto persistente | investigar artifact |
| métrica fuera de rango | inconsistencia metodológica |
| oracle contradice escenario | reabrir audit correspondiente |
| resultados peores | no reabrir benchmark |

### Comando de lote completo

Para `3` réplicas:

```bash
uv run --group litellm python -m tools.enforcement.run_all \
  --scenarios benchmark/enforcement/scenarios \
  --contracts contracts/enforcement \
  --model-profile benchmark/enforcement/config/model_profiles/default.yaml \
  --replications 3 \
  --out results/enforcement/campaign-base-r3
```

Para `5` réplicas:

```bash
uv run --group litellm python -m tools.enforcement.run_all \
  --scenarios benchmark/enforcement/scenarios \
  --contracts contracts/enforcement \
  --model-profile benchmark/enforcement/config/model_profiles/default.yaml \
  --replications 5 \
  --out results/enforcement/campaign-base-r5
```

`campaign-base-r5` sólo debe arrancar si `campaign-base-r3` ya cerró sin inconsistencia metodológica real.

### Post-proceso

Diagnóstico:

```bash
python3 -m tools.enforcement.diagnose_f1 \
  --runs results/enforcement/campaign-base-r3 \
  --out results/enforcement/campaign-base-r3/f1_diagnosis.json
```

Evaluación:

```bash
python3 -m tools.enforcement.evaluate \
  --runs results/enforcement/campaign-base-r3 \
  --oracle benchmark/enforcement/oracle \
  --out results/enforcement/campaign-base-r3/summary.json
```

Closeout formal:

```bash
python3 -m tools.enforcement.closeout_campaign \
  --manifest results/enforcement/campaign-base-r3/execution_manifest.json
```

### Artefactos a guardar

- `execution_manifest.json`
- `summary.json`
- `f1_diagnosis.json`
- `artifact_hashes.json`
- `campaign_closeout.md`
- trazas por corrida
- ledger por corrida

### Criterio de salida

Existen distribuciones por modo y por escenario para el modelo base, no sólo resultados puntuales.

## Fase 3. Segundo modelo

### Objetivo

Reducir la dependencia de un solo backend.

Este bloque sigue corriendo sobre `benchmark-v1.0` sin modificar escenarios, contratos, oracle, evaluator o diagnosis.

### Recomendación mínima

Agregar un segundo perfil:

- modelo abierto/local comparable, por ejemplo `gemma4:26b`

### Recomendación fuerte

Agregar además un tercer perfil API pequeño:

- por ejemplo `gpt-4o-mini` vía LiteLLM

### Preparación

Crear o verificar perfiles adicionales en:

- `benchmark/enforcement/config/model_profiles/`

Ejemplos sugeridos:

- `gemma4_26b.yaml`
- `gpt4o_mini.yaml`

Nota:

- `results/enforcement/campaign-gemma4-r3/execution_manifest.json` se emite sólo después de crear `benchmark/enforcement/config/model_profiles/gemma4_26b.yaml`
- este step no usa placeholder ni sustituye ese manifest por `openai_chat.yaml`
- `openai_chat.yaml` queda sólo como fallback opcional, no como ruta principal del segundo modelo

### Gate previo obligatorio

`campaign-gemma4-r3` sólo puede arrancar después de:

- `campaign-base-r3` validada con `validate_campaign --strict`
- `campaign-base-r3` cerrada con `closeout_campaign`
- ausencia de inconsistencia metodológica real

El estado actual debe tratarse así:

- `campaign-base-r3` incompleta o sin closeout = gate no resuelto
- `Ollama` no disponible o modelo no descargado = bloqueo operacional
- contradicción oracle/evaluator, métrica fuera de rango o exclusión injustificada = inconsistencia metodológica
- resultados peores pero metodológicamente válidos = no reabren `benchmark-v1.0`

### Profile objetivo

El segundo modelo se ejecuta con:

- `benchmark/enforcement/config/model_profiles/gemma4_26b.yaml`
- `provider: "litellm"`
- `model_id: "ollama_chat/gemma4:26b"`
- `declared_model_version: "gemma4:26b"`
- mismos `temperature`, `max_tokens`, `timeout` y `retry_policy` del profile base salvo limitación técnica real

### Preflight del execution manifest

Generación:

```bash
python3 -m tools.enforcement.execution_manifest \
  --benchmark-manifest benchmark/enforcement/benchmark_manifest.json \
  --model-profile benchmark/enforcement/config/model_profiles/gemma4_26b.yaml \
  --replications 3 \
  --runs-root results/enforcement/campaign-gemma4-r3 \
  --out results/enforcement/campaign-gemma4-r3/execution_manifest.json
```

Validación:

```bash
python3 -m tools.enforcement.validate_execution_manifest \
  --manifest results/enforcement/campaign-gemma4-r3/execution_manifest.json \
  --benchmark-manifest benchmark/enforcement/benchmark_manifest.json \
  --model-profile benchmark/enforcement/config/model_profiles/gemma4_26b.yaml \
  --replications 3 \
  --runs-root results/enforcement/campaign-gemma4-r3
```

### Ejecución

Dry run:

```bash
uv run --group litellm python -m tools.enforcement.run_all \
  --scenarios benchmark/enforcement/scenarios \
  --contracts contracts/enforcement \
  --model-profile benchmark/enforcement/config/model_profiles/gemma4_26b.yaml \
  --replications 3 \
  --dry-run \
  --out results/enforcement/campaign-gemma4-r3
```

Campaña:

```bash
uv run --group litellm python -m tools.enforcement.run_all \
  --scenarios benchmark/enforcement/scenarios \
  --contracts contracts/enforcement \
  --model-profile benchmark/enforcement/config/model_profiles/gemma4_26b.yaml \
  --replications 3 \
  --resume \
  --out results/enforcement/campaign-gemma4-r3
```

Regla de ejecución:

- no borrar ni reemplazar runs completos válidos
- sólo rerunear runs faltantes, parciales o corruptos
- usar `--resume` como modo normal de ejecución

### Post-proceso

Validación estricta:

```bash
python3 -m tools.enforcement.validate_campaign \
  --runs results/enforcement/campaign-gemma4-r3 \
  --expected-runs 252 \
  --strict
```

Closeout formal:

```bash
python3 -m tools.enforcement.closeout_campaign \
  --manifest results/enforcement/campaign-gemma4-r3/execution_manifest.json
```

Artefactos de cierre:

- `execution_manifest.json`
- `summary.json`
- `f1_diagnosis.json`
- `artifact_hashes.json`
- `campaign_closeout.md`

```bash
python3 -m tools.enforcement.diagnose_f1 \
  --runs results/enforcement/campaign-gemma4-r3 \
  --out results/enforcement/campaign-gemma4-r3/f1_diagnosis.json
```

### Criterio de salida

Existe evidencia comparable de al menos dos modelos distintos sobre el mismo benchmark congelado.

## Fase 4. Ablations mínimas

### Objetivo

Aislar qué componentes explican la ventaja de `guarded`.

### Ablations recomendadas

1. sin recovery feedback
2. sin terminal success
3. sin tool filtering o con variante controlada

### Estrategia

No correr inmediatamente el corpus completo. Primero hacer:

- subset adversarial
- `1` o `2` réplicas

Escenarios sugeridos:

- `S-011`
- `S-012`
- `S-013`
- `S-014`
- `S-020`

### Comando sugerido

Si existe una rama o configuración separada para la ablation:

```bash
uv run --group litellm python -m tools.enforcement.run_all \
  --scenarios benchmark/enforcement/scenarios \
  --contracts contracts/enforcement \
  --model-profile benchmark/enforcement/config/model_profiles/default.yaml \
  --replications 1 \
  --out results/enforcement/ablation-<name>
```

### Criterio de salida

Puede explicarse con evidencia qué mecanismo aporta más a la mejora de `guarded`.

## Fase 5. Held-out o corrida final post-freeze

### Objetivo

Blindar el experimento contra la crítica de sobreajuste.

### Opción A

Definir un subconjunto held-out de escenarios que no se use durante la calibración.

### Opción B

Usar el benchmark congelado completo, pero declarar explícitamente una corrida final post-freeze como la evidencia principal de tesis.

### Comandos

Si se usa una lista concreta de escenarios held-out, ejecutar cada uno con `run` o preparar un subconjunto separado.

Si se usa corrida final completa:

```bash
uv run --group litellm python -m tools.enforcement.run_all \
  --scenarios benchmark/enforcement/scenarios \
  --contracts contracts/enforcement \
  --model-profile benchmark/enforcement/config/model_profiles/default.yaml \
  --replications 5 \
  --out results/enforcement/final-freeze-r5
```

Luego:

```bash
python3 -m tools.enforcement.diagnose_f1 \
  --runs results/enforcement/final-freeze-r5 \
  --out results/enforcement/final-freeze-r5/f1_diagnosis.json
```

```bash
python3 -m tools.enforcement.evaluate \
  --runs results/enforcement/final-freeze-r5 \
  --oracle benchmark/enforcement/oracle \
  --out results/enforcement/final-freeze-r5/summary.json
```

### Criterio de salida

La tesis ya tiene una corrida final separada de la fase de calibración.

## Fase 6. Paquete de análisis

Estado:
- completada para el corte canónico de diecisiete campañas cerradas

### Objetivo

Preparar la evidencia que alimentará el capítulo final.

### Elementos requeridos

- tabla por modo:
  - `unsafe_side_effect_rate`
  - `governance_effectiveness`
  - `successful_safe_completion_rate`
  - `precision`
  - `recall`
  - `f1`
  - `mean_latency_ms`
  - `mean_token_usage`
- comparación `guarded` vs `strict`
- comparación `guarded` vs `no_contract`
- análisis por familia de escenario
- análisis de overhead
- hipótesis `H1–H4`

### Artefactos vigentes

- [results/enforcement/statistics/final-seventeen-campaigns.json](/Users/carlos.urteaga/git/agent-contracts-benchmark/results/enforcement/statistics/final-seventeen-campaigns.json:1)
- [docs/resultados_experimento.md](/Users/carlos.urteaga/git/agent-contracts-benchmark/docs/resultados_experimento.md:1)
- [docs/EXECUTIVE_SUMMARY.md](/Users/carlos.urteaga/git/agent-contracts-benchmark/docs/EXECUTIVE_SUMMARY.md:1)

### Cierre metodológico actual

- el artefacto estadístico canónico ya cubre prevención, utilidad, detección runtime y overhead
- `H1–H4` ya quedaron redactadas directamente sobre campañas cerradas
- `campaign-kimi-k26-r3` ya está incorporada al corte canónico actual
- `campaign-kimi-k26-r5`, `campaign-kimi-k27-code-r3`, `campaign-kimi-k27-code-r5`, `campaign-nemotron-3-ultra-r3`, `campaign-nemotron-3-ultra-r5`, `campaign-openai-direct-r3` y `campaign-qwen35-4b` `r3/r5` ya quedaron incorporadas al corte canónico actual
- los reruns exploratorios y smoke-only artifacts no se incorporan al paquete canónico
- el siguiente trabajo ya no es recalcular este bloque, sino decidir expansión selectiva, ablations o redacción

### Criterio de salida

Los resultados ya pueden escribirse como evidencia doctoral y no sólo como reporte técnico.

## Orden mínimo recomendado

Si el tiempo es limitado, ejecutar en este orden:

1. Fase 0. Freeze operacional
2. Fase 1. Validación de entorno
3. Fase 2. Corrida base replicada `×3`
4. Fase 3. Segundo modelo `×3`
5. Fase 4. Ablations mínimas
6. Fase 5. Corrida final post-freeze `×5`
7. Fase 6. Paquete de análisis

## Qué no hacer

- no seguir corrigiendo métricas durante la corrida final
- no mezclar resultados de piloto y resultados congelados
- no cambiar escenarios después de empezar la campaña final
- no comparar modelos con configuraciones contractuales distintas
- no reportar sólo medias puntuales sin separar piloto y fase final

## Regla de versionado post-freeze

| Cambio después del freeze | Acción |
| --- | --- |
| Cambia escenario | `benchmark-v1.1` y rerun completo |
| Cambia contrato | `benchmark-v1.1` y rerun completo |
| Cambia oracle | `benchmark-v1.1` y rerun completo |
| Cambia evaluator | `benchmark-v1.0.1` si es bugfix, pero rerun completo |
| Agrega modelo | No cambia benchmark; se registra en execution manifest |
| Cambia model profile | No cambia benchmark; se registra como nueva condición experimental |

## Resultado esperado

Al terminar este plan, el experimento debe poder sostener esta afirmación:

> Bajo un benchmark congelado, ejecutado con múltiples réplicas y al menos dos modelos, la gobernanza contractual reduce efectos inseguros y el modo `guarded` ofrece una relación superior entre seguridad y utilidad frente a `strict`, con costos operativos medibles y metodológicamente interpretables.

Ésa es la meta operacional del execution plan.
