# Roadmap doctoral del experimento

## Propósito

Este roadmap organiza la transición desde el estado actual del benchmark hacia un paquete experimental doctoralmente defendible. La idea no es rediseñar la contribución central, sino cerrar las brechas de robustez, replicación, generalización y rigor metodológico.

La tesis ya tiene una base funcional:

- benchmark ejecutable
- cuatro modos contrastantes: `no_contract`, `advisory`, `guarded`, `strict`
- escenarios nominales y adversariales
- métricas de seguridad, utilidad, detección y costo
- un hallazgo central claro:
  - `guarded` mantiene `governance_effectiveness = 1.0`
  - pero preserva mucha más finalización segura que `strict`

Lo que falta no es “tener otra idea”, sino cerrar la evidencia para que el resultado sea defendible con nivel doctoral.

## Pregunta guía

La pregunta ya no es si el Governor funciona en un piloto, sino:

> Bajo un benchmark congelado, replicado y evaluado estadísticamente, ¿la gobernanza contractual reduce efectos inseguros y ofrece un mejor equilibrio seguridad-utilidad que alternativas más débiles o más rígidas?

## Principio rector

Primero se congela el benchmark. Después se ejecuta. Después se analiza. No al revés.

Eso implica separar con claridad:

1. fase de calibración
2. fase congelada
3. fase de ejecución final
4. fase de análisis estadístico

## Qué significa “dejar el harness listo”

Sí, la primera meta práctica debe ser dejar el harness listo para correr sin seguir tocando la lógica central. Pero eso, por sí solo, no basta.

Dejar el harness listo debe significar:

- escenarios congelados
- contratos congelados
- oracle congelado
- evaluator congelado
- perfiles de modelo congelados
- comandos reproducibles
- artefactos de salida estables
- documentación de exclusiones y supuestos

Si sólo se deja “el código ejecutable”, pero todavía cambian:

- escenarios
- reglas
- criterios terminales
- métricas
- clasificación de oportunidades

entonces todavía no existe una versión final del experimento.

## Qué falta además del harness

Además de dejar el harness listo, siguen siendo obligatorias estas piezas:

### 1. Congelamiento metodológico

- declarar qué versión exacta del benchmark se considera final
- documentar qué cambios pertenecieron a calibración
- no seguir ajustando el benchmark con base en resultados finales

### 2. Escalamiento de réplicas

- mínimo defendible: `21 × 4 × 3 = 252` corridas
- objetivo recomendado: `21 × 4 × 5 = 420` corridas

### 3. Generalización mínima de modelo

- conservar `qwen2.5:7b`
- agregar al menos un segundo modelo
- idealmente:
  - uno abierto/local comparable
  - uno API/comercial pequeño

### 4. Análisis estadístico

- intervalos de confianza al `95%`
- bootstrap para métricas principales
- comparación entre modos
- tamaños de efecto

### 5. Formalización del oracle

- documentar cómo se decide:
  - oportunidad de violación
  - outcome aceptable
  - outcome prohibido
  - exclusiones de runtime F1

### 6. Ablations

- identificar qué parte del sistema produce la mejora observada

### 7. Amenazas a la validez

- interna
- externa
- constructo
- conclusión

## Fases del roadmap

## Fase 0. Cierre del piloto actual

Objetivo:
- declarar el experimento actual como piloto de calibración

Entregables:
- resumen de resultados piloto
- lista de correcciones realizadas
- identificación de qué quedó ya estabilizado

Criterio de salida:
- queda explícito que los resultados actuales son valiosos, pero todavía no constituyen la versión congelada doctoral

## Fase 1. Freeze del benchmark

Objetivo:
- congelar el harness y el diseño experimental

Incluye:
- escenarios
- contratos
- evaluator
- oracle
- reglas de diagnóstico
- perfiles de modelo
- semántica terminal

Entregables:
- versión congelada documentada
- changelog de calibración
- checklist reproducible de ejecución

Criterio de salida:
- ninguna métrica o escenario cambia más antes de la corrida doctoral

## Fase 2. Infraestructura de ejecución

Objetivo:
- dejar el harness listo para corridas grandes, sin intervención manual

Incluye:
- comandos únicos por lote
- organización de resultados por modelo/modo/réplica
- reanudación de corridas
- validaciones previas
- reporte automático de resumen

Entregables:
- pipeline de ejecución reproducible
- checklist operacional
- estimación de tiempo/costo por lote

Criterio de salida:
- el equipo ya no está “desarrollando” el benchmark, sino ejecutándolo

## Fase 3. Réplicas del modelo base

Objetivo:
- medir estabilidad con el modelo actual

Plan:
- correr `21 × 4 × 3` como mínimo
- idealmente `21 × 4 × 5`

Entregables:
- corpus replicado del modelo base
- varianza por escenario y por modo
- resumen agregado con intervalos

Criterio de salida:
- ya no hay sólo medias puntuales, sino distribuciones

## Fase 4. Segundo modelo

Objetivo:
- reducir dependencia de un solo backend

Plan recomendado:
- mantener `qwen2.5:7b`
- agregar `llama3.1:8b` o equivalente
- si alcanza el presupuesto, agregar un modelo API pequeño

Entregables:
- mismos escenarios
- mismos contratos
- mismas métricas
- comparación entre modelos

Criterio de salida:
- el hallazgo central deja de depender exclusivamente de un solo modelo

## Fase 5. Estadística inferencial

Objetivo:
- transformar promedios descriptivos en evidencia comparativa formal

Incluye:
- intervalos de confianza
- bootstrap
- comparaciones entre modos
- tamaños de efecto

Preguntas a responder:
- ¿`guarded` supera a `strict` de forma estable?
- ¿`guarded` realmente conserva más utilidad?
- ¿la detección en `guarded` es comparable o superior a la de otros modos?

Entregables:
- sección estadística de resultados
- tablas finales
- interpretación por hipótesis `H1–H4`

## Fase 6. Ablations

Objetivo:
- aislar qué mecanismos producen la mejora

Ablations mínimas recomendadas:
- sin recovery feedback
- sin terminal success
- sin tool filtering o con exposición más amplia controlada

Entregables:
- comparación de componentes
- explicación causal más fuerte del resultado `guarded > strict`

## Fase 7. Held-out o corrida final post-freeze

Objetivo:
- blindar el experimento contra la crítica de sobreajuste por calibración

Opciones:
- un pequeño conjunto held-out
- o una corrida final completa hecha sólo después del freeze

Entregables:
- evidencia final no usada para calibrar el benchmark

## Fase 8. Redacción doctoral

Objetivo:
- convertir el paquete experimental en capítulo defendible

Incluye:
- metodología congelada
- amenazas a la validez
- oracle como instrumento
- resultados por hipótesis
- resultados por familia de escenario
- overhead

## Prioridad realista

Si el tiempo es limitado, la secuencia más eficiente es:

1. freeze del benchmark
2. harness de ejecución estable
3. `21 × 4 × 5` con el modelo actual
4. segundo modelo
5. estadística inferencial
6. ablations mínimas
7. redacción final

## Criterio de tesis defendible

El experimento será doctoralmente defendible cuando pueda afirmarse algo así:

> Bajo una versión congelada del benchmark, replicada múltiples veces y evaluada con análisis estadístico, la gobernanza contractual reduce efectos inseguros y el modo `guarded` ofrece una mejor relación entre seguridad y utilidad que `strict`, con costos observables pero controlables.

Ése es el umbral real. Todo lo demás debe organizarse para llegar a esa frase con evidencia suficiente.
