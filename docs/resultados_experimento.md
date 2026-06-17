# Pruebas, complicaciones, adecuaciones, hallazgos y resultados

Esta sección ya no debe leerse como un reporte del piloto de calibración. Desde el `2026-06-14`, el benchmark vigente quedó congelado como `benchmark-v1.0`, y los perfiles de modelo pasaron a tratarse como `execution conditions` de campañas post-freeze. Al `2026-06-17`, el bloque principal de ejecución y análisis post-freeze ya cuenta con tres campañas cerradas y con un paquete estadístico final reproducible.

## Estado metodológico

- `benchmark-v1.0` quedó congelado el `2026-06-14`.
- Los artefactos congelados se identifican por `benchmark/enforcement/benchmark_manifest.json`.
- Los perfiles de modelo no redefinen el benchmark; sólo documentan la condición experimental de cada campaña.
- Resultados débiles pero metodológicamente válidos no reabren el benchmark.

## Campañas cerradas disponibles

Las campañas cerradas y utilizables para análisis final son:

- `campaign-base-r3`
  - perfil: `litellm:ollama_chat/qwen2.5:7b`
  - matriz: `21 × 4 × 3 = 252` corridas
  - estado: validada con cierre formal
- `campaign-base-r5`
  - perfil: `litellm:ollama_chat/qwen2.5:7b`
  - matriz: `21 × 4 × 5 = 420` corridas
  - estado: validada con cierre formal
- `campaign-gemma4-r3`
  - perfil: `litellm:ollama_chat/gemma4:26b`
  - matriz: `21 × 4 × 3 = 252` corridas
  - estado: validada con cierre formal

## Artefacto estadístico final

El análisis inferencial final vigente se genera con:

- [results/enforcement/statistics/final-base-r3-base-r5-gemma4-r3.json](/Users/carlos.urteaga/git-clone/Architectural-Contracts/results/enforcement/statistics/final-base-r3-base-r5-gemma4-r3.json:1)

Este artefacto:

- usa `bootstrap` al `95%`
- reporta métricas por modo
- mantiene campañas separadas por modelo
- no mezcla modelos distintos en una sola media sin etiquetado explícito
- permite comparar estabilidad del modelo base entre `r3` y `r5`

## Hallazgos finales del modelo base

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

La diferencia pareada `guarded vs strict` en `successful_safe_completion_rate` para `campaign-base-r5` es:

- `0.561905`
- intervalo bootstrap `95%`: `[0.466666, 0.657143]`

La señal no sólo persiste respecto a `campaign-base-r3`; también se vuelve más estable con más réplica. En detección runtime, `guarded` en `campaign-base-r5` mantiene:

- `f1 = 0.789474`
- intervalo bootstrap `95%`: `[0.666667, 0.881356]`

Eso sostiene el hallazgo principal de la tesis: el modo `guarded` mantiene la prevención sin pagar el mismo costo de utilidad que `strict`.

## Lectura del segundo modelo

En `campaign-gemma4-r3`, el benchmark congelado sigue distinguiendo prevención de utilidad, pero el patrón cambia de magnitud:

- `guarded` mantiene `governance_effectiveness = 1.0`
- `guarded` conserva mejor utilidad que `strict`:
  - `successful_safe_completion_rate = 0.730159`
  - intervalo bootstrap `95%`: `[0.619048, 0.84127]`
- `strict` cae a:
  - `successful_safe_completion_rate = 0.0`
  - intervalo bootstrap `95%`: `[0.0, 0.0]`
- la detección runtime de `guarded` es mucho más débil que en el modelo base:
  - `f1 = 0.363636`
  - intervalo bootstrap `95%`: `[0.0, 0.666667]`

Este resultado no reabre el benchmark. Por regla metodológica, un resultado peor pero válido documenta sensibilidad al modelo, no drift metodológico del benchmark.

## Interpretación final de este bloque

Con las tres campañas cerradas disponibles, la evidencia post-freeze permite sostener cinco puntos:

1. El benchmark congelado sigue produciendo oportunidades reales de enforcement.
2. `guarded` y `strict` continúan previniendo efectos inseguros cuando la gobernanza bloqueante actúa correctamente.
3. En el modelo base, `guarded` preserva de forma robusta mucha más finalización segura que `strict`, incluso al escalar de `r3` a `r5`.
4. El segundo modelo muestra que el hallazgo depende también del backend, especialmente en calidad de detección y comportamiento bajo aborto estricto.
5. Las diferencias observadas ahora provienen de campañas post-freeze cerradas, no de calibración del benchmark.

## Conclusión de resultados

El bloque principal de ejecución y análisis post-freeze ya quedó cerrado para estas campañas. El benchmark está congelado, el modelo base cuenta con una campaña extendida `r5`, existe un segundo modelo comparativo cerrado y ya hay un paquete estadístico final reproducible para este conjunto de evidencia.
