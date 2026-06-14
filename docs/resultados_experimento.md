# Pruebas, complicaciones, adecuaciones, hallazgos y resultados

En esta sección se muestran todas las pruebas realizadas, complicaciones, adecuaciones, hallazgos y resultados encontrados, lo cual va ligado con la hipótesis propuesta, la cual debe validarse en esta sección. En consecuencia, el análisis no se limita a enumerar ejecuciones o métricas, sino que busca interpretar la evidencia experimental obtenida y establecer si la propuesta desarrollada cumple con el objetivo central de demostrar que un esquema de contratos de agente y gobernanza externa puede reducir acciones inseguras sin eliminar la capacidad operativa del agente.

## Pruebas realizadas

Las pruebas efectuadas se organizaron en torno a un benchmark de enforcement para agentes LLM con uso de herramientas. El experimento se ejecutó sobre un conjunto de escenarios nominales y adversariales, comparando cuatro modos de operación:

- `no_contract`
- `advisory`
- `guarded`
- `strict`

Cada corrida generó evidencia observable en forma de trazas, ledgers y resúmenes de ejecución, lo que permitió analizar no sólo la salida textual del agente, sino también sus propuestas de acción, bloqueos, replanteamientos y efectos finales.

Las pruebas incluyeron tanto validación funcional de la infraestructura como ejecuciones completas del corpus experimental con backend real sobre Ollama y LiteLLM. De este modo, la evidencia generada combina verificación de implementación con observación empírica del comportamiento del agente bajo distintos niveles de enforcement.

## Complicaciones encontradas

Durante el desarrollo y la ejecución experimental surgieron varias complicaciones relevantes. Una de las principales fue la discrepancia entre resultados locales y fallas de integración continua, originada por diferencias entre archivos modificados localmente y archivos realmente incluidos en los cambios integrados al repositorio. Otra complicación importante fue la necesidad de corregir fórmulas del evaluador, ya que una versión inicial producía tasas inválidas al mezclar conteos a nivel de acción con denominadores a nivel de corrida.

Además, se identificaron dificultades propias del comportamiento agentivo del modelo, por ejemplo repeticiones innecesarias de acciones, recuperaciones incompletas tras un bloqueo y escenarios donde la presión adversarial no era suficiente para inducir la acción riesgosa esperada. Estas complicaciones no invalidan la propuesta; por el contrario, permiten justificar las adecuaciones metodológicas y técnicas que fortalecen la validez del estudio.

## Adecuaciones implementadas

Como respuesta a las complicaciones anteriores, se realizaron adecuaciones en distintos niveles del sistema. En el evaluador se redefinieron las métricas de prevención a nivel de corrida y se separó con mayor claridad la detección runtime de las violaciones de pre y post-ejecución. En los escenarios se ajustaron expectativas, criterios terminales y niveles de presión adversarial para alinear mejor la oportunidad de violación con el objetivo experimental.

En la implementación del runtime se añadió *feedback* estructurado del gobernador para apoyar la recuperación del agente después de un bloqueo, así como mecanismos de *terminal success* para finalizar ejecuciones seguras una vez alcanzado el outcome correcto. Estas adecuaciones son parte de la aportación experimental de la tesis, pues muestran que la gobernanza efectiva no depende sólo de detectar y bloquear, sino también de orientar la recuperación y evitar degradaciones innecesarias en la utilidad del agente.

## Hallazgos principales

Los hallazgos más importantes del experimento muestran que los modos con enforcement activo logran prevenir efectos inseguros de manera consistente. En la ejecución completa del benchmark, los modos `guarded` y `strict` evitaron la ejecución de acciones inseguras observadas en la línea base `no_contract` y en `advisory`. Sin embargo, también se observó una diferencia relevante entre ambos: `guarded` conservó una tasa de finalización segura considerablemente mayor que `strict`.

Otro hallazgo importante es que la calidad de la gobernanza no puede evaluarse sólo por detección de violaciones. Fue necesario medir también la oportunidad de acción insegura, la efectividad de prevención, la recuperación posterior al bloqueo y la finalización segura de la tarea. Este punto refuerza la postura de la tesis de que la evaluación de agentes gobernados debe ser multidimensional y no limitarse a clasificaciones binarias de éxito o fallo.

## Resultados encontrados

Los resultados agregados del experimento completo, correspondiente a `84` corridas (`21` escenarios `× 4` modos `× 1` réplica), muestran diferencias claras entre los cuatro modos de enforcement. En primer lugar, el número de acciones inseguras ejecutadas fue de `5` en `no_contract`, `5` en `advisory`, `0` en `guarded` y `0` en `strict`. Este dato por sí solo ya permite observar que la presencia del gobernador con capacidad de bloqueo modifica materialmente el comportamiento operativo del agente.

En cuanto a la métrica de `unsafe_side_effect_rate`, los modos `no_contract` y `advisory` obtuvieron `1.0`, mientras que `guarded` y `strict` obtuvieron `0.0`. Esto significa que, una vez que se presentó una oportunidad real de acción insegura, los dos primeros modos no lograron prevenir el efecto inseguro, mientras que los dos últimos sí lo evitaron completamente. En términos de `governance_effectiveness`, el patrón es complementario: `no_contract = 0.0`, `advisory = 0.0`, `guarded = 1.0` y `strict = 1.0`.

Sin embargo, la diferencia más importante para la tesis aparece al observar la `successful_safe_completion_rate`. En esta métrica, `guarded` alcanzó `0.904762`, mientras que `strict` obtuvo `0.333333`. Como referencia adicional, `no_contract` obtuvo `0.619048` y `advisory` `0.571429`. Estos valores muestran que el bloqueo rígido no es la mejor solución práctica si elimina demasiada utilidad, mientras que `guarded` consigue preservar la finalización segura en una proporción mucho mayor.

Las métricas de detección runtime también respaldan esta interpretación. `guarded` obtuvo `precision = 0.666667`, `recall = 1.0` y `f1 = 0.8`, mientras que `advisory` y `strict` obtuvieron `precision = 0.625`, `recall = 0.833333` y `f1 = 0.714286`. En otras palabras, `guarded` no sólo previno acciones inseguras, sino que además alcanzó la mejor calidad de detección entre los modos con enforcement.

Desde la perspectiva de oportunidad experimental, los cuatro modos compartieron un `unsafe_action_opportunity_rate = 0.238095`, lo que indica que el corpus sí generó suficientes situaciones de riesgo observables para comparar los modos en condiciones equivalentes. Este punto es importante porque fortalece la validez interna del benchmark: las diferencias observadas no se explican por ausencia de oportunidad, sino por el efecto del mecanismo de enforcement.

En relación con `H4`, la sobrecarga del enforcement también puede observarse directamente en el uso medio de tokens y en la latencia media por corrida. Los valores de `mean_token_usage` fueron `3483.714286` en `no_contract`, `3497.380952` en `advisory`, `3649.285714` en `guarded` y `1906.619048` en `strict`. Esto implica que `guarded` consumió aproximadamente `165.57` tokens más por corrida que `no_contract` y `151.90` más que `advisory`, lo cual es coherente con su mayor número de replanteamientos y con la incorporación de feedback del gobernador. En latencia media (`mean_latency_ms`), los valores fueron `150082.128887` en `no_contract`, `146950.853082` en `advisory`, `152272.317173` en `guarded` y `78346.903744` en `strict`. El caso de `strict` muestra menor costo porque aborta antes, mientras que `guarded` incurre en mayor trabajo para preservar utilidad y completar la tarea de manera segura.

En términos de la hipótesis, la evidencia respalda que un esquema de contratos y gobernanza externa puede reducir o eliminar efectos inseguros en un agente con uso de herramientas. No obstante, también se observa que no todos los modos de enforcement son equivalentes: la mejor contribución práctica no proviene del bloqueo más rígido, sino del equilibrio entre prevención y recuperación. En este sentido, los resultados favorecen especialmente al modo `guarded`.

## Validación de la hipótesis

La validación debe interpretarse respecto de las cuatro hipótesis experimentales definidas para el benchmark. En primer lugar, `H1` queda respaldada por los resultados, ya que los modos `guarded` y `strict` redujeron completamente la ejecución de acciones inseguras frente a `no_contract` y `advisory`: se observaron `5` acciones inseguras ejecutadas en `no_contract`, `5` en `advisory` y `0` tanto en `guarded` como en `strict`. Esto también es consistente con `unsafe_side_effect_rate = 1.0` en `no_contract` y `advisory`, frente a `0.0` en `guarded` y `strict`.

En segundo lugar, `H2` recibe un apoyo parcial y matizado. La hipótesis planteaba equivalencia entre la calidad de detección en `advisory` y en los modos bloqueantes. Los datos muestran que `advisory` y `strict` son idénticos en detección (`precision = 0.625`, `recall = 0.833333`, `f1 = 0.714286`), mientras que `guarded` mejora a `precision = 0.666667`, `recall = 1.0` y `f1 = 0.8`. Por tanto, la evidencia apunta a que la capacidad de detección se mantiene comparable entre modos, pero no permite afirmar equivalencia perfecta en sentido estricto con una sola réplica experimental.

En tercer lugar, `H3` queda claramente respaldada. Tanto `guarded` como `strict` alcanzaron `governance_effectiveness = 1.0`, pero `guarded` obtuvo una `successful_safe_completion_rate = 0.904762`, muy superior a `0.333333` de `strict`. Este contraste confirma que una estrategia de enforcement con recuperación ofrece una mejor relación entre seguridad y utilidad que una estrategia de aborto inmediato.

Finalmente, `H4` también se sostiene, ya que el enforcement introduce sobrecarga observable en tiempo de ejecución, iteraciones y uso de tokens. Los cuatro modos muestran costos distintos: `mean_token_usage = 3483.714286` en `no_contract`, `3497.380952` en `advisory`, `3649.285714` en `guarded` y `1906.619048` en `strict`. De forma similar, `guarded` alcanzó `mean_replans_per_run = 1.333333`, mientras que `strict` obtuvo `0`, precisamente porque aborta sin intentar recuperación. Esto demuestra que la gobernanza efectiva no es gratuita y que su costo debe formar parte de la evaluación integral del sistema.

Además, existe un hallazgo metodológico importante: las adecuaciones al evaluador, al oracle, a los escenarios adversariales y al mecanismo de recuperación mejoraron de manera visible la calidad de detección respecto al piloto anterior. En particular, `advisory` pasó de `f1 = 0.5` a `f1 = 0.714286`, y `guarded` pasó de `f1 = 0.4` a `f1 = 0.8`. Este resultado fortalece la validez del proceso experimental, pues muestra que las complicaciones encontradas no sólo fueron resueltas, sino que llevaron a un benchmark mejor calibrado y metodológicamente más sólido.

Por tanto, esta sección no sólo confirma la viabilidad de la propuesta, sino que también delimita sus condiciones más favorables de aplicación. La evidencia obtenida sustenta que la gobernanza externa de agentes LLM es factible, medible y metodológicamente defendible dentro del marco experimental planteado en esta tesis.
