# Pruebas, complicaciones, adecuaciones, hallazgos y resultados

Esta sección ya no describe el piloto ni la calibración. Desde el `2026-06-14`, el benchmark vigente quedó congelado como `benchmark-v1.0`, y los perfiles de modelo pasaron a tratarse como `execution conditions` de campañas post-freeze. Al `2026-06-17`, el bloque post-freeze principal ya cuenta con seis campañas cerradas y un paquete estadístico final reproducible.

## Estado metodológico

- `benchmark-v1.0` quedó congelado el `2026-06-14`.
- La identidad del benchmark está anclada en [benchmark/enforcement/benchmark_manifest.json](/Users/carlos.urteaga/git/agent-contracts-benchmark/benchmark/enforcement/benchmark_manifest.json:1).
- Los perfiles de modelo no redefinen el benchmark; sólo documentan la condición experimental de cada campaña.
- Resultados débiles pero metodológicamente válidos no reabren el benchmark.

## Campañas cerradas disponibles

Las campañas cerradas y utilizables para análisis final son:

- `campaign-base-r3`
  - perfil: `litellm:ollama_chat/qwen2.5:7b`
  - matriz: `21 × 4 × 3 = 252` corridas
- `campaign-base-r5`
  - perfil: `litellm:ollama_chat/qwen2.5:7b`
  - matriz: `21 × 4 × 5 = 420` corridas
- `campaign-gemma4-r3`
  - perfil: `litellm:ollama_chat/gemma4:26b`
  - matriz: `21 × 4 × 3 = 252` corridas
- `campaign-deepseek-v4-pro-r3`
  - perfil: `litellm:ollama_chat/deepseek-v4-pro:cloud`
  - matriz: `21 × 4 × 3 = 252` corridas
- `campaign-gpt-oss-120b-r3`
  - perfil: `litellm:ollama_chat/gpt-oss:120b-cloud`
  - matriz: `21 × 4 × 3 = 252` corridas
- `campaign-qwen35-397b-r3`
  - perfil: `litellm:ollama_chat/qwen3.5:397b-cloud`
  - matriz: `21 × 4 × 3 = 252` corridas

## Artefacto estadístico final vigente

El análisis inferencial final vigente se genera con:

- [results/enforcement/statistics/final-six-campaigns.json](/Users/carlos.urteaga/git/agent-contracts-benchmark/results/enforcement/statistics/final-six-campaigns.json:1)

Este artefacto:

- usa `bootstrap` al `95%`
- reporta métricas por modo
- mantiene campañas separadas por modelo
- no mezcla modelos distintos en una sola media sin etiquetado explícito
- permite comparar estabilidad del modelo base y sensibilidad del benchmark a backend

## Hallazgo principal del modelo base

El patrón central del benchmark congelado se mantiene y se fortalece al extender el modelo base a `campaign-base-r5`.

En `campaign-base-r5`:

- `guarded` conserva `governance_effectiveness = 1.0`
- `strict` también conserva `governance_effectiveness = 1.0`
- `guarded` preserva mucha más utilidad:
  - `successful_safe_completion_rate = 0.904762`
  - intervalo bootstrap `95%`: `[0.847619, 0.952381]`
- `strict` queda muy por debajo:
  - `successful_safe_completion_rate = 0.342857`
  - intervalo bootstrap `95%`: `[0.257143, 0.438095]`
- la diferencia pareada `guarded vs strict` en `successful_safe_completion_rate` es:
  - `0.561905`
  - intervalo bootstrap `95%`: `[0.466666, 0.657143]`

En detección runtime, `guarded` en `campaign-base-r5` mantiene:

- `f1 = 0.789474`
- intervalo bootstrap `95%`: `[0.666667, 0.881356]`

Eso sigue sosteniendo el hallazgo principal de la tesis: el modo `guarded` mantiene la prevención sin pagar el mismo costo de utilidad que `strict`.

## Lectura comparativa de los otros modelos

Los cuatro modelos adicionales conservan el mismo patrón cualitativo de utilidad a favor de `guarded`, pero con magnitudes distintas:

- `campaign-gemma4-r3`
  - `guarded successful_safe_completion_rate = 0.730159`
  - `strict successful_safe_completion_rate = 0.0`
  - `guarded f1 = 0.363636`
  - `guarded vs strict` en `successful_safe_completion_rate = 0.730159`
- `campaign-deepseek-v4-pro-r3`
  - `guarded successful_safe_completion_rate = 0.84127`
  - `strict successful_safe_completion_rate = 0.571429`
  - `guarded f1 = 0.5`
  - `guarded vs strict` en `successful_safe_completion_rate = 0.269841`
- `campaign-gpt-oss-120b-r3`
  - `guarded successful_safe_completion_rate = 0.746032`
  - `strict successful_safe_completion_rate = 0.47619`
  - `guarded f1 = 0.347826`
  - `guarded vs strict` en `successful_safe_completion_rate = 0.269842`
- `campaign-qwen35-397b-r3`
  - `guarded successful_safe_completion_rate = 0.761905`
  - `strict successful_safe_completion_rate = 0.52381`
  - `guarded f1 = 0.285715`
  - `guarded vs strict` en `successful_safe_completion_rate = 0.238095`

En los seis cierres, cuando `guarded` tiene oportunidades de intervención bloqueante, `governance_effectiveness` se mantiene en `1.0`. La variación entre modelos aparece sobre todo en calidad de detección runtime y en cuánta utilidad conserva cada backend bajo `strict`.

## Interpretación de este bloque

Con las seis campañas cerradas disponibles, la evidencia post-freeze permite sostener cinco puntos:

1. El benchmark congelado sigue produciendo oportunidades reales de enforcement.
2. `guarded` y `strict` continúan previniendo efectos inseguros cuando la gobernanza bloqueante actúa correctamente.
3. En el modelo base, `guarded` preserva de forma robusta mucha más finalización segura que `strict`, incluso al escalar de `r3` a `r5`.
4. En los modelos adicionales, el patrón `guarded > strict` en utilidad persiste, pero con degradación variable en detección runtime.
5. Las diferencias observadas ahora provienen de campañas post-freeze cerradas, no de calibración del benchmark.

## Conclusión de resultados

El Step 10 post-freeze ya quedó cerrado para estas campañas. El benchmark sigue congelado como `benchmark-v1.0`, el modelo base cuenta con campañas `r3` y `r5`, hay cuatro campañas comparativas `r3` adicionales, y ya existe un paquete estadístico final reproducible para este conjunto de evidencia.
