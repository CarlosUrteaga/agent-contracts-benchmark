# Backlog doctoral

## Estado general

`benchmark-v1.0` ya está congelado. El bloque post-freeze principal también ya quedó cerrado con:

- `campaign-base-r3`
- `campaign-base-r5`
- `campaign-gemma4-r3`
- `campaign-deepseek-v4-pro-r3`
- `campaign-gpt-oss-120b-r3`
- `campaign-qwen35-397b-r3`
- [results/enforcement/statistics/final-six-campaigns.json](/Users/carlos.urteaga/git/agent-contracts-benchmark/results/enforcement/statistics/final-six-campaigns.json:1)

## P0 — Narrativa final comparativa

Objetivo:
- convertir el cierre estadístico actual en tablas y argumentos doctorales explícitos

Backlog:
- redactar comparación por hipótesis `H1–H4`
- consolidar tabla por campaña y por modo
- explicitar qué cambia entre utilidad, prevención y detección runtime
- dejar claro que variación entre modelos no implica drift metodológico

Definition of Done:
- el capítulo de resultados puede apoyarse directamente en el paquete de seis campañas cerradas

## P0 — Decisión de expansión selectiva

Objetivo:
- decidir si hace falta una expansión `r5` fuera del modelo base

Backlog:
- comparar `deepseek-v4-pro`, `gpt-oss` y `qwen3.5` como candidatos de expansión
- decidir un solo candidato si se abre `r5`
- justificar por qué se expande o por qué no hace falta

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
