# C07 — Capítulo 7: Análisis parcial de resultados → Conclusiones (p. 99–102)

> **Diagnóstico:** son las conclusiones de TT1 (mayo). Dicen que el mejor
> modelo es XGBoost, que la diferencia se explica por la asimetría de
> variables (que ya se corrigió), que la aplicación "está en desarrollo" y
> proponen como trabajo futuro cuatro cosas que ya se hicieron. Hay que
> **reescribir el capítulo completo**. Borrador: `textos/T07_conclusiones.md`.

## Resumen de puntos

| ID | Página | Sección | Tema | Prioridad |
|---|---|---|---|---|
| 7-01 | 99 | 7 | Título "Análisis parcial de resultados" | CRÍTICO |
| 7-02 | 99 | 7.1 | Hallazgo central con cifras de TT1 | CRÍTICO |
| 7-03 | 99 | 7.1 | "asimetría en el número de características" | CRÍTICO |
| 7-04 | 99–100 | 7.2, obj. 1 | "35 modelos por experimento", por activo | IMPORTANTE |
| 7-05 | 100 | 7.2, obj. 2 | Ejemplo de la CNN 1D en META | IMPORTANTE |
| 7-06 | 100 | 7.2, obj. 3 | "XGBoost mayor F1"; "depende del activo" | CRÍTICO |
| 7-07 | 100 | 7.2, obj. 4 | "En desarrollo"; descarga por solicitud | CRÍTICO |
| 7-08 | 100–101 | 7.3 | Asimetría como factor explicativo principal | CRÍTICO |
| 7-09 | 101 | 7.3 | XGBoost y CNN-LSTM "opuestos" | IMPORTANTE |
| 7-10 | 101 | 7.3 | Aporte del bloque recurrente | IMPORTANTE |
| 7-11 | 101 | 7.3 | TSLA 0.269 y NVDA 0.284 | IMPORTANTE |
| 7-12 | 101 | 7.3 | Coherencia con Nabipour et al. | CRÍTICO |
| 7-13 | 101–102 | 7.4 | Limitaciones resueltas y faltantes | CRÍTICO |
| 7-14 | 102 | 7.5 | El trabajo futuro ya se hizo | CRÍTICO |
| 7-15 | — | 7 | Faltan: título vs resultado, paper, respuesta a la pregunta | IMPORTANTE |

---

### 7-01 · p. 99 · Título · CRÍTICO
"7. Análisis parcial de resultados" → **"7. Conclusiones"**. La introducción
(p. 8) ya lo anuncia así (C-19).

### 7-02 · p. 99 · §7.1, párrafos 2–3 · CRÍTICO
**Dice:** "XGBoost obtiene el mayor F1-macro promedio con 0.369 y es el
único modelo con factor de ganancia mayor a 1 en cinco de los siete
activos… Regresión Logística… produce la razón de Sharpe promedio más alta
con 0.285… (como CNN 1D sobre META en el Experimento C con una razón de
Sharpe de 3.640)".
**Debe decir:** el hallazgo central con el protocolo final: la LR obtuvo el
mayor F1-macro en 2025 (0.404 en B; 0.406 y 0.401 en A y C) y fue
significativamente mejor que los otros cuatro en los tres experimentos, con
el mejor Sharpe (+0.89; +0.62 con costos de 10 pb). En seis años de prueba
año por año, LR y XGBoost empatan (~0.35–0.36) y ambos superan a las redes
con significancia. En 2026, con datos no usados en ninguna decisión, la LR
siguió primera en clasificación, sin diferencia significativa con XGBoost.
La señal existe, es débil (kappa 0.12 en 2025) y cambia entre años.
Eliminar el caso de la CNN 1D en META (6-17).

### 7-03 · p. 99 · §7.1, último párrafo · CRÍTICO
**Dice:** "Este resultado no debe interpretarse como evidencia de que el
aprendizaje profundo es inferior… El diseño experimental introduce una
asimetría en el número de características… que limita la comparabilidad
directa".
**Debe decir:** "Este resultado no implica que el aprendizaje profundo sea
inferior en general: indica que, con datos diarios públicos, una etiqueta de
un día y características que ya resumen la historia de varios días, las
redes no encuentran información adicional (su pérdida de validación no baja
del nivel del azar con ninguna configuración). La comparación se hizo en
igualdad de condiciones —mismas características, mismas filas, misma
búsqueda de hiperparámetros y mismas métricas—, por lo que la diferencia no
se explica por el diseño experimental". La asimetría de TT1 se menciona solo
como la limitación que motivó la Etapa 3.

### 7-04 · p. 99–100 · §7.2, objetivo 1 · IMPORTANTE
**Dice:** "mediante ocho scripts de Python… Cada modelo se entrenó de forma
independiente por activo… produciendo un total de 35 modelos por experimento
en la estrategia principal".
**Debe decir:** "Se implementaron los cinco modelos (scikit-learn, XGBoost y
PyTorch con GPU) en un pipeline por etapas; cada modelo se entrenó como
modelo global (siete acciones) y por acción, en tres experimentos: 120
corridas por etapa, más la prueba año por año (seis años) y la prueba ciega
2026. Los hiperparámetros de los cinco se buscaron con Optuna". Cumplido.

### 7-05 · p. 100 · §7.2, objetivo 2 · IMPORTANTE
- Agregar las métricas nuevas (kappa, AUC, exactitud balanceada, log-loss),
  los costos, los intervalos de confianza y las validaciones en el tiempo.
- **Quitar** el ejemplo de la CNN 1D en META (F1 0.334 → Sharpe 3.640): es
  un caso aislado elegido entre 105. Si se quiere ilustrar que clasificación
  y dinero divergen, usar un caso del protocolo final: en 2025 XGBoost y la
  CNN 1D tienen el mismo F1 (0.359) y Sharpe muy distintos (+0.46 contra
  −0.46); o la prueba ciega 2026, donde la CNN 1D tiene el F1 más bajo y el
  mejor Sharpe.

### 7-06 · p. 100 · §7.2, objetivo 3 · CRÍTICO
**Dice:** "XGBoost es el modelo con mayor F1-macro promedio y mayor
estabilidad… Entre los modelos de aprendizaje profundo, CNN-LSTM supera
consistentemente a LSTM y CNN 1D… No existe un único modelo óptimo para
todos los activos… la recomendación de uso debe considerar el activo
específico".
**Debe decir:** "Cumplido. En la prueba principal la LR es la mejor en las
ocho métricas y supera con significancia a los otros cuatro; en seis años
empata con XGBoost y ambos superan a las redes; entre las tres redes no hay
diferencias significativas. Con el criterio declarado (sección 4.x) se
eligió la LR. Un solo modelo global es mejor o igual que un modelo por
acción en los cinco modelos, por lo que la plataforma usa un modelo para las
siete acciones".
"CNN-LSTM supera consistentemente…" es falso incluso con cifras de TT1
(C-24).

### 7-07 · p. 100 · §7.2, objetivo 4 · CRÍTICO
**Dice:** "Este objetivo se encuentra en desarrollo… Al recibir una
solicitud, el servidor descarga los datos más recientes del activo
consultado… y devuelve la señal del día correspondiente al mejor modelo
identificado para ese activo en el Experimento B. La aplicación web… se
encuentra en fase de desarrollo de interfaz…".
**Debe decir:** "Cumplido. La plataforma está desplegada en Render: cada día
hábil a las 16:30 de Nueva York descarga los datos, calcula las 76
características, genera la recomendación de la LR para las siete acciones,
evalúa las recomendaciones anteriores contra lo que ocurrió y las publica en
una aplicación con siete pantallas, que incluye el modelo elegido y la
comparación de los cinco". C-31, C-32.

### 7-08 · p. 100–101 · §7.3, "La asimetría en características como factor explicativo principal" · CRÍTICO
**Dice:** "…sería necesario un experimento donde todos los modelos reciban el
mismo conjunto de características…".
**Acción:** ese experimento **se hizo** (Etapa 3, publicado en MICAI) y los
clásicos siguieron arriba. Reemplazar el apartado por "Por qué gana un modelo
lineal bien regularizado": poca señal (domina la varianza), características
que ya son transformaciones no lineales de la historia, pocos datos para
modelos de 10⁵ parámetros, pérdida de validación de las redes en ln 3, y la
literatura que dice lo mismo (Grinsztajn et al. 2022; Patel et al. 2015) y
cuándo se invierte (Gu, Kelly y Xiu 2020). Texto en `textos/T07` §3.

### 7-09 · p. 101 · §7.3, "comportamiento opuesto de XGBoost y CNN-LSTM" · IMPORTANTE
Es un patrón de TT1 (por acción, lookback elegido con la prueba). Con el
protocolo final no se sostiene (XGBoost: 0.359 / 0.359 / 0.362). Eliminar o
presentarlo como observación de la Etapa 1 que no se confirmó.

### 7-10 · p. 101 · §7.3, "aporte del componente recurrente" · IMPORTANTE
"La diferencia… crece de 0.012 puntos en el Experimento A a 0.025 en el C" →
en A la diferencia era a favor de la CNN 1D (C-24) y en la Etapa 4 los
intervalos de ambas se traslapan. Eliminar o corregir.

### 7-11 · p. 101 · §7.3, "La dificultad de TSLA y NVDA" · IMPORTANTE
"F1-macro promedio más bajo del universo con 0.269 y 0.284" no coincide con
las tablas (≈ 0.300 y 0.299; C-27). Si se quiere hablar de variación entre
acciones, usar el hallazgo del paper: la acción explica el 15.5 % de la
variación del Sharpe y el modelo el 3.4 %.

### 7-12 · p. 101 · §7.3, "Coherencia con la literatura" · CRÍTICO
**Dice:** "Los resultados son coherentes con Nabipour et al. (2020), quienes
muestran que los modelos de aprendizaje profundo superan a los clásicos
cuando reciben las mismas características de entrada, condición que en este
trabajo no se cumple por diseño".
**Es al revés:** en este trabajo los cinco reciben las mismas
características y las redes **no** superan a los clásicos. Decir: "A
diferencia de Nabipour et al. (2020), que en el mercado de Teherán encuentran
ventaja de RNN y LSTM en clasificación binaria, aquí, con las mismas
características para todos, los modelos clásicos igualan o superan a las
redes; el resultado coincide con Patel et al. (2015) y Grinsztajn et al.
(2022), y las diferencias con trabajos donde las redes ganan se explican por
el tamaño de la muestra y el tipo de entrada".

### 7-13 · p. 101–102 · §7.4 Limitaciones · CRÍTICO
**Quitar o actualizar** (ya resueltas):
- "La simulación económica no incorpora costos de transacción" → se
  calcularon (5 y 10 pb); queda como limitación la ejecución al cierre, el
  tamaño fijo y la venta en corto sin costo de préstamo.
- "El diseño experimental introduce una asimetría en el número de
  características" → resuelta desde la Etapa 3.
- "los resultados corresponden al periodo de prueba 2025" → complementado
  con la prueba año por año (2020–2025) y 2026.
**Conservar:** solo indicadores técnicos (sin noticias ni macroeconomía),
frecuencia diaria.
**Agregar:**
- La señal es débil y cambia entre años (kappa 0.12 en 2025; ≈ 0.04 en 2026;
  la permutación no detecta señal en 2024).
- Siete acciones de un solo sector, que sobrevivieron (sesgo de
  supervivencia).
- El Sharpe de un año tiene un error estándar ≈ 1.
- Búsqueda simétrica en procedimiento, no en dimensión.
- La ventana de las redes termina en *t − 1* (efecto medido ≈ 0.007).
- Las 15 interacciones de producción se adoptaron viendo 2025 (luego
  validadas como equivalentes).
- La plataforma en el plan gratuito: se duerme sin tráfico y la
  actualización solo corre si el servicio está despierto.
Lista completa: `ESTUDIO_TT/A_modelo/A7` §8.

### 7-14 · p. 102 · §7.5 Trabajo futuro · CRÍTICO
Las cuatro líneas propuestas **ya se hicieron** (C-33):

| Trabajo futuro de TT1 | Estado |
|---|---|
| Ajuste del dataset (ventanas de entrenamiento, limpieza) | Hecho: Experimentos A/B/C, prueba año por año, Etapas 2, 4 y 5 |
| Integración completa de los módulos | Hecho |
| Despliegue en producción | Hecho (Render) |
| Búsqueda sistemática de hiperparámetros | Hecho (Optuna, Etapa 4) |

**Nuevo trabajo futuro** (en orden de valor esperado; `A7` §9 y
`03_MAPA_DE_EXPERIMENTOS.md` §5): horizonte de varios días como un problema
distinto; ampliar el universo de acciones (incluyendo empresas que
desaparecieron) para que las redes tengan datos suficientes; datos gratuitos
adicionales (macroeconomía de FRED, sentimiento de noticias); tamaño de
posición según volatilidad y optimización con costos; corregir la ventana de
las redes a `[t − W + 1, t]` y repetir la Etapa 4; otras arquitecturas (GRU,
Transformer) solo con más datos.

### 7-15 · Faltantes · IMPORTANTE
Agregar en las conclusiones:
1. **Respuesta explícita a la pregunta de investigación** y a H₀/H₁: no se
   rechaza H₀; ninguna red supera de manera consistente a los modelos de
   referencia.
2. **Por qué el sistema despliega una LR aunque el título hable de
   aprendizaje profundo** (0-04): el TT diseñó, implementó y evaluó tres
   arquitecturas profundas; la evidencia indicó desplegar el modelo más
   simple.
3. **El artículo publicado** como producto (MICAI 2026) y qué parte del TT
   cubre.
4. **Qué aporta el TT más allá del paper**: costos, seis años, 2026, el
   análisis del exceso de mantener y la plataforma.
