# Roadmap doctoral

## Fase 1. Freeze metodológico

Objetivo:
- congelar el benchmark antes de comparar modelos

Estado:
- completada como `benchmark-v1.0` el `2026-06-14`

Criterio de salida:
- ninguna métrica, escenario, contrato, oracle o evaluator cambia más dentro de `benchmark-v1.0`; las campañas posteriores sólo cambian execution conditions documentadas

## Fase 2. Infraestructura de ejecución

Objetivo:
- dejar el harness listo para corridas grandes, sin intervención manual

Estado:
- completada

Entregables cerrados:
- pipeline de ejecución reproducible
- reanudación por `--resume`
- manifests de ejecución
- validate/closeout por campaña

## Fase 3. Réplicas del modelo base

Objetivo:
- medir estabilidad con el modelo base

Estado:
- completada

Artefactos cerrados:
- `campaign-base-r3`
- `campaign-base-r5`

Resultado:
- el modelo base ya no depende sólo de `r3`

## Fase 4. Comparación multi-modelo

Objetivo:
- reducir dependencia de un solo backend

Estado actual:
- comparación inicial completada con cinco campañas `r3` adicionales

Campañas cerradas:
- `campaign-gemma4-r3`
- `campaign-deepseek-v4-pro-r3`
- `campaign-gpt-oss-120b-r3`
- `campaign-kimi-k26-r3`
- `campaign-qwen35-397b-r3`
- `campaign-gpt-oss-120b-r5`
- `campaign-deepseek-v4-pro-r5`

Resultado:
- el patrón `guarded > strict` en utilidad se mantiene
- la calidad de detección runtime depende materialmente del backend
- `gpt-oss` y `deepseek` ya cuentan con expansión `r5` y ya entran al corte estadístico final vigente

## Fase 5. Estadística inferencial

Objetivo:
- transformar resultados descriptivos en evidencia comparativa formal

Estado:
- completada para el corte canónico de dieciocho campañas cerradas

Artefacto vigente:
- [results/enforcement/statistics/final-eighteen-campaigns.json](/Users/carlos.urteaga/git/agent-contracts-benchmark/results/enforcement/statistics/final-eighteen-campaigns.json:1)

Incluye:
- bootstrap al `95%`
- métricas por modo
- métricas de recuperación y overhead
- comparaciones `guarded vs strict`, `guarded vs no_contract`, `guarded vs advisory`, `strict vs no_contract`, `strict vs advisory`
- campañas reportadas por separado, sin mezcla entre modelos
- cierre narrativo directo para `H1–H4`

## Fase 6. Oracle formalizado

Objetivo:
- tratar el oracle como instrumento experimental explícito y validable

Estado:
- formalización implementada y validada

Implicación metodológica:
- cualquier adopción de un oracle distinto obligaría a nueva versión de benchmark y rerun completo

## Fase 7. Siguiente bloque experimental

Objetivo:
- decidir cómo ampliar evidencia sin reabrir `benchmark-v1.0`

Bloque activo actual:
- decidir si `campaign-nemotron-3-ultra-r3` merece expansión a `r5`
- decidir si hace falta otra expansión `r5` no base o si el paquete actual ya es suficiente
- pasar a ablations o a redacción doctoral con el paquete canónico actual

Opciones razonables:
- extender a `r5` el mejor candidato no base
- abrir un bloque de ablations
- preparar el capítulo de resultados con el paquete actual, sin incorporar reruns exploratorios

## Fase 8. Ablations

Objetivo:
- aislar qué mecanismos producen la mejora

Pendiente:
- sin recovery feedback
- sin terminal success
- sin tool filtering o con exposición más amplia controlada

## Fase 9. Redacción doctoral

Objetivo:
- convertir el paquete experimental en capítulo defendible

Incluye:
- benchmark congelado
- oracle como instrumento
- resultados por hipótesis
- amenazas a la validez
- sensibilidad por modelo

## Prioridad realista

La secuencia más eficiente desde aquí es:

1. decidir si hace falta una única expansión selectiva `r5` fuera del modelo base
2. pasar a ablations si se necesita explicación causal adicional de `guarded > strict`
3. consolidar redacción doctoral sobre el paquete canónico ya cerrado
