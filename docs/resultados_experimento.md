# Pruebas, complicaciones, adecuaciones, hallazgos y resultados

Esta sección ya no debe leerse como un reporte del piloto de calibración. Desde el `2026-06-14`, el benchmark vigente quedó congelado como `benchmark-v1.0`, y los perfiles de modelo pasaron a tratarse como `execution conditions` de campañas post-freeze. Por tanto, los resultados relevantes para la tesis se organizan por campañas cerradas contra el mismo benchmark congelado.

## Estado metodológico

- `benchmark-v1.0` quedó congelado el `2026-06-14`.
- Los artefactos congelados se identifican por `benchmark/enforcement/benchmark_manifest.json`.
- Los perfiles de modelo no redefinen el benchmark; sólo documentan la condición experimental de cada campaña.
- Resultados débiles pero metodológicamente válidos no reabren el benchmark.

## Campañas cerradas disponibles

Al `2026-06-16`, existen dos campañas post-freeze cerradas y utilizables para análisis estadístico interino:

- `campaign-base-r3`
  - perfil: `litellm:ollama_chat/qwen2.5:7b`
  - matriz: `21 × 4 × 3 = 252` corridas
  - estado: validada con cierre formal
- `campaign-gemma4-r3`
  - perfil: `litellm:ollama_chat/gemma4:26b`
  - matriz: `21 × 4 × 3 = 252` corridas
  - estado: validada con cierre formal

La campaña objetivo del modelo base `campaign-base-r5` sigue pendiente para el cierre final del bloque post-freeze.

## Artefacto estadístico vigente

El análisis inferencial actual se genera con:

- [results/enforcement/statistics/interim-base-r3-plus-gemma4-r3.json](/Users/carlos.urteaga/git-clone/Architectural-Contracts/results/enforcement/statistics/interim-base-r3-plus-gemma4-r3.json:1)

Este artefacto:

- usa `bootstrap` al `95%`
- reporta métricas por modo
- mantiene campañas separadas por modelo
- no mezcla modelos distintos en una sola media sin etiquetado explícito

## Hallazgos interinos del modelo base

En `campaign-base-r3`, el patrón central del benchmark congelado se mantiene:

- `guarded` conserva `governance_effectiveness = 1.0`
- `strict` también conserva `governance_effectiveness = 1.0`
- `guarded` preserva mucha más utilidad:
  - `successful_safe_completion_rate = 0.888889`
  - intervalo bootstrap `95%`: `[0.809524, 0.952381]`
- `strict` queda muy por debajo:
  - `successful_safe_completion_rate = 0.333333`
  - intervalo bootstrap `95%`: `[0.222222, 0.460317]`

La diferencia pareada `guarded vs strict` en `successful_safe_completion_rate` es:

- `0.555556`
- intervalo bootstrap `95%`: `[0.428572, 0.68254]`

Eso sostiene, al menos de forma interina, el hallazgo principal de la tesis: el modo `guarded` mantiene la prevención sin pagar el mismo costo de utilidad que `strict`.

## Hallazgos interinos del segundo modelo

En `campaign-gemma4-r3`, el patrón cambia en magnitud pero no invalida el benchmark:

- `guarded` mantiene `governance_effectiveness = 1.0`
- `strict` muestra una degradación operativa fuerte
- la detección runtime de `guarded` es más conservadora:
  - `precision = 1.0`
  - `recall = 0.222222`
  - `f1 = 0.363636`

Este resultado no reabre el benchmark. Por regla metodológica, un resultado peor pero válido sólo documenta sensibilidad al modelo; no justifica rediseñar escenarios, contratos, oracle o evaluator.

## Interpretación actual

Con las dos campañas cerradas disponibles, la evidencia post-freeze ya permite sostener cuatro puntos:

1. El benchmark congelado sigue produciendo oportunidades reales de enforcement.
2. `guarded` y `strict` continúan previniendo efectos inseguros cuando la gobernanza bloqueante actúa correctamente.
3. `guarded` preserva mejor la finalización segura que `strict` en el modelo base cerrado.
4. El patrón no debe interpretarse con una sola campaña ni con un solo modelo; por eso sigue pendiente `campaign-base-r5`.

## Qué falta para el cierre final

Esta sección todavía no debe tratarse como cierre estadístico definitivo. Para eso falta:

- cerrar `campaign-base-r5` con `21 × 4 × 5 = 420` corridas válidas
- regenerar el paquete estadístico final con la campaña base extendida
- actualizar tablas y narrativa final con la evidencia completa post-freeze

Mientras eso no ocurra, el estado correcto es:

- benchmark: congelado
- ejecución: en curso post-freeze
- análisis: interino, no final
