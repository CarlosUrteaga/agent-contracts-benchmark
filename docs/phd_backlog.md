# Backlog evolutivo del experimento doctoral

## Objetivo del backlog

Este backlog organiza el trabajo en evoluciones. Cada evolución busca cerrar una brecha concreta del experimento sin mezclar desarrollo del benchmark con ejecución final. La idea es pasar de:

- benchmark funcional

a:

- benchmark congelado
- pipeline ejecutable
- evidencia replicada
- análisis doctoral defendible

## Criterios de priorización

Se usa la siguiente lógica:

- `P0`
  bloquea defensa doctoral si no se resuelve
- `P1`
  fortalece seriamente el valor científico
- `P2`
  mejora profundidad, publicación o extensión

## Evolución 1. Freeze del benchmark

Prioridad:
- `P0`

Estado:
- completada el `2026-06-14` como `benchmark-v1.0`

Objetivo:
- separar explícitamente calibración y evaluación final

Backlog:
- documentar qué partes cambiaron durante la calibración
- declarar qué archivos quedan congelados
- crear una versión identificable del benchmark final
- dejar por escrito qué `summary.json` y qué evaluator son los autoritativos
- fijar la redacción final de `H1–H4`

Definition of Done:
- existe una “versión congelada” del benchmark
- ya no se cambian reglas, escenarios ni evaluator antes de la corrida doctoral

Nota:
- los `model profiles` no forman parte del benchmark congelado; se registran como execution conditions por campaña

## Evolución 2. Harness operativo

Prioridad:
- `P0`

Objetivo:
- dejar el sistema listo para ejecutar lotes grandes sin intervención manual

Backlog:
- comando único para corridas completas
- comando único para evaluación y diagnóstico
- estructura estable de resultados por modelo/modo/réplica
- checklist de prerrequisitos
- cálculo o estimación de tiempo por corrida
- validación previa de entorno y perfil de modelo

Definition of Done:
- el equipo puede correr el benchmark sin tocar el código
- el trabajo deja de ser de desarrollo y pasa a ser de ejecución

Bloque activo inmediato:
- cierre de `campaign-base-r5`
- consolidación del paquete estadístico post-freeze
- actualización final de resultados y resumen ejecutivo

## Evolución 3. Réplicas del modelo base

Prioridad:
- `P0`

Objetivo:
- obtener estabilidad experimental del backend actual

Estado interino:
- `campaign-base-r3` ya quedó cerrada

Backlog restante:
- extender a `21 × 4 × 5`
- consolidar resultados por escenario y por modo
- generar distribuciones, no sólo medias

Definition of Done:
- `campaign-base-r3` y `campaign-base-r5` están cerradas
- cada métrica principal tiene variación observable y no sólo un valor puntual

## Evolución 4. Paquete estadístico

Prioridad:
- `P0`

Objetivo:
- convertir el experimento de descriptivo a inferencial

Estado interino:
- existe `tools/enforcement/bootstrap_metrics.py`
- existe un artefacto interino con campañas cerradas separadas por modelo

Backlog:
- bootstrap para:
  - `successful_safe_completion_rate`
  - `governance_effectiveness`
  - `precision`
  - `recall`
  - `f1`
- intervalos de confianza al `95%`
- comparación de `guarded` vs `strict`
- comparación de `guarded` vs `no_contract`
- tamaño de efecto
- análisis de múltiple comparación si aplica

Definition of Done:
- el capítulo de resultados puede justificar diferencias con análisis formal

## Evolución 5. Segundo modelo

Prioridad:
- `P0`

Objetivo:
- reducir sesgo por dependencia de `qwen2.5:7b`

Estado interino:
- `gemma4:26b` ya está integrado como segundo perfil LiteLLM
- `campaign-gemma4-r3` ya quedó cerrada

Backlog restante:
- comparar el patrón de `campaign-gemma4-r3` contra el cierre final del modelo base

Secuencia obligatoria restante:
- cerrar `campaign-base-r5`
- regenerar el paquete estadístico final incluyendo base extendida y segundo modelo

Recomendación:
- primero un abierto/local comparable
- luego, si alcanza tiempo o presupuesto, un modelo API pequeño

Default elegido:
- `benchmark/enforcement/config/model_profiles/gemma4_26b.yaml`
- `provider: "litellm"`
- `model_id: "ollama_chat/gemma4:26b"`
- `openai_chat.yaml` sólo como fallback opcional

Definition of Done:
- la tesis ya no depende de un solo backend
- la comparación entre modelos aparece en el paquete estadístico final

## Evolución 6. Oracle formalizado

Prioridad:
- `P1`

Objetivo:
- tratar el oracle como instrumento experimental

Backlog:
- documentar entradas y salidas del oracle
- definir oportunidad de violación
- definir criterios de outcome aceptable y prohibido
- documentar exclusiones de runtime F1
- materializar un catálogo validable del oracle
- agregar regresión automática contra drift del catálogo o de la spec
- versionar el oracle si se adopta como benchmark vigente

Opcional fuerte:
- validación externa pequeña con revisores humanos

Estado interino:
- `docs/oracle_spec.md`, `docs/oracle_traceability_matrix.md` y `tools/enforcement/validate_oracle.py` ya existen
- falta decidir si esta formalización se promueve a una nueva versión de benchmark con rerun completo

Definition of Done:
- otro lector puede entender y reproducir la lógica de evaluación

## Evolución 7. Held-out o corrida final post-freeze

Prioridad:
- `P1`

Objetivo:
- blindar contra sobreajuste del benchmark a la calibración

Backlog:
- definir subconjunto held-out
- o ejecutar una corrida final completa sólo después del freeze
- reportar esos resultados por separado

Definition of Done:
- existe evidencia final independiente de la calibración

## Evolución 8. Ablations

Prioridad:
- `P1`

Objetivo:
- entender qué componentes producen la mejora

Backlog mínimo:
- ablation sin recovery feedback
- ablation sin terminal success
- ablation sin tool filtering o con filtro relajado controlado

Preguntas a responder:
- ¿`guarded` mejora por el bloqueo?
- ¿por la recuperación?
- ¿por ambos?

Definition of Done:
- la mejora ya no es sólo observada; también es explicable por componentes

## Evolución 9. Análisis por familia de escenarios

Prioridad:
- `P1`

Objetivo:
- evitar que el promedio global esconda patrones importantes

Backlog:
- separar nominales vs adversariales
- separar por tipo de riesgo:
  - evidencia
  - autorización
  - memoria
  - notificaciones
  - ledger/fingerprint
- reportar dónde `guarded` funciona mejor y dónde falla más

Definition of Done:
- el análisis ya no depende sólo de promedios globales

## Evolución 10. Overhead defendible

Prioridad:
- `P1`

Objetivo:
- fortalecer `H4`

Backlog:
- tabla completa de overhead por modo
- costo de tokens por modo
- latencia por modo
- costo por acción bloqueada
- costo por recuperación exitosa
- costo por familia de escenario

Definition of Done:
- `H4` se sostiene no sólo con números aislados, sino con análisis de costo-efectividad

## Evolución 11. Amenazas a la validez

Prioridad:
- `P1`

Objetivo:
- cerrar la defensa metodológica

Backlog:
- validez interna
- validez externa
- validez de constructo
- validez de conclusión

Definition of Done:
- la tesis responde explícitamente a las objeciones metodológicas más previsibles

## Evolución 12. Extensiones publicables

Prioridad:
- `P2`

Objetivo:
- convertir la tesis en agenda de publicaciones

Opciones:
- tercer modelo
- segundo dominio
- taxonomía de amenazas más profunda
- integración con herramienta real
- experimentos de evasión semántica

Definition of Done:
- existe una ruta clara de paper 2 / paper 3 sin bloquear la tesis principal

## Qué sí basta y qué no basta

### Sí basta como primera meta

- dejar el harness congelado y ejecutable

### No basta para cerrar el PhD

- dejar sólo el código listo
- correr una sola réplica más
- tener sólo medias puntuales
- depender de un solo modelo

## Secuencia mínima recomendada

Si hubiera que reducir el trabajo a lo estrictamente necesario, el orden sería:

1. Evolución 1: freeze
2. Evolución 2: harness operativo
3. Evolución 3: réplicas del modelo base
4. Evolución 4: análisis estadístico
5. Evolución 5: segundo modelo
6. Evolución 6: oracle formalizado
7. Evolución 8: ablations
8. Evolución 11: amenazas a la validez

## Resultado esperado del backlog

Al terminar estas evoluciones, el experimento ya no se presentará como:

- “un benchmark interesante que funcionó en un piloto”

sino como:

- “un benchmark congelado, replicado, comparado entre modelos y analizado con inferencia estadística, que demuestra que `guarded` ofrece una relación superior entre seguridad y utilidad frente a `strict` bajo condiciones controladas”

Ése es el cambio real que este backlog debe producir.
