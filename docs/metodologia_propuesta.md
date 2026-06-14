# Metodología, diseño e implementación propuesta

## Problema que resolverá

El problema central de esta tesis es la falta de mecanismos prácticos y evaluables para gobernar agentes basados en modelos de lenguaje grandes cuando interactúan con herramientas externas y producen efectos en tiempo de ejecución. En la práctica, un agente no sólo genera texto: decide qué herramienta invocar, en qué orden, con qué argumentos y cuándo detenerse. Esa autonomía introduce riesgos de seguridad, cumplimiento y trazabilidad, por ejemplo aprobaciones no autorizadas, creación de tickets sin evidencia suficiente, escritura de memoria fuera de alcance o envío de notificaciones sensibles sin aprobación previa.

El problema no se resuelve únicamente con alineación del modelo, filtrado de respuestas o evaluación estática de prompts. Se requiere un mecanismo externo capaz de inspeccionar propuestas de acción, validar precondiciones y postcondiciones, bloquear acciones inseguras y permitir recuperación cuando sea posible. Por ello, la tesis propone un marco experimental para responder, con evidencia reproducible, si los contratos de agente y un gobernador de ejecución pueden reducir efectos inseguros sin destruir la utilidad operativa del agente.

## Descripción general de la solución propuesta

La solución propuesta es un **benchmark de gobernanza en tiempo de ejecución para agentes con uso de herramientas**, basado en tres elementos: un agente LLM, un conjunto controlado de herramientas deterministas y un **Agent Governor** que aplica contratos formales durante la ejecución. El agente toma decisiones reales de llamada de herramientas; el gobernador observa cada propuesta y la evalúa contra reglas declarativas; y el benchmark mide, en distintos modos de enforcement, qué tan bien se previenen efectos inseguros y qué tanto se preserva la finalización segura de tareas.

La propuesta se implementa en cuatro modos experimentales:

- `no_contract`
- `advisory`
- `guarded`
- `strict`

Interpretación:

- `no_contract` funciona como línea base sin intervención.
- `advisory` detecta y registra violaciones pero no bloquea.
- `guarded` bloquea acciones inseguras y permite replanteamiento.
- `strict` bloquea y aborta.

Esta estructura permite observar no sólo si se detectan violaciones, sino también el compromiso entre seguridad y utilidad. La arquitectura general del flujo puede resumirse en la figura `\ref{fig:figure}`: el agente propone una acción sobre una herramienta, el Governor evalúa esa propuesta contra el contrato activo, decide si la acción se permite, se bloquea o se aborta, y sólo después de esa decisión puede ocurrir el efecto sobre el estado o sobre la herramienta. A continuación, el runtime registra la traza, actualiza el ledger y entrega la evidencia al evaluador experimental.

## Descripción detallada por fases y módulos

### Fase 1: modelado del problema y definición contractual

La primera fase consiste en traducir riesgos operativos a restricciones observables de ejecución. En esta tesis, dichas restricciones se expresan como contratos de agente que contienen huellas de configuración, herramientas declaradas, reglas de pre-ejecución, reglas de tiempo de ejecución y reglas de post-ejecución. Esta fase integra el conocimiento del marco teórico sobre gobernanza, control de acceso, validación por políticas y auditoría de agentes, con el fin de convertir principios abstractos en reglas verificables.

El resultado de esta fase es un conjunto de contratos YAML que formalizan propiedades como autorización, evidencia requerida, alcance permitido de memoria, aprobación previa y consistencia del ledger de ejecución. Esta formalización constituye una aportación relevante porque traslada la discusión teórica sobre seguridad de agentes a objetos ejecutables y medibles.

### Fase 2: diseño del benchmark experimental

La segunda fase diseña el benchmark como un entorno controlado pero suficientemente expresivo para inducir decisiones riesgosas. Para ello se definen escenarios nominales y adversariales, un conjunto pequeño de herramientas deterministas y un perfil de modelo reproducible. Los escenarios no se evalúan contra una secuencia fija de pasos, sino contra *outcomes* aceptables y prohibidos. Esta decisión metodológica es importante porque evita sobreajustar la evaluación a una sola trayectoria y permite medir recuperación segura, rechazo seguro o cumplimiento seguro con distintas rutas de ejecución.

En esta fase también se determinan las expectativas runtime de cada escenario, las propiedades terminales y los casos que deben excluirse de la medición de F1 cuando no representan una oportunidad runtime válida. Con ello, el benchmark mantiene coherencia metodológica entre diseño del escenario, oportunidad de violación y definición de métricas.

### Fase 3: implementación del runtime gobernado

La tercera fase implementa el ciclo de ejecución del agente. Este runtime construye el contexto del modelo, expone sólo las herramientas permitidas por el escenario, recibe propuestas de acción, consulta al gobernador, ejecuta herramientas permitidas, almacena trazas, y sintetiza resultados finales. La implementación incluye adaptadores de modelo, una capa de herramientas simuladas, cálculo de propiedades finales, soporte para *replan*, y mecanismos de *feedback* del gobernador para orientar la recuperación después de un bloqueo.

Una aportación concreta de esta tesis en esta fase es el soporte de recuperación gobernada: no sólo se registra una violación, sino que el sistema puede impedir la acción insegura y empujar al agente hacia una secuencia válida. El caso de notificaciones sensibles tras aprobación muestra que la gobernanza eficaz requiere tanto bloqueo como señal de recuperación.

### Fase 4: instrumentación, evaluación y diagnóstico

La cuarta fase implementa la observabilidad experimental. Cada corrida produce `trace.jsonl`, `run_ledger.json` y `summary.json`. A partir de esos artefactos se calculan métricas de prevención, finalización segura, oportunidad de acción insegura, detección runtime y sobrecarga. Entre las métricas principales se encuentran:

- `unsafe_side_effect_rate`
- `governance_effectiveness`
- `successful_safe_completion_rate`
- `precision`
- `recall`
- `f1`

Adicionalmente, se incorpora una etapa de diagnóstico de F1 para distinguir errores de alineación del *oracle*, escenarios con baja presión adversarial, y casos estructuralmente excluidos de la medición runtime. Esta parte es importante porque evita conclusiones engañosas y fortalece la validez interna del experimento.

### Fase 5: ejecución comparativa y análisis

La quinta fase ejecuta la matriz experimental completa sobre todos los escenarios y modos. El objetivo es comparar la línea base sin contrato contra variantes con observación, bloqueo con recuperación y bloqueo con aborto. La hipótesis principal es que `guarded` ofrecerá una mejor relación entre seguridad y utilidad que `strict`, al prevenir efectos inseguros sin penalizar de forma excesiva la capacidad de completar tareas.

Esta fase culmina con el análisis comparativo de resultados, donde se contrasta cuándo la detección es suficiente, cuándo el bloqueo mejora la seguridad, y cuándo el aborto reduce de manera innecesaria la utilidad del agente. Así, el benchmark no sólo mide si una regla se activa, sino si la propuesta completa resulta operativamente conveniente.

## Aportación de la tesis y sustento teórico

La aportación principal de esta tesis es un marco reproducible para estudiar gobernanza externa de agentes LLM con uso de herramientas en tiempo de ejecución. Esta aportación se sustenta en tres niveles. Primero, retoma del marco teórico la necesidad de mecanismos verificables de control, trazabilidad y cumplimiento para sistemas autónomos. Segundo, toma del estado del arte la observación de que los agentes modernos ya no pueden evaluarse sólo como generadores de texto, sino como sistemas que ejecutan acciones y producen efectos. Tercero, propone una metodología experimental concreta para vincular ambos planos mediante contratos ejecutables, instrumentación reproducible y métricas orientadas a seguridad y utilidad.

En términos metodológicos, la tesis no se limita a proponer una arquitectura conceptual; también demuestra factibilidad de implementación mediante un *software artifact* ejecutable, escenarios controlados, integración con backends LLM reales y evidencia cuantitativa. Esto vuelve sustentable la propuesta, porque la misma puede ser replicada, auditada y extendida a otros modelos, proveedores o entornos con herramientas reales.

## Calidad argumentativa y congruencia con la investigación previa

La propuesta mantiene congruencia con la investigación desarrollada hasta ahora porque parte del supuesto, respaldado por el estado del arte, de que los modelos con capacidad agentiva requieren gobernanza exógena cuando interactúan con sistemas externos. También es congruente con el marco teórico sobre control basado en políticas, seguridad por restricciones y validación de transiciones de estado. En lugar de afirmar que la alineación interna del modelo es suficiente, la tesis argumenta que se necesita una capa complementaria de enforcement y evidencia.

Finalmente, la propuesta es factible porque ya cuenta con implementación operativa, corpus de escenarios, perfiles de modelo, contratos, diagnóstico y evaluación. En ese sentido, la tesis avanza de una discusión conceptual hacia una demostración experimental medible. La referencia a la figura `\ref{fig:figure}` permite integrar esta explicación textual con la representación visual de la arquitectura, reforzando la coherencia entre diseño, implementación y evaluación.
