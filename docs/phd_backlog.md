# Backlog doctoral

## Estado general

`benchmark-v1.0` ya está congelado. El bloque post-freeze principal también ya quedó cerrado con:

- `campaign-base-r3`
- `campaign-base-r5`
- `campaign-claude-opus-48-r3`
- `campaign-gemma4-r3`
- `campaign-deepseek-v4-pro-r3`
- `campaign-gpt-oss-120b-r3`
- `campaign-kimi-k26-r3`
- `campaign-kimi-k26-r5`
- `campaign-kimi-k27-code-r3`
- `campaign-kimi-k27-code-r5`
- `campaign-nemotron-3-ultra-r3`
- `campaign-nemotron-3-ultra-r5`
- `campaign-openai-direct-r3`
- `campaign-openai-xhigh-r3`
- `campaign-qwen35-397b-r3`
- `campaign-qwen35-4b-r3`
- `campaign-qwen35-4b-r5`
- `campaign-gpt-oss-120b-r5`
- `campaign-deepseek-v4-pro-r5`
- [results/enforcement/statistics/final-nineteen-campaigns.json](/Users/carlos.urteaga/git/agent-contracts-benchmark/results/enforcement/statistics/final-nineteen-campaigns.json:1)

## P0 — Narrativa final comparativa

Objetivo:
- convertir el cierre estadístico actual en tablas y argumentos doctorales explícitos

Estado:
- completado sobre el corte canónico de diecinueve campañas

Entregables cerrados:
- comparación por hipótesis `H1–H4`
- lectura separada de prevención, utilidad, detección runtime y overhead
- aclaración explícita de que la variación entre modelos no implica drift metodológico
- exclusión explícita de reruns exploratorios y smoke-only artifacts del paquete canónico

Definition of Done:
- el capítulo de resultados puede apoyarse directamente en el paquete de diecinueve campañas cerradas

## P0 — Decisión de expansión selectiva

Objetivo:
- decidir si hace falta una expansión `r5` fuera del modelo base

Backlog:
- comparar `deepseek-v4-pro`, `gpt-oss` y `qwen3.5` como candidatos de expansión
- decidir un solo candidato si se abre `r5`
- justificar por qué se expande o por qué no hace falta
- decidir si `nemotron-3-ultra:cloud` merece expansión a `r5`
- mantener fuera del corte canónico cualquier rerun exploratorio no cerrado como campaña

Definition of Done:
- existe una decisión explícita de seguir o no con un `r5` no base

## P1 — Ablations

Objetivo:
- aislar qué componente produce la ventaja de `guarded`

Backlog:
- sin recovery feedback
- sin terminal success
- sin filtrado de herramientas

Definition of Done:
- hay al menos una explicación causal más fuerte de `guarded > strict`

## P1 — Oracle como instrumento

Objetivo:
- mantener el oracle defendible como artefacto metodológico

Backlog:
- referenciar la formalización del oracle dentro del capítulo metodológico
- conectar oracle, evaluator y métricas con amenazas a la validez

Definition of Done:
- un lector puede reconstruir el instrumento sin inferencias implícitas

## P1 — Redacción doctoral

Objetivo:
- pasar de artefactos técnicos a argumento de tesis

Backlog:
- metodología congelada
- amenazas a la validez
- resultados por hipótesis
- resultados por familia de escenario
- sensibilidad por backend

Definition of Done:
- existe una narrativa defendible y trazable desde benchmark hasta resultados
