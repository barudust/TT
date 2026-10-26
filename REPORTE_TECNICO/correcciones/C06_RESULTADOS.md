# C06 — Capítulo 6: Experimentación y resultados (p. 82–98)

> **Diagnóstico:** §6.2 a §6.5 (13 páginas, Tablas 15–28) son los resultados
> de TT1 (Etapa 1): modelo por acción, variables distintas por modelo,
> lookback de las redes elegido **con la prueba**, Exp A con otra prueba y
> redes evaluadas sobre menos días. Con esas cifras gana XGBoost. El
> resultado del TT es el de la Etapa 4, que hoy aparece en un párrafo de
> §6.6.3. Además, §6.2–6.5 tienen varios errores de conteo y afirmaciones que
> sus propias tablas contradicen (C-21 a C-28).
>
> **Acción principal:** reestructurar el capítulo por etapas
> (`01_ESTRUCTURA_PROPUESTA.md`, cap. 6), condensar TT1 en una tabla y
> poner la Etapa 4 como resultado principal. Borrador:
> `textos/T06_resultados.md`. Tablas `tablas/T-01`, `T-07` a `T-13`,
> `T-17` a `T-21`. Gráficas `graficas/G01`–`G07`.

## Resumen de puntos

| ID | Página | Sección | Tema | Prioridad |
|---|---|---|---|---|
| 6-01 | 82 | 6 (intro) | Estructura y alcance del capítulo | CRÍTICO |
| 6-02 | 82 | 6.1 | Versiones de bibliotecas | CRÍTICO |
| 6-03 | 82 | 6.1 | "Ocho scripts" | IMPORTANTE |
| 6-04 | 82–83 | 6.1 | Estrategia por activo; hiperparámetros fijos | CRÍTICO |
| 6-05 | 83 | 6.2 | **Lookback elegido con la prueba** | CRÍTICO |
| 6-06 | 83–86 | 6.2, Tablas 15–17 | Resultados de TT1 como resultado | CRÍTICO |
| 6-07 | 83 | 6.2.1 | Partición A | CRÍTICO |
| 6-08 | 85 | 6.2.3 | "posterior a la pandemia" | FORMA |
| 6-09 | 86 | 6.3 / 6.4 | Títulos intercambiados | FORMA |
| 6-10 | 87 | 6.3.1 | "en todos los experimentos" | IMPORTANTE |
| 6-11 | 87 | 6.3.1 | La asimetría de variables ya se resolvió | CRÍTICO |
| 6-12 | 88 | 6.3.3 | Conteos de la Tabla 20 | IMPORTANTE |
| 6-13 | 88–89 | 6.3.4 | Tabla 21: lookback no declarado | IMPORTANTE |
| 6-14 | 89 | 6.3.6 | Aporte del bloque recurrente | IMPORTANTE |
| 6-15 | 90 | 6.4 | Sin costos; días distintos "no afectan la validez" | CRÍTICO |
| 6-16 | 91 | 6.4.1 | TSLA y MSFT | IMPORTANTE |
| 6-17 | 91–92 | 6.4.3, Tabla 25 | Mejores casos individuales | IMPORTANTE |
| 6-18 | 92 | 6.5 | "el año 202" | FORMA |
| 6-19 | 92 | 6.5 | "Análisis por subperíodos" | IMPORTANTE |
| 6-20 | 93–95 | 6.5.2–6.5.4 | Errores en Tablas 27–28 y su texto | IMPORTANTE |
| 6-21 | 95 | 6.6 | Primera persona; v1–v8 | CRÍTICO |
| 6-22 | 95 | 6.6.1–6.6.2 | Etapa 2: nombres y multicolinealidad | IMPORTANTE |
| 6-23 | 95–96 | 6.6.3 | **El resultado principal en un párrafo** | CRÍTICO |
| 6-24 | 96 | 6.6.3 | "+0.033" contra el paper | IMPORTANTE |
| 6-25 | 96 | 6.6.4–6.6.5 | Ensambles y refinamientos: nombres | FORMA |
| 6-26 | 96–97 | 6.6.6 | Etiqueta y variables: marcar "fuera del planteamiento"; interacciones | IMPORTANTE |
| 6-27 | 97 | 6.6.7 | Año por año: agregar la versión limpia y la prueba conjunta | IMPORTANTE |
| 6-28 | 97 | 6.6.7 | 2026: dos cifras distintas | IMPORTANTE |
| 6-29 | 98 | 6.6.8, Tabla 30 | Nombres y una fila nueva | FORMA |
| 6-30 | — | Nuevo | Etapa 3 (paper §7) | CRÍTICO |
| 6-31 | — | Nuevo | Etapa 4 completa | CRÍTICO |
| 6-32 | — | Nuevo | Diagnóstico de las redes | IMPORTANTE |
| 6-33 | — | Nuevo | Etapa 6: global contra por acción, exceso de mantener | IMPORTANTE |
| 6-34 | — | Nuevo | Selección del modelo desplegado | CRÍTICO |
| 6-35 | — | Nuevo | Gráficas | IMPORTANTE |

---

### 6-01 · p. 82 · Introducción · CRÍTICO
**Dice:** "…cerrando con un análisis por subperíodos. Todos los resultados
corresponden al conjunto de prueba de 2025, que permanece constante en los
tres experimentos".
**Debe decir:** presentar el capítulo por etapas: Etapa 1 (línea base de
TT1, resumida), Etapa 2 (primeras mejoras), Etapa 3 (comparación en igualdad
de condiciones, publicada en MICAI §7), **Etapa 4 (protocolo final,
resultado principal)**, robustez en el tiempo (año por año, permutación,
prueba ciega 2026), Etapa 5 (búsqueda de mejoras) y Etapa 6 (modelo de la
plataforma), y cerrar con la selección del modelo desplegado. Aclarar que el
resultado principal es el de 2025 con el protocolo de la Etapa 4 y que
2020–2025 y 2026 lo complementan.

### 6-02 · p. 82 · §6.1, versiones · CRÍTICO
**Dice:** Python 3.12.3, pandas 3.0.0, numpy 2.4.4, yfinance 1.2.0,
scikit-learn 1.8.0, xgboost 3.2.0, PyTorch 2.11.0, CUDA 12.8, matplotlib
3.10.9, seaborn 0.13.2.
**Debe decir:** las versiones registradas en el material suplementario del
paper para la investigación: **Python 3.13.5, scikit-learn 1.7.2, PyTorch
2.12 (CUDA 12.8), XGBoost 3.2.0, Optuna 4.8**; y para la plataforma
(`api/requirements.txt`): Flask 3.1.3, SQLAlchemy 2.0.49, pandas 3.0.2, numpy
2.4.4, scikit-learn 1.7.2, yfinance 1.3.0, APScheduler 3.11.2, gunicorn 23.0.
Explicar por qué scikit-learn está fijo en 1.7.2 en ambos (el `.pkl` debe
cargar con la misma versión con que se entrenó). El hardware (Ryzen 5 7600,
RTX 5060 Ti, 32 GB, WSL2) es correcto. Ver S-09.

### 6-03 · p. 82 · §6.1, "ocho scripts" · IMPORTANTE
**Dice:** "El pipeline de experimentación se organiza en ocho scripts…
Los Scripts 06, 07 y 08 entrenan y evalúan el LSTM, el CNN-LSTM y el CNN
1D".
**Acción:** eso describe el pipeline de TT1 y no coincide con el repositorio
(`scripts_v1/08_evaluate_models.py` evalúa; la CNN 1D no está en
`scripts_v1/`; C-37). Reemplazar por la tabla de scripts por etapa
(`tablas/T-16`) o remitir al anexo de reproducibilidad.

### 6-04 · p. 82–83 · §6.1, estrategia y entrenamiento · CRÍTICO
- "La estrategia de entrenamiento principal consiste en ajustar un modelo
  independiente por cada uno de los siete activos" → global principal (C-34).
- "Para los modelos de aprendizaje profundo la arquitectura y los
  hiperparámetros de entrenamiento son fijos por diseño… dos configuraciones
  por modelo… 20 y 60 días" → Optuna (C-08, C-12).
- "la fijación de la semilla aleatoria en 42 para numpy, Python y PyTorch en
  todos los scripts" → cinco semillas en la evaluación final y semilla 42 en
  Optuna (4-51).
Si se conserva, que quede como descripción de la **Etapa 1**.

### 6-05 · p. 83 · §6.2, párrafo 1 · CRÍTICO
**Dice:** "Para los modelos con ventana de retroceso variable… se reporta en
cada caso la configuración de lookback que produjo el mayor F1-macro sobre
el conjunto de prueba del activo correspondiente".
**Acción:** dejarlo explícito como **defecto del protocolo de la Etapa 1**
(y de la Etapa 3, que el paper declara): elegir con la prueba favorece a las
redes. El protocolo final lo corrige (lookback elegido con 2024) y, aun sin
esa ventaja, las redes quedan debajo. Es un argumento a favor de la
conclusión, no en contra; pero el documento no puede presentar esas cifras
como el resultado.

### 6-06 · p. 83–86 · §6.2 y Tablas 15–17 · CRÍTICO
**Acción:** condensar las tres tablas por activo en una sola tabla de
**Etapa 1** (`tablas/T-01`: promedio, mínimo y máximo de F1 y Sharpe medio
por modelo) con una nota de por qué no es comparable con las etapas
siguientes: variables distintas por modelo, por acción, lookback elegido con
la prueba, Exp A con prueba 2024–2025, redes sobre menos días. Las tablas
por activo pueden ir a un anexo. Conservar dos observaciones de TT1 que
siguen siendo ciertas: las redes colapsan hacia una clase en algunos casos
(LSTM en NVDA, Exp A: mantener el 98.9 % de los días) y la variación entre
acciones es grande.

### 6-07 · p. 83 · §6.2.1 · CRÍTICO
**Dice:** "periodo 2014–2021 para entrenamiento y 2022–2023 para
validación. La Tabla 15 resume los resultados… sobre el conjunto de prueba
de 2025".
Según la Tabla 3, en TT1 la prueba de A era 2024–2025 (C-04). Si se conserva
la tabla de TT1, decir "prueba 2024–2025". En el resto del documento, A =
2014–2023 / 2024 / 2025.

### 6-08 · p. 85 · §6.2.3 · FORMA
**Dice:** "concentrándose exclusivamente en el régimen de mercado posterior
a la pandemia". **Debe decir:** "2020–2023, que incluye la pandemia y la
recuperación".

### 6-09 · p. 86 · Títulos de 6.3 y 6.4 · FORMA
6.3 "Resultados económicos por experimento" contiene la jerarquía de
clasificación; 6.4 "Comparativa entre modelos" contiene lo económico (C-20).
Se resuelve con la estructura nueva.

### 6-10 · p. 87 · §6.3.1 · IMPORTANTE
**Dice:** "los dos modelos de aprendizaje automático clásico superan a las
tres arquitecturas de aprendizaje profundo en F1-macro promedio en todos los
experimentos".
**Falso con sus propias tablas:** en el Experimento C la CNN-LSTM (0.356)
supera a la LR (0.350) (Tabla 17; C-21). Con el protocolo final sí es cierto
para la LR: es la mejor en A, B y C con significancia.

### 6-11 · p. 87 · §6.3.1 · CRÍTICO
**Dice:** "Esta diferencia… está influenciada por la asimetría en el número
de características disponibles para cada familia… Esta limitación del diseño
experimental se discute en el capítulo 7".
**Debe decir (en la nueva sección de Etapa 1):** "TT1 identificó la
asimetría de variables como la principal limitación de su comparación. Desde
la Etapa 3 los cinco modelos reciben las mismas 61 variables, y los modelos
clásicos siguen arriba: la asimetría no explicaba la diferencia. En el
Experimento B por acción, la LR pasó de 0.355 (4 variables) a 0.392 (61)".
**Fuente:** `ESTUDIO_TT/D_defensa/D1` §1; paper Tabla 5.

### 6-12 · p. 88 · §6.3.3 · IMPORTANTE
"Regresión Logística lidera en cuatro de los siete activos en F1-macro y en
cinco en razón de Sharpe" → la Tabla 20 da **tres y tres** (C-22). Si la
tabla se elimina por ser de TT1, el problema desaparece.

### 6-13 · p. 88–89 · §6.3.4, Tabla 21 · IMPORTANTE
Los valores "por activo" de las redes (0.288, 0.323, 0.306) no coinciden con
la Tabla 16 (0.297, 0.342, 0.329) porque la 21 usa lookback 20 y la 16 el
mejor lookback elegido con la prueba (C-23); decirlo si se conserva. El
mensaje (el modelo global supera al por acción) es correcto y se mantiene,
pero la evidencia sólida es la de la Etapa 6: comparación **pareada sobre
los mismos días**, la LR global gana 18 de 21 pares (p = 0.002) y el global
gana o empata en los cinco modelos (`tablas/T-17`).

### 6-14 · p. 89 · §6.3.6 · IMPORTANTE
**Dice:** "En el Experimento B el CNN-LSTM supera al CNN 1D en 0.019 puntos…
con lookback 20… En los Experimentos A y C las diferencias son de 0.012 y
0.025 puntos respectivamente a favor del CNN-LSTM. El bloque recurrente
aporta valor predictivo en todos los experimentos".
**Errores:** con lookback 20 la diferencia en B es 0.017 (0.323 − 0.306);
en A gana la CNN 1D (0.333 contra 0.321, como dice §6.2.1); por lo tanto no
"en todos los experimentos" (C-24). En la Etapa 4, en B la CNN-LSTM (0.372)
y la CNN 1D (0.359) no difieren significativamente. Corregir o eliminar.

### 6-15 · p. 90 · §6.4, párrafos 1–2 · CRÍTICO
- "No se incorporan costos de transacción ni deslizamiento de precio" → en
  la Etapa 4 se calculan con 5 y 10 pb (`tablas/T-10`).
- **Dice:** "Regresión Logística y XGBoost operan sobre los 248 días hábiles
  del conjunto de prueba completo, mientras que los modelos con ventana de
  retroceso de 20 días disponen de 228 días y los de 60 días de 188 días…
  Esta diferencia… no afecta la validez de la comparación al trabajar con
  retornos anualizados y razón de Sharpe".
  **Debe decir:** esa diferencia **sí** afecta: los modelos se evalúan sobre
  días distintos y el F1 no es comparable. Es exactamente la observación de
  la sinodal sobre métricas justas. El protocolo final la corrigió (ventanas
  sobre la serie continua, asignadas por la fecha de la etiqueta): **los
  cinco modelos se evalúan sobre las mismas 1 736 filas**
  (`RO/observaciones_sinodal/1_mismas_filas.csv`). Texto en
  `textos/T03_justificaciones_sinodal.md` §2.

### 6-16 · p. 91 · §6.4.1, último párrafo · IMPORTANTE
"TSLA y MSFT son los activos más difíciles desde la perspectiva económica
para los modelos clásicos, con Sharpe negativo en ambos modelos" → XGBoost
en TSLA, Exp B, tiene +0.885 (Tabla 28; C-25). Solo MSFT es negativo en
ambos.

### 6-17 · p. 91–92 · §6.4.3 y Tabla 25 · IMPORTANTE
**Dice:** "los mejores resultados económicos individuales de todo el trabajo
terminal corresponden a modelos de aprendizaje profundo… CNN 1D sobre META
en el Experimento C, con una razón de Sharpe de 3.640…".
**Acción:** eliminar la sección o agregar la advertencia: son los máximos de
105 combinaciones (5 modelos × 7 acciones × 3 experimentos), con el lookback
elegido mirando la prueba; con tantas comparaciones, algún valor alto es
esperable por azar. No es evidencia de nada y un sinodal lo puede usar en
contra ("¿entonces por qué no usaron la CNN?"). Ver "No citar" en
`03_CIFRAS_VIGENTES.md`.

### 6-18 · p. 92 · §6.5 · FORMA
"comparten el mismo conjunto de prueba (el año 202)" → **2025**.

### 6-19 · p. 92 · §6.5 · IMPORTANTE
**Dice:** "Análisis por subperíodos"; el contenido es cómo cambia el
desempeño con la longitud del entrenamiento (A, B, C), con la misma prueba.
**Acción:** renombrar "Sensibilidad a la longitud del entrenamiento" y
reservar el análisis por periodos para la prueba año por año (2020–2025) y
2026. Con el protocolo final la conclusión es simple: la LR no depende de la
longitud (0.406 / 0.404 / 0.401) y las redes sí (CNN-LSTM 0.245 / 0.372 /
0.338).

### 6-20 · p. 93–95 · §6.5.2–6.5.4, Tablas 26–28 · IMPORTANTE
Errores si se conservan (son de TT1; lo recomendable es eliminarlos):
- §6.5.2: "TSLA y GOOGL son los activos más sensibles… en Regresión
  Logística, con rangos de 0.066 y 0.079" → AAPL tiene 0.078 (C-28). En la
  Tabla 27, GOOGL marcado "Ambos" aunque LR (0.079) > XGBoost (0.053).
- §6.5.3: "TSLA es el único activo donde XGBoost produce Sharpe
  consistentemente positivo en los tres experimentos" → también AMZN y META
  (C-26).
- §6.5.4: "Primera, los modelos clásicos son más robustos… mientras que los
  modelos de aprendizaje profundo muestran mayor sensibilidad" → la CNN 1D
  tiene el rango más chico (0.004).
- §6.5.4: "NVDA es el activo más difícil… ningún modelo produce Sharpe
  positivo en los tres experimentos… F1-macro promedio… 0.269" → la LR en
  NVDA tiene Sharpe positivo en los tres (0.730, 1.479, 0.735) y el promedio
  de NVDA en las Tablas 15–17 es ≈ 0.299; además §6.2.3 dice que el más
  difícil es TSLA (C-27).

### 6-21 · p. 95 · §6.6, introducción · CRÍTICO
**Dice:** "Los resultados de las secciones anteriores nos dejaron con una
sensación incómoda… pensamos que lo honesto era seguir buscando…" y "Las
iteraciones se nombran v2 a v8… y no existe una v6 porque esa sigla se usó
para una sub-etapa de la v5".
**Acción:** (1) tono impersonal; (2) sustituir v1–v8 por las **etapas**
(`04_GLOSARIO_DE_REDACCION.md`); (3) con la estructura nueva, esta
"experimentación adicional" deja de ser adicional: sus secciones pasan a ser
6.3 a 6.8. La frase sobre la v6 se elimina.

### 6-22 · p. 95 · §6.6.1–6.6.2 · IMPORTANTE
- 6.6.1 (v2 y v3) → **Etapa 2**. Las cifras son correctas.
- 6.6.2 (selección de variables) → Etapa 2, publicado en el paper (§6,
  11 de 15). Agregar el experimento nuevo de **multicolinealidad** con el
  protocolo final (VIF ≤ 10, 45 variables, 11 de 15 a favor de las 61; el
  filtro perjudica a las redes) — `tablas/T-11`, `graficas/G06`.
- "desde la v4 todos los modelos usan las mismas variables" → "desde la
  Etapa 3".

### 6-23 · p. 95–96 · §6.6.3 · CRÍTICO
**Hoy:** el protocolo final y su resultado (LR 0.404, redes 0.359–0.372)
ocupan un párrafo.
**Debe ser** la sección central del capítulo (Etapa 4), con:
1. El protocolo (dev/final, mismas filas, Optuna para los cinco) — remite
   al capítulo 4.
2. F1-macro con intervalos en A, B y C (`tablas/T-09`, `graficas/G01`).
3. Las ocho métricas (`tablas/T-10`).
4. Diferencias pareadas (la LR significativamente mejor que los otros
   cuatro en A, B y C; entre los otros cuatro no hay diferencias
   significativas en B).
5. Economía con y sin costos y rotación (`graficas/G02`).
6. Comparación con la Etapa 3: la LR sube y las redes bajan cuando se quita
   la ventaja de elegir el lookback con la prueba (`graficas/G03`).
7. Diagnóstico de las redes (6-32).

### 6-24 · p. 96 · §6.6.3 · IMPORTANTE
**Dice:** "La búsqueda le sumó +0.033 de F1-macro a la Regresión Logística,
que quedó en 0.404 sobre 2025".
**Revisar:** el paper (Tabla 7, columna Δ) reporta **+0.019** respecto a la
Etapa 3 (0.385 → 0.404). Si +0.033 se refiere a otra comparación, decir cuál;
si no, usar +0.019.
Además: "agrupación de datos" en la lista de seis decisiones → "*pooling*
temporal" (resumen de la secuencia), que es lo que se probó.

### 6-25 · p. 96 · §6.6.4–6.6.5 · FORMA
Cifras correctas. Cambiar "v7" por **Etapa 5** y aclarar que el stacking,
la votación suave y la mezcla LR + XGBoost con pesos 0/1 son de la Etapa 2, y
las mezclas optimizadas con 2024 y los refinamientos (calibración isotónica,
umbral de mantener, SWA, recencia) son de la Etapa 5.

### 6-26 · p. 96–97 · §6.6.6 · IMPORTANTE
- Otros horizontes y percentiles: marcarlos explícitamente como **fuera del
  planteamiento** (cambian el problema) y llevarlos a trabajo futuro; no
  presentar el "F1 0.41–0.43 a 5 días" como un resultado. Ya lo dice en
  parte; reforzarlo.
- **Interacciones:** el texto dice que se conservan "como equivalentes, no
  como una mejora comprobada" (correcto). Agregar: (1) que la plataforma las
  usa porque no empeoran y se adoptaron el 26 de agosto, antes de validarlas;
  (2) que la validación posterior (2024 y origen rodante 2019–2024) dio un
  empate (0.354 contra 0.357); (3) que los resultados de A/B/C y del paper son
  **sin** interacciones. Tabla `tablas/T-20`.

### 6-27 · p. 97 · §6.6.7, Tabla 29 · IMPORTANTE
La Tabla 29 usa los ajustes elegidos con 2024 (Etapa 4), que para los años
2020–2023 son información posterior. Agregar la versión **limpia**, con los
ajustes fijos de la Etapa 3 (que no vieron ningún año): LR 0.360 (gana 3 de
6 años), XGBoost 0.356, CNN 1D 0.338, LSTM 0.331, CNN-LSTM 0.326; y la prueba
conjunta de los seis años: LR − XGBoost +0.003 (no significativa), LR − cada
red +0.017 a +0.026 (significativas). `tablas/T-12`, `graficas/G04`.
Conservar la nota de que la CNN-LSTM no tiene 2025 en la versión de la Tabla
29.

### 6-28 · p. 97 · §6.6.7, 2026 · IMPORTANTE
El párrafo de 2026 (modelo anterior 0.313, modelo con peso × 0.90 0.354,
Wilcoxon p = 0.31) es correcto. Agregar la **prueba ciega 2026 de los cinco
modelos** (enero–22 de octubre, ajustes congelados): LR 0.346, XGBoost
0.343, LSTM 0.331, CNN-LSTM 0.318, CNN 1D 0.304; solo la diferencia contra la
CNN 1D es significativa; en Sharpe, la CNN 1D (+0.88) y la LSTM (+0.72)
superan a la LR (+0.38). Explicar que **0.354 y 0.346 son modelos y periodos
distintos** (`03_CIFRAS_VIGENTES.md` §9) y la lectura honesta del Sharpe de
2026 (un periodo de diez meses no es significativo; en dinero el orden
cambia cada año). `tablas/T-13`, `graficas/G05`.

### 6-29 · p. 98 · §6.6.8 y Tabla 30 · FORMA
Cambiar los nombres de la columna "Línea explorada" a las etapas
("Umbrales por clase (Etapa 2)", "Hiperparámetros (Etapa 4)", etc.).
Agregar una fila: "Prueba ciega 2026 de los cinco | LR primera (0.346), sin
diferencia significativa salvo contra la CNN 1D". "cerca de treinta técnicas
en siete iteraciones" → "en cinco etapas". El párrafo de trabajo futuro pasa
a §7.5.

### 6-30 · Nuevo · Etapa 3 (paper §7) · CRÍTICO
El reporte no presenta los resultados que publicó el paper. Agregar una
sección corta con la tabla de F1 global en A/B/C (LR 0.399 promedio), la
tabla por acción (LR 0.387), la economía de B (LR Sharpe +0.755, profit
factor 1.21) y el hallazgo de que la acción explica 4.5 veces más la
variación del Sharpe que el modelo. Aclarar que el lookback de las redes se
eligió con la prueba (el paper lo declara). `tablas/T-07`.

### 6-31 · Nuevo · Etapa 4 · CRÍTICO
Ver 6-23.

### 6-32 · Nuevo · Diagnóstico de las redes · IMPORTANTE
Es la explicación de **por qué** las redes no ganan y hoy está en dos
líneas. Agregar: la pérdida de validación nunca baja de ln 3 ≈ 1.0986 (el
valor de decir 1/3 a todo) con ninguna configuración; achicar la LSTM de
592 131 a 10 275 parámetros no cambia el resultado; con paro temprano por
pérdida se restauraba la época 1 o 2; elegir la época por F1 dio +0.059 a la
LSTM; reentrenar con validación las empeora (−0.024 a −0.047); un
entrenamiento tarda 7–12 s, así que el cómputo no era la restricción. Fuente:
`ESTUDIO_TT/A_modelo/A5` §3.4 y §6; `RO/docs/DIAGNOSTICO_MODELOS_PROFUNDOS.md`.

### 6-33 · Nuevo · Etapa 6 · IMPORTANTE
Agregar: (1) global contra por acción, pareado (`tablas/T-17`); (2) el exceso
de mantener y su causa ("voto dividido": en el 100 % de los días en que dice
mantener, P(comprar) + P(vender) > P(mantener); y el régimen del VIX), lo que
se probó para corregirlo y por qué se eligió el peso × 0.90 con origen
rodante (`tablas/T-18`); (3) la confirmación en 2026 (`tablas/T-19`); (4) los
niveles de seguridad calibrados (`tablas/T-21`). Fuente: `A7` §4–5.

### 6-34 · Nuevo · Selección del modelo desplegado · CRÍTICO
Aplicar el criterio declarado en el capítulo 4 (4-46): clásicos sobre redes
en todas las pruebas; LR y XGBoost empatan en seis años; ante el empate, LR
por parsimonia (231 parámetros contra 485 árboles de profundidad 9), menor
rotación (0.38 contra 0.65) y mejor Sharpe con costos, interpretabilidad y
determinismo; confirmación en 2026. Mostrar también que elegir cada año el
mejor modelo en validación habría dado 0.342–0.344, peor que quedarse con la
LR (`03_CIFRAS_VIGENTES.md` §7.2). Texto en
`textos/T03_justificaciones_sinodal.md` §3.

### 6-35 · Nuevo · Gráficas · IMPORTANTE
El capítulo no tiene ninguna figura. Agregar las de `graficas/`:
G01 F1 con intervalos (A/B/C), G02 Sharpe con y sin costos, G03 Etapa 3
contra Etapa 4, G04 año por año, G05 prueba ciega 2026, G06 multicolinealidad,
G07 global contra por acción.
