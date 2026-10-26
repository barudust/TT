# 00 — Resumen ejecutivo de la revisión

> **En una frase:** el reporte actual es el documento de TT1 (mayo) con
> parches. Los capítulos 2 a 6.5 describen el método y los resultados de la
> **Etapa 1**, y el trabajo que da el resultado final (Etapas 3 a 6: mismas
> variables para todos, protocolo estricto, Optuna, intervalos de confianza,
> prueba año por año, 2026, plataforma desplegada) aparece comprimido en
> cuatro páginas de "experimentación adicional" (§6.6). Por eso el documento
> concluye que **gana XGBoost**, mientras que el sistema desplegado y el
> artículo publicado usan la **Regresión Logística**. Hay que invertir la
> estructura: el protocolo final al centro y TT1 como antecedente.

---

## Los 12 problemas grandes

| # | Problema | Dónde | Qué hacer | Detalle |
|---|---|---|---|---|
| 1 | **La conclusión contradice al sistema y al paper.** El cap. 7 dice que el mejor modelo es XGBoost (0.369); la plataforma usa la LR y el paper reporta LR 0.404 | §7.1, §7.2, Resumen | Reescribir resultados y conclusiones con la Etapa 4 como resultado principal | `correcciones/C06`, `C07`; `textos/T06`, `T07` |
| 2 | **El método descrito es el de TT1.** Selección de variables por modelo, Exp A con prueba 2024–2025, un modelo por acción, arquitecturas fijas, métricas sobre 90 días | Cap. 4 casi completo | Describir el protocolo final (Etapas 3–4) y dejar TT1 como antecedente | `correcciones/C04`; `textos/T04` |
| 3 | **El número de variables cambia en cada página:** 54 (texto), 46 (figuras 3–4 y Tabla 12), 61 (Tabla 4 y código). Producción usa 76 | Resumen, §4.2, §4.3, §5.2, Fig. 3–4 | 61 variables base en 9 familias; 76 en producción (61 + 15 interacciones) | `02_CONTRADICCIONES` C-01 |
| 4 | **Selección de variables por modelo (§4.4)** contradice "mismos datos para todos" (§3.6) y es la causa de la comparación injusta que la sinodal señaló | §4.4, Tablas 5–7, §6.3.1, §7.3 | Sustituir por "mismas 61 variables para los cinco" + la evidencia de que filtrar empeora (11 de 15) + el análisis de multicolinealidad | `textos/T03` |
| 5 | **El Experimento A está mal y se contradice:** la Tabla 3/8 dice prueba 2024–2025, el texto dice que los tres comparten 2025 | §4.2, §4.5, §6.2.1 | A = 2014–2023 / 2024 / 2025 | `correcciones/C04` 4-09 |
| 6 | **Métricas no comparables entre modelos:** el lookback de las redes se eligió con la prueba y las redes se evaluaron sobre menos días (228 o 188 contra 248) | §6.2, §6.4 | Explicarlo como defecto de la Etapa 1/3 corregido en la Etapa 4: mismas 1 736 filas, todo elegido en 2024 | `textos/T03` (métricas justas) |
| 7 | **Dice que no hay pruebas de significancia**, cuando sí las hay (bootstrap por bloques, permutación, prueba año por año, prueba ciega 2026). La hipótesis omite la CNN 1D | §4 (intro), §2.1.3 | Reescribir pregunta, hipótesis y sección de validación estadística | `correcciones/C04` 4-01 a 4-04 |
| 8 | **Hiperparámetros y entrenamiento contradictorios:** "fijos" (§4.8.3) contra "rejilla" (§4.10.1); paro temprano por pérdida con paciencia 15 contra F1 con paciencia 10 | §4.8, §4.10, §6.1 | Describir Optuna (Etapa 4) para los cinco y el protocolo anidado dev/final | `tablas/T-05`, `T-06` |
| 9 | **La simulación económica se contradice:** §2.6.3 dice que VENDER es "liquidar o quedarse en efectivo"; §4.11 dice venta en corto. Hay dos fórmulas distintas del retorno acumulado. Dice que no hay costos | §2.6.3, §4.9.3, §4.11 | Una sola regla (+1/−1/0), una sola fórmula, costos de 10 pb | `correcciones/C02` 2-14, `C04` 4-30 |
| 10 | **El capítulo 5 describe el sistema que se diseñó en TT1, no el que existe:** PostgreSQL con 9 tablas, ETL incremental con cron, interfaz de 3 niveles, puertos locales y dos juegos de rutas distintos. Además dice que el modelo "está pendiente" y que la aplicación "está en desarrollo" | Cap. 5, §7.2 obj. 4, §7.5 | Reescribir con el sistema real: SQLite (4 tablas), actualización dentro de la API (APScheduler), 7 pantallas, Render, 24 pruebas | `correcciones/C05`; `textos/T05`; `diagramas/` |
| 11 | **No se declara cómo se eligió el modelo final** (observación de la sinodal: "¿por resultados o por desempeño?") | §4.9.4, §6, §7 | Declarar el criterio: clásicos > redes en todas las pruebas; LR y XGBoost empatan en 6 años; ante el empate, parsimonia, menor rotación y costos, interpretabilidad; confirmación en 2026 | `textos/T03` |
| 12 | **El paper no aparece**, faltan referencias que el texto usa y hay errores en la portada | Todo; Referencias; portada | Citar el paper, agregarlo como producto y anexo; completar referencias; corregir portada | `../PAPER_MICAI/05_INCLUSION_EN_EL_REPORTE.md`; `correcciones/C00`, `C08` |

---

## Riesgos de defensa que esta revisión cierra

1. **"El título dice aprendizaje profundo y eligieron una regresión."**
   El TT diseñó, implementó y optimizó tres redes (LSTM, CNN 1D, CNN-LSTM)
   y las comparó contra referencias clásicas, que es lo que piden el objetivo
   general y la pregunta de investigación. La respuesta a la pregunta fue que,
   con datos diarios públicos y señal de un día, las redes no superan a los
   clásicos; por eso el sistema despliega el mejor modelo según un criterio
   declarado. Esto debe decirse **explícitamente** en el resumen, la
   introducción y las conclusiones (borrador en `textos/T01` y `T07`).
2. **"La comparación no es justa."** Hoy es justa (mismas variables, mismas
   filas, misma búsqueda, mismas ocho métricas). El documento tiene que
   contarlo y mostrar la tabla de igualdad (`tablas/T-08`).
3. **"Escogieron la LR viendo la prueba."** Criterio declarado y prueba ciega
   2026 (`textos/T03`).
4. **"¿Por qué no quitaron variables colineales?"** Diagnóstico de VIF y
   experimento con filtro VIF ≤ 10 (`textos/T03`, `tablas/T-11`).
5. **"El documento dice PostgreSQL y el sistema usa SQLite."** Hay que
   contar el cambio y su justificación (`textos/T05`).

---

## Esfuerzo por capítulo

| Capítulo | Estado | Trabajo |
|---|---|---|
| Portada, resumen, índices | Errores de portada; resumen sin resultado y con 54 variables | Bajo: corregir y reescribir resumen/abstract (borrador listo) |
| 1. Introducción | Bien en general | Bajo: matizar motivación, agregar resultado y productos |
| 2. Marco teórico | Bien en general | Medio: 15 correcciones puntuales y 2 secciones nuevas (métricas adicionales y validación estadística) |
| 3. Estado del arte | Bien | Bajo: Tabla 1, orden de citas, frase de 3.6 |
| 4. Metodología | Describe TT1 | **Alto**: reescribir §4 intro, 4.4, 4.5, 4.7, 4.8, 4.9, 4.10, 4.11 |
| 5. Sistema | Describe el diseño de TT1 | **Alto**: reescribir casi todo; 6 figuras nuevas |
| 6. Resultados | Resultados de TT1 + resumen de lo demás | **Alto**: reestructurar por etapas; la Etapa 4 como resultado principal |
| 7. Conclusiones | Conclusiones de TT1 | **Alto**: reescribir |
| Referencias | Faltan ~15 | Medio |

---

## Lo que está bien y conviene conservar

- La etiqueta por percentil rodante 30/70 y su justificación (§2.2).
- La Tabla 4 de variables (es correcta: tiene 61 filas).
- El estado del arte (cap. 3) y la brecha de investigación.
- La descripción de por qué no usar accuracy y por qué F1-macro.
- Los supuestos y limitaciones del backtest (§4.11.1 y §4.11.4), con el
  añadido de los costos.
- El contenido de §6.6 (es correcto y está bien resumido), pero debe pasar a
  ser el centro del capítulo 6, con el nombre de cada etapa.
- La experiencia de pruebas e integración de §5.3.3 y §5.5.3–5.5.5 (bug de
  conexiones, CORS, fechas en UTC): es valiosa, solo hay que pasarla a tono
  impersonal y actualizar la tecnología.
