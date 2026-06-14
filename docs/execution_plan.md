# Execution Plan

## Objetivo

Este documento define el plan operativo para ejecutar el experimento doctoral sin seguir modificando el benchmark durante la fase de evaluación. Su propósito es convertir el estado actual del proyecto en una secuencia de corridas reproducibles, con puntos de control claros y artefactos verificables.

La regla central es:

> primero se congela el benchmark, después se ejecuta, y sólo al final se analiza.

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
- [tools/enforcement/evaluate.py](/Users/carlos.urteaga/git-clone/Architectural-Contracts/tools/enforcement/evaluate.py:1)
- [tools/enforcement/diagnose_f1.py](/Users/carlos.urteaga/git-clone/Architectural-Contracts/tools/enforcement/diagnose_f1.py:1)
- [benchmark/enforcement/config/model_profiles/default.yaml](/Users/carlos.urteaga/git-clone/Architectural-Contracts/benchmark/enforcement/config/model_profiles/default.yaml:1)

## Fase 0. Freeze operacional

### Objetivo

Congelar el benchmark antes de la corrida doctoral.

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

### Checklist

- no cambiar escenarios
- no cambiar contratos
- no cambiar evaluator
- no cambiar diagnosis
- no cambiar semántica terminal
- no cambiar perfiles de modelo durante esta fase

### Evidencia a guardar

- hash del commit congelado
- copia del `summary.json` del piloto previo
- nota de freeze con fecha

### Comandos

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

El benchmark queda declarado como versión congelada para evaluación. A partir de aquí ya no se hacen cambios metodológicos antes de los lotes finales.

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

### Objetivo

Ejecutar la validación pre-freeze completa de `21 × 4 × 1` de forma reanudable y segura.

### Regla operativa

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

El benchmark queda **freeze-ready** sólo si:

- la campaña completa tiene `84` runs válidos
- cada run tiene `summary.json`
- cada run tiene `trace.jsonl`
- cada run tiene `run_ledger.json`
- cada run tiene `run_complete.json`
- no existen directorios parciales o corruptos contados como completos
- `f1_diagnosis.json` se genera correctamente
- `summary.json` se genera correctamente

## Fase 2. Corrida base replicada del modelo actual

### Objetivo

Ejecutar el benchmark completo sobre el modelo base congelado.

### Lote mínimo doctoral

- `21 × 4 × 3 = 252` corridas

### Lote objetivo

- `21 × 4 × 5 = 420` corridas

### Organización recomendada

Usar carpetas separadas por campaña:

- `results/enforcement/campaign-base-r3/`
- `results/enforcement/campaign-base-r5/`

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

### Artefactos a guardar

- `summary.json`
- `f1_diagnosis.json`
- trazas por corrida
- ledger por corrida

### Criterio de salida

Existen distribuciones por modo y por escenario para el modelo base, no sólo resultados puntuales.

## Fase 3. Segundo modelo

### Objetivo

Reducir la dependencia de un solo backend.

### Recomendación mínima

Agregar un segundo perfil:

- modelo abierto/local comparable, por ejemplo `llama3.1:8b`

### Recomendación fuerte

Agregar además un tercer perfil API pequeño:

- por ejemplo `gpt-4o-mini` vía LiteLLM

### Preparación

Crear o verificar perfiles adicionales en:

- `benchmark/enforcement/config/model_profiles/`

Ejemplos sugeridos:

- `llama31_8b.yaml`
- `gpt4o_mini.yaml`

### Ejecución

Para cada modelo adicional:

```bash
uv run --group litellm python -m tools.enforcement.run_all \
  --scenarios benchmark/enforcement/scenarios \
  --contracts contracts/enforcement \
  --model-profile benchmark/enforcement/config/model_profiles/<perfil>.yaml \
  --replications 3 \
  --out results/enforcement/<campaign-name>
```

### Post-proceso

```bash
python3 -m tools.enforcement.diagnose_f1 \
  --runs results/enforcement/<campaign-name> \
  --out results/enforcement/<campaign-name>/f1_diagnosis.json
```

```bash
python3 -m tools.enforcement.evaluate \
  --runs results/enforcement/<campaign-name> \
  --oracle benchmark/enforcement/oracle \
  --out results/enforcement/<campaign-name>/summary.json
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
