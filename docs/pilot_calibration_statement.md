# Declaración de fase piloto y calibración

## Propósito

Este documento establece formalmente que las corridas actualmente ejecutadas del benchmark de enforcement corresponden a una **fase piloto/calibración** y no deben presentarse como la evaluación experimental final de nivel doctoral.

## Declaración principal

La versión inicial del benchmark se utilizó como fase piloto para validar infraestructura, corregir métricas, calibrar escenarios y ajustar criterios terminales. Una vez completada esta fase, se congeló una versión final del benchmark para la evaluación experimental principal.

## Justificación metodológica

No conviene presentar las `84` corridas actuales como experimento final, porque durante esa etapa todavía se realizaron adecuaciones que cambiaron materialmente el instrumento experimental. Entre las más importantes se encuentran:

- correcciones al evaluador
- refinamiento del oracle
- ajustes a escenarios adversariales
- incorporación de feedback estructurado para recuperación
- incorporación de lógica de `terminal success`

Estas modificaciones fueron necesarias para:

- validar que la infraestructura funcionara end-to-end
- corregir definiciones métricas que inicialmente producían resultados inválidos o poco interpretables
- alinear mejor la oportunidad de violación con los escenarios adversariales
- mejorar la recuperación del agente después de un bloqueo
- estabilizar los criterios de finalización segura

## Interpretación correcta de las 84 corridas actuales

Las `84` corridas ya ejecutadas tienen valor experimental, pero su papel correcto es el de evidencia de:

- factibilidad de implementación
- funcionamiento del harness
- señal inicial del efecto del Governor
- calibración de métricas y escenarios
- identificación de problemas metodológicos y técnicos

Por tanto, esas corridas deben citarse como:

- **piloto experimental**
- **fase de calibración**
- **evidencia preliminar**

Y no como:

- evaluación doctoral definitiva
- experimento final congelado
- evidencia confirmatoria final

## Cómo debe redactarse en metodología

Se recomienda usar una formulación equivalente a la siguiente:

> La versión inicial del benchmark se utilizó como fase piloto para validar infraestructura, corregir métricas, calibrar escenarios y ajustar criterios terminales. Una vez completada esta fase, se congeló una versión final del benchmark para la evaluación experimental principal.

También puede ampliarse así:

> En una primera etapa se ejecutó una fase piloto del benchmark con el objetivo de validar la infraestructura de ejecución, identificar inconsistencias en el evaluador, refinar el oracle, ajustar la presión adversarial de ciertos escenarios y estabilizar los criterios terminales de éxito y fallo. Debido a estas adecuaciones, los resultados de dicha etapa se consideran evidencia preliminar de calibración y no la evaluación final del experimento. Posteriormente, se definió una versión congelada del benchmark, la cual se utilizará como base de la evaluación experimental principal.

## Implicación para el roadmap

Esta declaración habilita la siguiente secuencia metodológica:

1. cierre formal de la fase piloto
2. congelamiento del benchmark
3. ejecución replicada de la versión final
4. análisis estadístico e inferencial

## Conclusión

El valor de la fase piloto no disminuye por no ser la versión final del experimento. Al contrario, su función es precisamente fortalecer la validez del estudio al permitir detectar errores, calibrar el instrumento y llegar a una versión final metodológicamente más estable. En este sentido, las `84` corridas actuales deben entenderse como el cierre de la etapa de calibración y como la base a partir de la cual se construirá la evaluación doctoral definitiva.
