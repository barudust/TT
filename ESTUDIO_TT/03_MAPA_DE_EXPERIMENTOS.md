# 03 — Mapa de experimentos (referencia única)

> **Para qué sirve.** Es la versión ordenada de todo lo que se corrió en el
> proyecto. Sustituye la numeración vieja (v0, v1 … v8, "Vía 7", "Vía 8",
> V0–V6), que creció sin plan y tenía huecos (no hubo v6) y nombres
> repetidos. Todo el estudio (`ESTUDIO_TT/`) y el documento final deben usar
> **los nombres de esta página**. Las carpetas del repositorio conservan los
> nombres viejos para no romper el código; la tabla de la sección 7 dice qué
> carpeta corresponde a cada cosa.
>
> **Marcas que se usan en toda la página:**
> **[PAPER §n]** = lo publica el artículo de MICAI en esa sección ·
> **[SOLO TT]** = no está en el artículo · **[NO CITAR]** = cifra que no
> debe presentarse como resultado · **[FUERA]** = sale del planteamiento
> del problema; se reporta como trabajo futuro.

---

## 1. Tres palabras que no hay que confundir

| Palabra | Qué es | Cuántos hay |
|---|---|---|
| **Etapa** | Una vuelta de trabajo que respondió una pregunta (antes "versión") | 6 |
| **Experimento** | Una forma de dividir los años en entrenamiento, validación y prueba | 3: **A, B y C** |
| **Validación adicional** | Una prueba extra de que el resultado no fue suerte de un año | 3: año por año (2020–2025), origen rodante (2019–2024) y 2026 |

Los experimentos A, B y C **no son etapas**: se repiten dentro de las
etapas 1 a 4 (cada etapa los vuelve a correr con su protocolo).

---

## 2. Los tres experimentos (A, B y C)

Desde la Etapa 3 los tres comparten validación y prueba; solo cambia cuánta
historia se usa para entrenar. Así se responde si más años de datos ayudan
o si el mercado viejo ya no sirve.

| Experimento | Entrenamiento | Validación | Prueba | Años | Papel |
|---|---|---|---|---:|---|
| A | 2014–2023 | 2024 | 2025 | 10 | Máxima historia |
| **B** | **2018–2023** | **2024** | **2025** | **6** | **Principal** (y base del modelo de la plataforma) |
| C | 2020–2023 | 2024 | 2025 | 4 | Solo mercado reciente |

- **Por qué B es el principal:** se declaró antes de ver resultados (en el
  diseño de TT1 ya era el "recomendado", periodo posterior al COVID): 6 años
  es un punto medio entre cantidad de datos y vigencia del mercado.
- **En las etapas 1 y 2** el Experimento A era distinto: entrenamiento
  2014–2021, validación 2022–2023 y **prueba 2024–2025**. Por eso esas
  cifras de A no se comparan con las de B y C. Se corrigió en la Etapa 3.
- Cada experimento se corre de dos formas: **un modelo global** para las 7
  acciones y **un modelo por acción**. Desde la Etapa 3 el principal es el
  global.

---

## 3. Las seis etapas de un vistazo

| Etapa | Nombre | Cuándo | Antes se llamaba | Pregunta | Respuesta corta | Paper |
|---|---|---|---|---|---|---|
| **1** | Línea base (TT1) | Hasta 18 may | v1 | ¿Funciona el sistema completo con 5 modelos? | Sí; XGBoost mejor en F1 y LR en Sharpe, pero la comparación no era pareja | No |
| **2** | Primeras mejoras | May–jun | optimización de mayo, "v0", v2, v3 | ¿Se puede mejorar cada modelo? | Sí, algo; pero con un protocolo que no sirve para reportar | Solo §6 |
| **3** | Comparación en igualdad | Junio | v4 | ¿Cuál gana si todos reciben lo mismo? | La LR (y XGBoost cerca) | **§3–§7** |
| **4** | Protocolo final | Agosto | v5 (pasos V0–V6) | ¿El resultado sobrevive a un protocolo estricto? | **Sí: la LR gana con significancia en A, B y C** | **§8** |
| **5** | Búsqueda de mejoras | Fin de agosto | v7 ("Vía 7") y v8 ("Vía 8") | ¿Algo más mejora sin cambiar el problema? | Casi nada; solo se adoptan 15 interacciones | No |
| **6** | Modelo de la plataforma y validación | Sep–oct | "análisis de septiembre" | ¿Cómo se comporta el modelo real y en datos nuevos? | Se ajusta el exceso de mantener; 2026 = 0.354 | No |

**La historia en una frase:** la Etapa 1 dio un primer resultado con una
comparación dispareja; la 2 exploró mejoras sin un protocolo limpio; la 3
igualó las condiciones; la 4 hizo el protocolo estricto que da **el resultado
principal del TT**; la 5 comprobó que no quedaba mejora razonable dentro del
planteamiento; y la 6 llevó el modelo a la plataforma y lo validó con datos
que nunca vio.

```
TT1 ──► Etapa 1 ──► Etapa 2 ──► Etapa 3 ──► Etapa 4 ──► Etapa 5 ──► Etapa 6
        línea base  primeras    igualdad    protocolo   búsqueda    plataforma
                    mejoras     [PAPER §7]  final       de mejoras  y validación
                                            [PAPER §8]
                                            RESULTADO
                                            PRINCIPAL
```

---

## 4. Cada etapa en detalle

### Etapa 1 — Línea base (reporte de TT1) · [SOLO TT]

- **Qué se hizo.** El sistema completo: dataset de 7 acciones con 61
  variables y etiqueta 30/70 a un día; selección de variables distinta
  para cada modelo; LR, XGBoost, LSTM, CNN 1D y CNN-LSTM; un modelo por
  acción como estrategia principal; los 3 experimentos (A con prueba
  2024–2025).
- **Resultado (por acción, promedio de A/B/C):** XGBoost 0.369, LR 0.351,
  CNN-LSTM 0.340, CNN 1D 0.331, LSTM 0.291. Sharpe más alto: LR (0.285).
- **Qué problema dejó abierto** (lo dice el propio TT1, §5.6): cada modelo
  recibía variables distintas, así que no se podía comparar en igualdad.
- **Qué se conserva hasta hoy:** el cálculo de las 61 variables y la
  etiqueta (`scripts_v1/01_build_raw_dataset.py`), copiado idéntico a la
  plataforma.

### Etapa 2 — Primeras mejoras (mayo–junio) · [SOLO TT, salvo §6]

- **Qué se hizo.** Se optimizó cada modelo por separado con los datos y
  particiones de TT1, y se probaron ideas para subir el resultado:
  1. Optimización por modelo (todas las 61 variables, distintos
     escaladores, LSTM bidireccional, etc.).
  2. **Preselección de variables contra usar las 61** → filtrar empeora en
     11 de 15 casos. **[PAPER §6]**
  3. 181 variables (z-scores, rezagos, interacciones) y calibración de
     umbrales → peor.
  4. 94 variables con contexto de mercado (tasas, dólar, oro, petróleo,
     sectores) → sin mejora.
  5. LightGBM, stacking, voto ponderado, mezcla LR+XGBoost, filtro por
     confianza → ninguno supera a la LR sola.
- **Por qué sus cifras no se reportan.** La mejor configuración se eligió
  mirando la prueba y el Experimento A tenía otra prueba. La cifra de esa
  época (**F1 0.417, Sharpe 1.25**) es **[NO CITAR]**.
- **Qué dejó.** La idea de dar las 61 variables a todos, la sospecha de un
  "techo" cerca de 0.40 y la necesidad de un protocolo limpio.

### Etapa 3 — Comparación en igualdad de condiciones (junio) · [PAPER §3–§7]

- **Qué cambió.** Las 61 variables para los cinco modelos; los tres
  experimentos con la misma prueba (2025); 120 corridas (5 modelos × 3
  experimentos × global y 7 acciones).
- **Resultado [PAPER §7]:** F1 global promedio de A/B/C: LR **0.399**,
  XGBoost 0.385, CNN-LSTM 0.377, LSTM 0.376, CNN 1D 0.359. Sharpe de la LR en
  B: +0.76.
- **Otros hallazgos publicados:** la acción explica 4.5 veces más el Sharpe
  que el modelo; efecto de los años de entrenamiento; distribución de
  señales.
- **Qué falló y se corrigió en la Etapa 4** (diagnóstico del 14 de agosto):
  las redes no tuvieron búsqueda de hiperparámetros comparable a la de
  XGBoost; su ventana (lookback) se eligió con la prueba (el paper lo
  declara); el paro temprano devolvía la época 1–2.

### Etapa 4 — Protocolo final (agosto) · [PAPER §8] · **resultado principal**

- **Por qué.** Los revisores del paper pidieron una búsqueda seria para las
  redes, y el diagnóstico encontró los problemas de arriba.
- **El protocolo.** Ninguna decisión usa la prueba: las configuraciones se
  eligen en 2024 (modo *dev*: entrenamiento 2018–2022, época en 2023) y la
  prueba 2025 se evalúa una sola vez (modo *final*). Mismo número de filas
  para los cinco modelos.
- **Pasos** (antes "V0–V6"):

| Paso | Qué hizo | Resultado | Paper |
|---|---|---|---|
| 4.1 Replicación | Nuevo código que reproduce la Etapa 3 | 18 de 18 celdas idénticas | §8 |
| 4.2 Decisiones de protocolo | 6 decisiones probadas en 2024 | Lo que más ayuda: elegir la época por F1 (+0.059 a la LSTM) | §8 |
| 4.3 Optuna para las redes | 80 intentos, 17–20 hiperparámetros | Ninguna baja la pérdida de validación del nivel del azar (ln 3) | §8 |
| 4.4 Optuna para LR y XGBoost | 150 intentos | LR: L2, C = 0.000165, RobustScaler | §8 |
| 4.5 Más variables (93) | Contexto de mercado ampliado | No ayuda → descartado | No |
| 4.6 Costos de transacción | 5 y 10 puntos base | LR con 10 pb: Sharpe +0.62; XGBoost +0.01 | No |
| 4.7 Intervalos y año por año | Bootstrap por bloques; prueba en 2020–2025 | Ver abajo | IC: §8; año por año: No |

- **Resultado principal (F1-macro, prueba 2025, modelo global):**

| Modelo | A (10 años) | B (6 años) | C (4 años) |
|---|---:|---:|---:|
| **Regresión Logística** | **0.406** | **0.404** | **0.400** |
| XGBoost | 0.359 | 0.359 | 0.362 |
| LSTM | 0.373 | 0.369 | 0.317 |
| CNN-LSTM | 0.245 | 0.372 | 0.338 |
| CNN 1D | 0.263 | 0.359 | 0.294 |

  La LR es significativamente mejor que cada uno de los otros cuatro en los
  tres experimentos (intervalos bootstrap, 95 %) y tiene el mejor Sharpe en
  los tres (+0.95, +0.89, +0.93). El paper publica B con intervalos
  **[PAPER §8]**; A y C con intervalos son **[SOLO TT]**.
- **Prueba año por año** (antes "walk-forward"; se corrió aquí pero se
  analizó en la Etapa 6) **[SOLO TT]**: para cada año de 2020 a 2025 se
  entrena con 5 años, se valida con el anterior y se prueba en ese año.
  Promedio: XGBoost 0.356, LR 0.350, CNN-LSTM 0.328, LSTM 0.314, CNN 0.292;
  solo los clásicos tienen Sharpe positivo (+0.22). Ningún modelo pasa de
  0.394 en ningún año.

### Etapa 5 — Búsqueda de mejoras (fin de agosto) · [SOLO TT]

Sobre el protocolo de la Etapa 4, sin cambiar el problema:

| Prueba | Resultado | Decisión |
|---|---|---|
| Calibración isotónica de probabilidades | Ayuda un poco a XGBoost; empeora a la LR y a las redes | Descartada (no aplica al modelo final) |
| Umbral económico de mantener | Sube el Sharpe, se derrumba el F1 | Descartada |
| Mezclas LR + XGBoost y de los 5 | Peor que la LR sola | Descartada |
| Promediar pesos de una red (SWA) | Sin efecto en el F1 | Descartada |
| Dar más peso a datos recientes | No ayuda a la LR | Descartada |
| Rezagos, variables entre acciones, multi-escala | −0.004 a +0.003 | Descartadas |
| **15 interacciones** (productos de pares de variables) | +0.023 en 2025; en 2019–2024 empatan (0.357 contra 0.354) | **Adoptadas en la plataforma** como equivalentes |
| Otros horizontes y percentiles de la etiqueta | Más F1 a 5–7 días, pero es otro problema | **[FUERA]** → trabajo futuro |

### Etapa 6 — Modelo de la plataforma y validación (septiembre–octubre) · [SOLO TT]

- **Por qué mantener aparecía de más:** "voto dividido" (cuando comprar y
  vender se reparten la probabilidad, gana mantener) y el régimen del VIX.
- **Etiqueta 40/60:** no corrige el exceso y empeora → se queda 30/70.
- **Global contra por acción sobre los mismos días:** el global gana con
  significancia en LR, LSTM y CNN 1D; empata en XGBoost y CNN-LSTM.
- **Ajuste:** reentrenar con el peso de la clase mantener × 0.90, elegido
  por origen rodante 2019–2024 (sin ver 2025 ni 2026). Antes (julio) se
  usaba un factor fijo sobre la probabilidad de mantener; se descartó porque
  estaba ajustado a 2024.
- **2026 (enero–septiembre), datos que el modelo nunca vio:** F1 0.354,
  kappa 0.035, Sharpe +0.29, mantener 40 % (real 35 %).
- **Plataforma:** niveles de seguridad calibrados con origen rodante; se
  midió el efecto de que la ventana de las redes termine un día antes
  (≈ 0.007 de F1).
- **El modelo de la plataforma:** LR L2, C = 0.000165 (Etapa 4) + 15
  interacciones (Etapa 5) + peso de mantener × 0.90 (Etapa 6), entrenado con
  2018–2025 (la configuración de B extendida hasta 2025). Versión
  `LR-v8-interactions-holdw090`.
- **Respuesta a la sinodal (26 de octubre)** — `scripts_opt/observaciones_sinodal.py`,
  detalle en [D9](D_defensa/D9_OBSERVACIONES_SINODAL.md):
  - Las ocho métricas para los cinco en las mismas filas: la LR es la mejor
    en todas, en A, B y C.
  - Elección del modelo: la validación de un año no sirve para escoger; en
    seis años LR y XGBoost empatan y las redes quedan abajo con
    significancia; ante el empate se elige la LR por sencillez y costos.
  - **Prueba ciega 2026 de los cinco** (ajustes congelados, entrenamiento
    2020–2024): LR primera en F1 (0.346) sin diferencia significativa con
    XGBoost, LSTM y CNN-LSTM; en dinero dos redes salen mejor ese año.
  - Multicolinealidad: 26 variables con VIF > 10. Con el protocolo final, las
    61 contra un filtro VIF ≤ 10 (45 variables): las 61 son mejores en 11 de
    15 casos; el filtro perjudica a las redes y a los clásicos les da igual.

---

## 5. Fuera del planteamiento (trabajo futuro) · [FUERA]

El planteamiento del TT es **una señal diaria** (horizonte de un día) con
**etiqueta 30/70** y **datos gratuitos de precios**. Lo que cambia
cualquiera de esas tres cosas no se reporta como resultado, sino como
trabajo futuro:

| Idea | Por qué sale del planteamiento | Qué se vio |
|---|---|---|
| Predecir a 2–10 días | Ya no es una señal diaria | Con 5–7 días y 25/75: F1 ≈ 0.43, Sharpe ≈ +1.5 (Etapa 5) |
| Otros percentiles (25/75, 20/80) | Cambia la definición de las clases | Algunos suben el F1; no comparables con el TT |
| Datos alternativos (noticias, macroeconómicos, opciones) | No son precios gratuitos | No se probaron |
| Datos intradía | Otra frecuencia | No se probaron |
| GRU, Transformers | Otras arquitecturas | No se corrieron |
| Ejecución real con costos y deslizamiento | Otro problema (operación) | Solo costos fijos en la Etapa 4 |

---

## 6. Qué usa el paper, sección por sección

| Sección del paper | Contenido | Viene de |
|---|---|---|
| §3 Datos y etiqueta | 7 acciones, 61 variables, etiqueta 30/70, experimentos A/B/C con prueba 2025 | Etapa 3 |
| §4 Modelos | Configuración de los cinco | Etapa 3 (texto heredado de TT1, ver punto 2 de la sección 8) |
| §5 Evaluación | F1-macro, simulación económica, por qué no accuracy | Etapa 3 |
| §6 Preselección de variables | Filtrar empeora en 11 de 15 casos | **Etapa 2** (ver punto 1 de la sección 8) |
| §7 Resultados | 120 corridas, global y por acción, variación por acción | Etapa 3 |
| §8 Robustez | Protocolo estricto, Optuna para todos, intervalos de B | Etapa 4 |
| §9–§11 | Discusión, limitaciones (un solo año de prueba, sin costos), conclusiones | — |

**No está en el paper:** la Etapa 1 (sus cifras), la Etapa 2 (salvo §6),
intervalos de A y C, costos, prueba año por año, permutación, toda la Etapa
5, toda la Etapa 6 y la plataforma. Por eso el TT es más amplio que el paper
y lo que el paper declara como limitación (un solo año, sin costos) el TT ya
lo resolvió.

---

## 7. Equivalencias con el repositorio

| Etapa | Nombre viejo | Scripts | Resultados | Documento de trabajo |
|---|---|---|---|---|
| 1 | v1 | `scripts_v1/` | `tesis_ml_stocks/` | Reporte TT1 |
| 2 | "v0", v1 (optimización), v2, v3 | `scripts_opt/opt_*.py`, `common.py`, `common_v2.py`, `feature_engineering_v2.py`, `opt_*_v2.py`, `opt_lgbm.py`, `stacking.py`, `soft_voting.py`, `ensemble_lr_xgb.py`, `lr_confidence_filter.py`, `common_v3.py`, `train_all_v3.py`, `analisis_feature_selection.py`, `consolidar_120.py`, `reporte_final.py` | `RESULTADOS_OPTIMIZADOS/modelos_optimizados*/`, `stacking/`, `soft_voting/`, `ensemble_lr_xgb/`, `lr_confidence_filter/`, `v3/`, `reportes/` | `docs/GUIA_PROGRESO.md`, `docs/ANALISIS_FEATURE_SELECTION.md` |
| 3 | v4 | `common_v4.py`, `train_all_v4.py`, `consolidar_v4.py`, `replicar_lr_v4.py`, `plots_paper.py` | `RESULTADOS_OPTIMIZADOS/v4/` | Paper §7 |
| 4 | v5, pasos V0–V6 | `diag_deep.py`, `common_v5.py`, `run_v5.py`, `build_dataset_v5.py`, `calibrar_v5.py`, `reporte_v5.py` | `RESULTADOS_OPTIMIZADOS/v5/` | `docs/DIAGNOSTICO_MODELOS_PROFUNDOS.md`, `docs/PLAN_MAESTRO_BUSQUEDA.md`, `docs/RESULTADOS_V5.md` |
| 5 | v7 "Vía 7", v8 "Vía 8" | `via7_refinamiento.py`, `via8_dataset.py`, `via8_target_extendido.py`, `via8_combinado.py` | `RESULTADOS_OPTIMIZADOS/v7/`, `v8/` | `docs/VIA7_REFINAMIENTO.md`, `docs/VIA8_DATASET.md` |
| 6 | "septiembre" | `analisis_hold_global.py`, `ajuste_hold_rolling.py`, `ajuste_hold_2026.py`, `evaluar_produccion_2026.py`, `entrenar_produccion.py`, `calibrar_niveles_confianza.py`, `verificar_ventana_redes.py`, `calibrar_hold.py` (antecedente de julio) | `RESULTADOS_OPTIMIZADOS/analisis_hold/`, `calibracion_hold/` | `docs/ANALISIS_HOLD_Y_GLOBAL.md`, `JUSTIFICACION_LIMITE_DEL_MODELO.md` |

**Por qué no hay "v6":** la numeración vieja llamó V0–V6 a los pasos internos
de v5 y luego saltó a v7. Con las etapas ese hueco desaparece.

**Historia del modelo en la plataforma:** julio, LR elasticnet de la Etapa 2
→ 26 de agosto, LR de la Etapa 4 + interacciones (Etapa 5) → 30 de
septiembre, + peso de mantener × 0.90 (Etapa 6).

---

## 8. Puntos a cuidar (para la estrategia de defensa)

Lo que un sinodal podría encontrar si revisa con detalle. Ninguno cambia la
conclusión, pero hay que tener la respuesta lista:

| # | Punto | Dónde | Respuesta corta |
|---|---|---|---|
| 1 | El §6 del paper (preselección) viene de la Etapa 2: Experimento A con la prueba vieja y configuraciones elegidas con la prueba | Paper §6 | **Confirmado con el protocolo final** (26 oct): un filtro VIF ≤ 10 calculado solo con el entrenamiento empeora en 11 de 15 casos ([D9 §3](D_defensa/D9_OBSERVACIONES_SINODAL.md)); además la LR por acción pasa de 0.355 (4 variables) a 0.392 (las 61) |
| 2 | El paper dice que la CNN-LSTM recibe 5 canales OHLCV; el código de la Etapa 3 le da las 61 variables | Paper §4 | Frase heredada del diseño de TT1; en la corrida publicada las cinco reciben lo mismo |
| 3 | En la Etapa 3 la ventana de las redes se eligió con la prueba | Paper §7 | El paper lo declara; favorecía a las redes y aun así ganó la LR; la Etapa 4 lo corrigió |
| 4 | Las 15 interacciones se propusieron viendo 2025 | Etapa 5 | Validadas después en 2019–2024: empatan (0.357 contra 0.354); los resultados de A/B/C son sin ellas |
| 5 | 2025 fue el mejor año del modelo | Etapa 4, año por año | El año se fijó antes de ver resultados; por eso se reporta también año por año y 2026 |
| 6 | En año por año la LR empata con XGBoost | Etapa 4 | La LR gana con significancia en A, B y C, aguanta mejor los costos y es más simple |
| 7 | La prueba de permutación pasa en 2025 pero no en 2024 | Etapa 4 | Coherente con que la señal es débil e inestable entre años; se dice como limitación |
| 8 | La ventana de las redes termina un día antes que la de la LR | Etapas 3–4 | Medido: cuesta ≈ 0.007 de F1, no cambia el orden |
| 9 | La cifra de mayo (0.417) y la mejora de 5–7 días (0.43) | Etapas 2 y 5 | **[NO CITAR]** / **[FUERA]**: protocolo inválido y otro problema |
| 11 | La elección de la LR podría parecer hecha con la prueba (en validación 2024 no era la primera) | Etapas 4 y 6 | Criterio declarado en [D9 §2](D_defensa/D9_OBSERVACIONES_SINODAL.md): seis años (empate con XGBoost) + sencillez y costos + prueba ciega 2026 |
| 12 | En la prueba ciega 2026 dos redes tienen mejor Sharpe que la LR | Etapa 6 | Un Sharpe de diez meses no es significativo; en clasificación la LR sigue primera; en dinero el orden cambia cada año |
| 10 | Peor caída de la simulación de la LR en 2025: −45 % | Etapa 4 | Sin costos ni control de riesgo; el TT no propone operar con dinero real |

---

## 9. Cifras que se pueden citar (y de dónde salen)

| Cifra | Qué es | Etapa | Paper |
|---|---|---|---|
| 0.404 [0.379, 0.428] | LR, Experimento B, prueba 2025 | 4 | §8 |
| 0.406 / 0.404 / 0.400 | LR en A / B / C | 4 | Solo B |
| +0.89 | Sharpe de la LR en B, sin costos | 4 | §8 |
| +0.62 | Sharpe de la LR en B con 10 pb | 4 | No |
| 0.350 y 0.356 | LR y XGBoost, promedio año por año 2020–2025 | 4 | No |
| 0.399 | LR, promedio A/B/C de la comparación en igualdad | 3 | §7 |
| 11 de 15 | Casos en que filtrar variables empeora | 2 | §6 |
| 18 de 21 | Comparaciones en que el global le gana al por acción (LR) | 6 | No |
| 0.354 | Modelo de la plataforma en 2026 | 6 | No |
| ≈ 0.333 | Azar con tres clases | — | — |
