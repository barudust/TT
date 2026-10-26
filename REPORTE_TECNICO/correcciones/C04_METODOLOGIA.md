# C04 — Capítulo 4: Metodología (p. 35–66)

> **Diagnóstico:** este capítulo describe el método de TT1 (Etapa 1):
> selección de variables distinta por modelo, Experimento A con prueba
> 2024–2025, un modelo por acción, arquitecturas de red fijas, búsqueda en
> rejilla, lookback elegido con la prueba, evaluación sin pruebas
> estadísticas y sin costos. El resultado principal del TT sale de otro
> método (Etapas 3 y 4). Hay que **reescribir** 4.1 (intro), 4.4, 4.5, 4.6,
> 4.7, 4.8, 4.9 (criterio), 4.10 y partes de 4.11, y dejar TT1 como
> antecedente en el capítulo 6 (Etapa 1).
>
> Borradores para las secciones que cambian completas:
> `textos/T04_metodologia.md` y `textos/T03_justificaciones_sinodal.md`.
> Tablas: `tablas/TABLAS_NUEVAS.md` (T-02 a T-06, T-08).

## Resumen de puntos

| ID | Página | Sección | Tema | Prioridad |
|---|---|---|---|---|
| 4-01 | 35 | 4 (intro) | CRISP-DM "secuencial"; faltan las etapas | IMPORTANTE |
| 4-02 | 35 | 4 (intro) | Pregunta de investigación sin CNN 1D | CRÍTICO |
| 4-03 | 35–36 | 4 (intro) | Hipótesis sin CNN 1D ni criterio operativo | CRÍTICO |
| 4-04 | 36 | 4 (intro) | "No se realiza prueba de significancia" | CRÍTICO |
| 4-05 | 36 | 4.1 | "Cada modelo recibe una representación distinta" | CRÍTICO |
| 4-06 | 36 | 4.1.1 | Calentamiento: MA200 aquí, MA30 en 4.2 | IMPORTANTE |
| 4-07 | 36 | 4.1.1 | "El año 2026 no se incluye" | CRÍTICO |
| 4-08 | 37 | 4.1.2 | Tabla 2: título y sectores | IMPORTANTE |
| 4-09 | 37 | 4.1.2 | "generalización del modelo de Deep Learning" | FORMA |
| 4-10 | 38 | 4.2 | Interpolación lineal | IMPORTANTE |
| 4-11 | 38 | 4.2 | 54 características | CRÍTICO |
| 4-12 | 38–39 | 4.2 | Etiqueta: conservar; detalle de plataforma | FORMA |
| 4-13 | 39 | 4.2, Tabla 3 | **Partición A de TT1** | CRÍTICO |
| 4-14 | 39 | 4.2 | "igual jerarquía" contra "B principal" | IMPORTANTE |
| 4-15 | 39 | 4.2 | Escalado de TT1 | CRÍTICO |
| 4-16 | 39–40 | 4.3 | 54 y "desde 2009" | CRÍTICO |
| 4-17 | 40–42 | 4.3 | "Tabla 3" por "Tabla 4" | FORMA |
| 4-18 | 40 | 4.3.3 | "ocho" medias móviles | FORMA |
| 4-19 | 40 | 4.3.2 | Jegadeesh y Titman sin referencia | IMPORTANTE |
| 4-20 | 41 | 4.3.8 | semana_mes no va de −1 a 1 | FORMA |
| 4-21 | 42–46 | Tabla 4 | Detalles de fórmulas; faltan las interacciones | IMPORTANTE |
| 4-22 | 46–51 | **4.4 completo** | **Selección de características por modelo** | CRÍTICO |
| 4-23 | 51–52 | 4.5.1, Tabla 8 | Tabla duplicada y A de TT1 | CRÍTICO |
| 4-24 | 52 | 4.5.1 | "tasas de interés altas" en 2020–2023 | IMPORTANTE |
| 4-25 | 52 | 4.5.1 | "periodo alcista de 2018–2019" | FORMA |
| 4-26 | 52 | 4.5 | Faltan las validaciones adicionales | CRÍTICO |
| 4-27 | 53 | 4.5.2 | Fuentes de fuga: quitar selección, agregar protocolo | IMPORTANTE |
| 4-28 | 53–55 | 4.6 | Escaladores de TT1 | CRÍTICO |
| 4-29 | 54–55 | 4.6.4 | OHLCV local y "NVDA 800 USD" | CRÍTICO |
| 4-30 | 55 | 4.7.1 | La ventana termina en *t − 1* | IMPORTANTE |
| 4-31 | 55–56 | 4.7.2 | Lookback 20 y 60 | CRÍTICO |
| 4-32 | 56 | 4.7.3, Tabla 9 | Dimensiones con F_Exp + OHLCV; "ablación" | CRÍTICO |
| 4-33 | 56 | 4.8 | "sexto modelo" y "por activo" | CRÍTICO |
| 4-34 | 57 | 4.8.1 | LR de TT1 | CRÍTICO |
| 4-35 | 57 | 4.8.1 | "primeros 90 días del conjunto de prueba" | CRÍTICO |
| 4-36 | 57–58 | 4.8.2 | XGBoost de TT1; `scale_pos_weight` | CRÍTICO |
| 4-37 | 58 | 4.8.3 | LSTM de TT1, "sin búsqueda" | CRÍTICO |
| 4-38 | 59 | 4.8.4 | CNN-LSTM de TT1 | CRÍTICO |
| 4-39 | 59–60 | 4.8.5 | CNN 1D de TT1; "Tabla X" | CRÍTICO |
| 4-40 | 60 | 4.8.6 | Líneas base: reportar sus valores | IMPORTANTE |
| 4-41 | 60 | 4.9 | Cómo se agregan las métricas | IMPORTANTE |
| 4-42 | 61 | 4.9.1 | Fórmula de exactitud | FORMA |
| 4-43 | 61 | 4.9.1 | Agregar las métricas nuevas; F1 ponderado | IMPORTANTE |
| 4-44 | 62 | 4.9.3 | Dos fórmulas de retorno; sin costos | CRÍTICO |
| 4-45 | 62 | 4.9.3 | "Sharpe > 1 aceptable, > 2 bueno" sin fuente | IMPORTANTE |
| 4-46 | 62–63 | 4.9.4 | **Criterio de comparación y de selección** | CRÍTICO |
| 4-47 | 63 | 4.10 | "un modelo por activo, experimento y lookback"; prueba "invisible" | CRÍTICO |
| 4-48 | 63 | 4.10.1 | Rejilla → Optuna | CRÍTICO |
| 4-49 | 63 | 4.10.2 | Paro temprano contradictorio | CRÍTICO |
| 4-50 | 64 | 4.10.3 | Pesos de clase en producción | IMPORTANTE |
| 4-51 | 64 | 4.10.4 | Reproducibilidad | IMPORTANTE |
| 4-52 | 64–66 | 4.11 | Costos, rotación, Sharpe agrupado | IMPORTANTE |

---

## 4 (introducción del capítulo)

### 4-01 · p. 35 · CRISP-DM y SCRUM · IMPORTANTE
**Dice:** "CRISP-DM estructura el trabajo en seis fases secuenciales".
**Acción:**
1. CRISP-DM es **iterativo** (permite volver de evaluación a preparación
   de datos o modelado); decir "seis fases que se recorren de forma
   iterativa".
2. Agregar las **seis etapas** del proyecto como las iteraciones de
   CRISP-DM que se hicieron, con la pregunta que respondió cada una. Tabla
   `tablas/T-02`, figura `diagramas/D08_etapas.svg`, texto en
   `textos/T04_metodologia.md` §1.
3. Si se menciona SCRUM, decir cómo se aplicó (duración de los sprints,
   entregables, cómo se registró: `docs/ACTIVIDADES_SEGUIMIENTO.md`,
   historial de git).
**Por qué:** las etapas explican por qué el documento tiene resultados de
TT1, del paper y finales, y por qué cambió la conclusión.

### 4-02 · p. 35 · Pregunta de investigación · CRÍTICO
**Dice:** "¿pueden los modelos de DL (LSTM y CNN-LSTM) ofrecer un
rendimiento superior… frente a modelos clásicos (Regresión Logística y
XGBoost) y un baseline ingenuo, al estimar la dirección diaria de precios de
activos financieros líquidos?".
**Debe decir:** "¿pueden los modelos de aprendizaje profundo (LSTM, CNN 1D
y CNN-LSTM) ofrecer un desempeño superior, en métricas de clasificación y en
una simulación económica, frente a modelos clásicos (Regresión Logística y
XGBoost) y a líneas base ingenuas, al generar señales diarias de compra,
venta o mantenimiento para las siete acciones de estudio?".

### 4-03 · p. 35–36 · Hipótesis · CRÍTICO
**Acción:**
- Incluir la CNN 1D en H₀ y H₁.
- Definir qué es "superior de manera consistente" de forma verificable:
  *"un modelo es superior a otro si la diferencia pareada de F1-macro en el
  año de prueba tiene un intervalo de confianza bootstrap del 95 % que
  excluye el cero en el Experimento B (principal), la dirección se repite en
  los Experimentos A y C, y no se invierte en la prueba año por año"*.
- Texto propuesto en `textos/T04_metodologia.md` §2.

### 4-04 · p. 36 · Significancia · CRÍTICO
**Dice:** "Dado el carácter descriptivo y comparativo del estudio, no se
realiza una prueba de significancia estadística formal… se analizará el
desempeño por subperiodos anuales dentro del conjunto de prueba".
**Debe decir:** describir la validación que se hizo: intervalos bootstrap
por bloques y diferencias pareadas, prueba de permutación, prueba año por
año 2020–2025, comparación pareada global contra por acción (Wilcoxon y
signo) y prueba ciega 2026. Ver C-16 y `textos/T04_metodologia.md` §8.
**Por qué:** las pruebas existen y son el respaldo principal del resultado;
además §2.1.3 promete significancia estadística.

---

## 4.1 Descripción del conjunto de datos

### 4-05 · p. 36 · §4.1, párrafo 1 · CRÍTICO
**Dice:** "Dado que cada modelo recibe una representación de entrada
distinta en términos de número de características, método de escalado y
estructura temporal, se describe también cómo se construye el dataset
específico para cada familia de modelos".
**Debe decir:** "Los cinco modelos reciben el mismo conjunto de 61
características calculadas con el mismo código y la misma partición
temporal; solo cambia la forma: los modelos clásicos reciben el vector del
día y las redes una ventana de días consecutivos".
**Fuente:** `ESTUDIO_TT/D_defensa/D9` §5; C-18.

### 4-06 · p. 36 · §4.1.1, párrafo 3 · IMPORTANTE
**Dice (p. 36):** el calentamiento se necesita "como la media móvil de 200
días (MA200)". **Dice (p. 38):** "la media móvil de 30 días necesita al menos
30 observaciones, el ATR de 14 días necesita 14…".
**Acción:** unificar: los indicadores más largos son la media de 200 días
(`dist_ma200`, `cruce_ma50_ma200`) y la normalización del VIX con 252 días
(`VIX_norm`); por eso se descarga desde 2013 y las filas incompletas se
eliminan.

### 4-07 · p. 36 · §4.1.1, párrafo 3 · CRÍTICO
**Dice:** "La descarga finaliza el 31 de diciembre de 2025. El año 2026 no
se incluye porque al momento de construcción del dataset el año no está
completo…".
**Debe decir:** "El conjunto de desarrollo termina el 29 de diciembre de 2025
(último día con etiqueta). Los datos del 2 de enero al 22 de octubre de 2026
se descargaron después con el mismo código y se usan solo como validación
ciega: ninguna decisión del trabajo los utilizó. La plataforma descarga
además los datos de cada día hábil".
**Fuente:** `tesis_ml_stocks/01_raw_datasets_2026/`; S-12.

### 4-08 · p. 37 · §4.1.2, Tabla 2 · IMPORTANTE
**Dice:** título "Activos seleccionados para su evaluación con los modelos
de Deep Learning"; sector de GOOGL y META = "Tecnología"; "Nvidia";
"Consumo discrecional / Consumo Discrecional"; "META" con otra fuente.
**Debe decir:**

| Empresa | Ticker | Sector (GICS) |
|---|---|---|
| Apple | AAPL | Tecnologías de la información |
| Microsoft | MSFT | Tecnologías de la información |
| NVIDIA | NVDA | Tecnologías de la información |
| Alphabet | GOOGL | Servicios de comunicación |
| Meta Platforms | META | Servicios de comunicación |
| Amazon | AMZN | Consumo discrecional |
| Tesla | TSLA | Consumo discrecional |

Título: "Acciones del caso de estudio". Opcional: agregar una columna con la
volatilidad anualizada 2014–2025 para respaldar la frase "distintos niveles
de volatilidad" (se calcula de los parquet).

### 4-09 · p. 37 · §4.1.2 · FORMA
"para evaluar la generalización del modelo de Deep Learning" → "de los
modelos".

---

## 4.2 Preprocesamiento

### 4-10 · p. 38 · Valores faltantes · IMPORTANTE
**Dice:** "se aplica interpolación lineal siempre que los días faltantes
representen menos del 1%…".
**Debe decir:** "Las siete series no tienen días hábiles faltantes en el
periodo. Las series de mercado (SPY y VIX) se alinean por fecha con cada
acción y, si faltara un día, se rellena con el último valor conocido
(nunca con uno futuro)". Ver S-13.

### 4-11 · p. 38 · Cálculo de características · CRÍTICO
"se calculan 54 características técnicas" → **61** (C-01).

### 4-12 · p. 38–39 · Definición del target · FORMA
Conservar (es correcto: `shift(1)`, ventana de 252, mínimo 126). Opcional:
mencionar que la plataforma calcula la misma etiqueta para evaluar cada
señal, con una prueba automática que verifica que coincide al 100 % con la
del dataset (`api/tests/test_main.py`).

### 4-13 · p. 39 · Tabla 3 · CRÍTICO
**Dice:** A: 2014–2021 / 2022–2023 / 2024–2025, "Máximo historial, pandemia
en validación"; B "Ciclo completo post-COVID (escenario de volatilidad
media)"; C "Era moderna, robustez".
**Debe decir:**

| Experimento | Entrenamiento | Validación | Prueba | Años de entrenamiento | Papel |
|---|---|---|---|---:|---|
| A | 2014–2023 | 2024 | 2025 | 10 | Máxima historia |
| **B** | **2018–2023** | **2024** | **2025** | **6** | **Principal** |
| C | 2020–2023 | 2024 | 2025 | 4 | Solo mercado reciente |

Mencionar en una nota que en TT1 el Experimento A probaba en 2024–2025 y por
eso sus resultados no se comparaban con B y C. Ver C-04, `tablas/T-03`,
`diagramas/D09_particiones.svg`.

### 4-14 · p. 39 · "igual jerarquía" · IMPORTANTE
**Dice:** "Se definen tres escenarios de evaluación (A, B y C) con igual
jerarquía".
**Contradice** p. 52 ("escenario clave") y p. 84 ("experimento principal").
**Debe decir:** "El Experimento B se declaró principal desde el diseño
(punto medio entre cantidad de datos y vigencia del régimen); A y C sirven
para comprobar que la conclusión no depende de cuántos años se usen".

### 4-15 · p. 39 · Escalado · CRÍTICO
**Dice:** StandardScaler para LR, MinMaxScaler para LSTM y CNN-LSTM,
XGBoost sin escalar.
**Debe decir:** ver 4-28 (esta mención se puede eliminar aquí y dejar solo
§4.6).

---

## 4.3 Ingeniería de características

### 4-16 · p. 39–40 · Introducción de 4.3 · CRÍTICO
- "se construyen 54 características" → **61**.
- "Todas las características se calculan sobre los datos completos
  disponibles desde 2009" → "desde el 1 de enero de 2013" (S-14).
- "La tabla 3 presenta la descripción completa de las 54 características"
  → "La Tabla 4 presenta las 61 características".

### 4-17 · p. 40–42 · Referencias "Ver Tabla 3" · FORMA
Las nueve menciones "Ver Tabla 3, categoría…" → "Tabla 4" (C-03). Usar
referencias cruzadas automáticas.

### 4-18 · p. 40 · §4.3.3 · FORMA
"Se calculan ocho características derivadas de medias móviles" → **nueve**
(5 distancias, 3 cruces y la pendiente de la MA20). C-02.

### 4-19 · p. 40 · §4.3.2 · IMPORTANTE
"documentado por Jegadeesh y Titman (1993)" no está en la bibliografía.
Agregar: N. Jegadeesh y S. Titman, "Returns to buying winners and selling
losers: Implications for stock market efficiency", *The Journal of
Finance*, 48(1), 65–91, 1993.

### 4-20 · p. 41 · §4.3.8 · FORMA
**Dice:** "La semana del mes se normaliza al rango [−1, 1]".
**Debe decir:** "La semana del mes (1 a 5) se centra con `(s − 2.5)/2.5`,
que da valores entre −0.6 y 1" (`api/ml/features.py`, línea `semana_mes`).

### 4-21 · p. 42–46 · Tabla 4 · IMPORTANTE
La tabla es correcta (61 filas, coincide con el código). Ajustes menores:
- `obv_ratio`: el código divide entre el valor absoluto de la media:
  `OBV / |MA20(OBV)| − 1`.
- `vol_log`: `ln(Volume + 1)`.
- `ret_3d`: homogeneizar la tipografía de "ln".
- **Agregar** (en la misma tabla o en una tabla aparte) las **15
  interacciones** del modelo de la plataforma, con la aclaración de que se
  usan solo en producción y no en la comparación de los cinco modelos.
  Lista en `tablas/T-04`; fuente `api/ml/artifacts/interaction_pairs.json`.

---

## 4.4 Selección de características por modelo (p. 46–51)

### 4-22 · §4.4 completo y Tablas 5–7 · CRÍTICO
**Dice:** cada modelo recibe un subconjunto distinto elegido por un método
estadístico distinto (LR: Pearson + VIF, 8/4/3 variables; XGBoost: SHAP,
24/23/25; LSTM y CNN-LSTM: Spearman, 25/10/3, más 5 canales OHLCV).
**Acción:** **reemplazar la sección completa** por "Mismo conjunto de
características para todos los modelos", con cuatro partes:
1. **Por qué el mismo conjunto:** para atribuir una diferencia al modelo
   hay que cambiar solo el modelo; TT1 ya había identificado la asimetría de
   variables como la principal limitación de su comparación.
2. **La selección por modelo se probó y empeora:** usar las 61 fue mejor
   que el subconjunto filtrado en 11 de 15 combinaciones (Etapa 2,
   publicado en el paper §6).
3. **Multicolinealidad:** diagnóstico (26 pares con |r| > 0.9; 26 variables
   con VIF > 10) y experimento con el protocolo final (filtro VIF ≤ 10
   calculado solo con el entrenamiento, 45 variables): las 61 ganan en 11 de
   15; el filtro perjudica a las redes y a los clásicos les da igual.
4. **Las 61 son la opción más favorable para las redes**, así que la
   comparación no las perjudica.
Borrador completo: `textos/T03_justificaciones_sinodal.md` §1 y §4.
Tabla: `tablas/T-11`. La teoría del VIF pasa a §2.9 (ver 2-28).
**Qué hacer con el contenido actual:** un párrafo en 6.2 (Etapa 1) que diga
cómo se seleccionaba en TT1 y por qué se abandonó. Las Tablas 5–7 pueden ir
a un anexo si el equipo quiere conservarlas, o eliminarse.
**Por qué:** es la causa de la comparación injusta que la sinodal señaló,
contradice §3.6 y no es lo que usan los resultados finales ni el paper.

---

## 4.5 Partición temporal

### 4-23 · p. 51–52 · §4.5.1 y Tabla 8 · CRÍTICO
- La Tabla 8 repite la Tabla 3: **eliminar una de las dos** y dejar la
  versión corregida (4-13).
- "Los tres experimentos comparten el mismo conjunto de prueba (2025)" es
  correcto una vez corregida la tabla.
- **Dice (p. 52):** "El Experimento A amplía el horizonte de entrenamiento
  desde 2014 hasta 2021… coloca los años 2022 y 2023 en el conjunto de
  validación…".
  **Debe decir:** "El Experimento A entrena con 2014–2023 (diez años), que
  incluyen el ciclo alcista de 2014–2019, la pandemia, la corrección de 2022
  y la recuperación de 2023; comparte validación (2024) y prueba (2025) con
  B y C".

### 4-24 · p. 52 · Descripción del Experimento C · IMPORTANTE
**Dice:** "…modelos entrenados exclusivamente en la era de tasas de interés
altas y auge de la inteligencia artificial…".
**Debe decir:** "…entrenados solo con 2020–2023, que incluye la pandemia,
dos años de tasas cercanas a cero, el alza de tasas y la corrección de 2022
y el inicio del auge de la inteligencia artificial en 2023".

### 4-25 · p. 52 · Descripción del Experimento B · FORMA
"el periodo alcista de 2018–2019" → "2018–2019, antes de la pandemia" (2018
cerró con caída del S&P 500).

### 4-26 · p. 52 · Faltan validaciones · CRÍTICO
**Agregar** una subsección "Validaciones adicionales" con:
- **Prueba año por año 2020–2025:** para cada año *T*, entrenar con
  [T−6, T−2], validar con T−1 y probar con T.
- **Origen rodante 2019–2024:** para el modelo de la plataforma (elegir el
  peso de mantener y comparar con y sin interacciones sin mirar 2025).
- **Prueba ciega 2026:** enero–22 de octubre, ajustes congelados.
- **Modelo de producción:** entrenado con 2018–2025.
Figura `diagramas/D09_particiones.svg`, tabla `tablas/T-03`, texto en
`textos/T04_metodologia.md` §4.

### 4-27 · p. 53 · §4.5.2 · IMPORTANTE
- Conservar las fuentes de fuga controladas: escalado ajustado con
  entrenamiento y etiqueta con `shift(1)`.
- **Quitar** "la selección de características… se calcula sobre el bloque
  de entrenamiento" (ya no hay selección).
- **Agregar:** en el protocolo final ninguna decisión (hiperparámetros,
  arquitectura, época, lookback, escalador) usa 2025; las decisiones se toman
  con 2024 y la época con 2023 (ver 4-48); el último día de cada periodo
  como única fuga residual reconocida (ver 2-11).
- El párrafo sobre las ventanas del primer día de validación es correcto
  para la Etapa 4 y queda; corregir §2.3.4 (2-11), que dice lo contrario.

---

## 4.6 Escalado de características

### 4-28 · p. 53–55 · §4.6.1–4.6.3 · CRÍTICO
**Dice:** StandardScaler para la LR, MinMaxScaler para LSTM y CNN-LSTM,
XGBoost sin escalar.
**Debe decir:** "En el protocolo final el escalador se trató como
hiperparámetro (Standard, Robust o MinMax) y Optuna eligió **RobustScaler**
(mediana y rango intercuartílico) para la LR y las tres redes; XGBoost es
invariante al escalado. El escalador se ajusta solo con el entrenamiento, por
acción en la investigación y uno global para las siete en producción (la
diferencia medida es despreciable: 0.4125 contra 0.4086 de F1 en 2025)".
Conservar StandardScaler y MinMaxScaler como opciones evaluadas.
**Por qué RobustScaler:** los retornos tienen colas pesadas (marzo de 2020);
la media y la desviación estándar se distorsionan con esos días.
**Fuente:** `ESTUDIO_TT/A_modelo/A2` §13.

### 4-29 · p. 54–55 · §4.6.4 Normalización local de OHLCV · CRÍTICO
**Acción:** eliminar la sección del método. Desde la Etapa 3 **ninguna** red
recibe los cinco canales OHLCV (las cinco usan las mismas 61 variables).
Mencionarlo solo en 6.2 (Etapa 1). Además, el ejemplo **"NVDA cotiza
alrededor de 800 USD y AAPL alrededor de 170 USD" es incorrecto**: NVIDIA
hizo un desdoblamiento 10 a 1 en junio de 2024 y los precios ajustados que
se usan están en otra escala.
**Ojo:** el paper (§4) también menciona los canales OHLCV de la CNN-LSTM;
es una frase heredada que no corresponde al código de la Etapa 3. No
repetirla (ver P-07).

---

## 4.7 Construcción de secuencias

### 4-30 · p. 55 · §4.7.1 · IMPORTANTE
**Dice:** `X[i] = features[i : i+lookback]`, `y[i] = target[i+lookback]` y
"todas las características de la ventana X[i] corresponden a días
estrictamente anteriores al día cuya etiqueta se predice".
**Acción:** la fórmula es la que usa el código, pero hay que explicar su
consecuencia: la etiqueta del día *t* describe el movimiento de *t* a *t+1*,
así que la ventana de la red termina en *t − 1* y **no incluye las
características del día *t***, que la LR y XGBoost sí ven. No es fuga (le
falta información, no le sobra), pero es una desventaja para las redes. Se
midió con la LR: quitarle el día *t* le cuesta ≈ 0.007 de F1, mucho menos que
la diferencia con las redes. Agregar además que las ventanas se construyen
sobre la serie continua y se asignan por la fecha de la etiqueta (mismas
filas para todos; figura `diagramas/D12_mismas_filas.svg`).
**Fuente:** `ESTUDIO_TT/A_modelo/A5` §7.

### 4-31 · p. 55–56 · §4.7.2 · CRÍTICO
**Dice:** "Se evalúan dos ventanas de lookback para cada modelo secuencial":
20 y 60 días.
**Debe decir:** "El tamaño de la ventana se eligió con Optuna entre 10, 20,
40 y 60 días usando solo 2024. Las configuraciones finales usan 10 días
(LSTM y CNN 1D) y 20 días (CNN-LSTM). En TT1 y en la Etapa 3 se entrenaron 20
y 60 días y se reportó la mejor **en la prueba**, lo que favorecía a las
redes; el protocolo final lo corrigió". C-12.

### 4-32 · p. 56 · §4.7.3 y Tabla 9 · CRÍTICO
**Dice:** dimensiones `(n, 20 o 60, F_Exp)` con F_Exp ∈ {3, 10, 25}, más 5
canales OHLCV para CNN-LSTM y CNN 1D; "El CNN 1D comparte las dimensiones de
entrada del CNN-LSTM por diseño… convirtiendo al CNN 1D en una ablación
directa".
**Debe decir:**

| Modelo | Entrada | Forma |
|---|---|---|
| LR, XGBoost | Vector del día | (n, 61) |
| LSTM | Ventana de 10 días | (n, 10, 61) |
| CNN 1D | Ventana de 10 días | (n, 10, 61) |
| CNN-LSTM | Ventana de 20 días | (n, 20, 61) |

(76 columnas en lugar de 61 solo en el modelo de la plataforma.) La idea de
la CNN 1D como ablación exacta de la CNN-LSTM vale para TT1; en el protocolo
final cada arquitectura se ajustó por separado, así que la comparación entre
ambas mide arquitecturas completas, no solo el bloque recurrente.

---

## 4.8 Descripción de los modelos

> Reemplazar 4.8.1–4.8.5 por las configuraciones finales (Etapa 4) y dejar
> una tabla comparativa TT1 → Etapa 3 → Etapa 4 (`tablas/T-05`).
> Borradores en `textos/T04_metodologia.md` §6.

### 4-33 · p. 56 · Introducción de 4.8 · CRÍTICO
- "El sexto es un baseline ingenuo" → "Además, se usan dos líneas base
  ingenuas" (no es un sexto modelo; el TT compara cinco).
- "Todos los modelos se entrenan de forma independiente por activo,
  produciendo un modelo distinto para cada uno de los siete activos" →
  "Cada modelo se entrena de forma global, con las siete acciones juntas
  (~10 500 filas en el Experimento B), y como comparación por acción (~1 500
  filas cada uno)". C-34.

### 4-34 · p. 57 · §4.8.1 Regresión Logística · CRÍTICO

| Aspecto | Dice (TT1) | Debe decir (protocolo final) |
|---|---|---|
| Formulación | One-vs-rest con sigmoide | **Multinomial** (softmax), coherente con §2.4.1 (C-06) |
| Regularización | L2 con C en {0.001, 0.01, 0.1, 1, 10, 100} | Optuna eligió entre L1, L2 y elasticnet, C ∈ [10⁻⁴, 10³]: **L2, C = 0.000165** |
| Escalador | StandardScaler | **RobustScaler** |
| Pesos de clase | `balanced` | `balanced` (investigación); `balanced` con mantener × 0.90 (plataforma) |
| Solver | lbfgs, 2 000 iteraciones | lbfgs en la investigación; SAGA (5 000 iteraciones) en la plataforma; mismo óptimo (problema convexo) |
| Estrategia | Por activo principal, global adicional | **Global principal**, por activo como comparación |
| Entrenamiento final | Reentrena con entrenamiento + validación | Igual (para los clásicos se mantiene) |

Agregar: 231 parámetros (3 × 76 + 3) en producción; determinista.
**Fuente:** `ESTUDIO_TT/A_modelo/A4` §1; `RO/v5/ganadores_clasicos.json`.

### 4-35 · p. 57 · §4.8.1, último párrafo · CRÍTICO
**Dice:** "La evaluación reporta métricas… calculadas sobre los primeros 90
días del conjunto de prueba… todos calculados sobre la ventana de 90 días".
**Debe decir:** "…sobre el año de prueba completo (248 días hábiles por
acción, 1 736 filas)". C-11.
Además, la lista de métricas pasa a §4.9 (las mismas para los cinco modelos).

### 4-36 · p. 57–58 · §4.8.2 XGBoost · CRÍTICO

| Aspecto | Dice (TT1) | Debe decir |
|---|---|---|
| Búsqueda | Rejilla: árboles {100…500}, profundidad {3, 4, 6}, tasa {0.01, 0.05, 0.1}, submuestreo {0.6, 0.8, 1} | **Optuna, 150 intentos, 9 hiperparámetros** (árboles 150–800, profundidad 2–10, tasa 0.005–0.3, submuestreo de filas 0.5–1 y de columnas 0.3–1, min_child_weight 1–15, gamma 0–3, reg_alpha 0–5, reg_lambda 0.1–8) |
| Ganador | — | 485 árboles, profundidad 9, tasa 0.074, submuestreo 0.97 / 0.93, min_child_weight 2, gamma 0.035, reg_alpha 1.70, reg_lambda 5.23, `hist` en GPU |
| Desbalance | "`scale_pos_weight` ajustado por clase" | **Pesos por muestra balanceados** (`sample_weight`). `scale_pos_weight` solo existe para clasificación binaria |
| Semillas | `random_state=42` | Cinco semillas (42, 1, 7, 2024, 100) con probabilidades promediadas |
| Paro temprano | — | No; el número de árboles lo fija Optuna |

**Fuente:** `ESTUDIO_TT/A_modelo/A4` §2.3.

### 4-37 · p. 58 · §4.8.3 LSTM · CRÍTICO
**Dice:** F_Exp ∈ {25, 10, 3}; dos capas de 128 unidades; "no se realiza
búsqueda de hiperparámetros, la arquitectura y los parámetros de
entrenamiento se fijan a priori"; Adam 10⁻³, weight decay 10⁻⁴, lote 64,
80 épocas, paciencia 15 sobre la pérdida.
**Debe decir:** configuración elegida por Optuna (80 intentos, 17
hiperparámetros, objetivo F1 en 2024): ventana de 10 días × 61 variables;
LSTM unidireccional de 2 capas × 118 unidades con dropout 0.43;
*pooling* por atención sobre los 10 estados; LayerNorm; dropout 0.43;
capa lineal 118 → 3; *focal loss* (γ = 1.43); AdamW (tasa 1.6 × 10⁻⁴,
weight decay 7.8 × 10⁻⁴); lote 64; ReduceLROnPlateau; recorte de gradiente
5.0; época elegida por pérdida de validación; RobustScaler; 198 480
parámetros. C-08.
**Fuente:** `ESTUDIO_TT/A_modelo/A5` §4.3.

### 4-38 · p. 59 · §4.8.4 CNN-LSTM · CRÍTICO
**Dice:** Conv1D 64 y 128 (kernel 3, BatchNorm, ReLU, dropout 0.2), dos
LSTM de 128, entrada F_Exp + 5 OHLCV, hiperparámetros fijos.
**Debe decir:** ventana de 20 días × 61; dos bloques convolucionales 61 → 77
→ 154 filtros, kernel 7, BatchNorm, ReLU, dropout 0.42 (con *padding*, la
secuencia no se acorta); LSTM unidireccional de 1 capa × 136; último estado;
LayerNorm; dropout 0.42; lineal 136 → 3; *focal loss* (γ = 2.01); AdamW (tasa
4.4 × 10⁻⁴, weight decay 0.018), sin programador de tasa; época por pérdida de
validación; 276 109 parámetros; 80 intentos de Optuna, 19 hiperparámetros.
**Fuente:** A5 §4.5.

### 4-39 · p. 59–60 · §4.8.5 CNN 1D · CRÍTICO
**Dice:** mismo bloque convolucional que la CNN-LSTM, Global Average
Pooling, Linear(128, 64), Linear(64, 3), entrada F_Exp + 5 OHLCV, "conforme
a la Tabla X de la sección 4.7.3".
**Debe decir:** ventana de 10 días × 61; dos bloques 61 → 50 → 100 filtros,
kernel 7, ReLU, dropout 0.16, sin BatchNorm; promedio global en el tiempo;
lineal 100 → 101 → ReLU → dropout → 101 → 3; *focal loss* (γ = 2.48); AdamW
(tasa 1.2 × 10⁻⁵, weight decay 0.056); época por F1 promedio de 3 épocas;
67 007 parámetros; 80 intentos, 20 hiperparámetros.
**Además:** "Tabla X" es una referencia rota → Tabla 9 (o la que
corresponda).
**Fuente:** A5 §4.4.

### 4-40 · p. 60 · §4.8.6 Baseline ingenuo · IMPORTANTE
Conservar las dos líneas base y **reportar sus valores** en los resultados:
decir siempre mantener ≈ 0.20 de F1-macro y aleatorio estratificado ≈ 0.33
(año 2025). "El baseline se calcula por activo y por experimento" → para el
resultado principal basta el valor global; por acción solo si se muestran
resultados por acción.

---

## 4.9 Métricas de evaluación

### 4-41 · p. 60 · Introducción de 4.9 · IMPORTANTE
**Dice:** "Todas las métricas se calculan por activo y por experimento, y
los resultados se reportan tanto a nivel individual como promediados sobre
los siete activos".
**Debe decir:** "Para el modelo global, las métricas se calculan sobre las
1 736 filas de prueba de las siete acciones juntas (no como promedio de los
siete valores por acción); los resultados por acción se reportan como
complemento". Importante porque el F1 sobre todas las filas y el promedio
de los F1 por acción no son la misma cantidad (el paper §8 lo menciona).

### 4-42 · p. 61 · §4.9.1 · FORMA
"Accuracy = (TP + TN)/(TP + TN + FP + FN)" es la fórmula binaria; usar la
multiclase `Σ_k TP_k / n`, igual que §2.6.1 (C-15).

### 4-43 · p. 61 · §4.9.1 · IMPORTANTE
- Agregar exactitud balanceada, kappa, AUC macro y pérdida logarítmica, y
  decir que **las ocho métricas se calculan igual para los cinco modelos y
  sobre las mismas filas** (respuesta a la sinodal). Texto en
  `textos/T03_justificaciones_sinodal.md` §2.
- El F1 ponderado no se reporta en los resultados finales: o se quita, o se
  dice que se calcula pero no se usa para decidir.

### 4-44 · p. 62 · §4.9.3 · CRÍTICO
- **Dos fórmulas** para el retorno acumulado (C-14): aquí
  `Π(1 + r_t · dirección_t) − 1` con `r_t` logarítmico (mezcla retornos
  simples y logarítmicos) y en §4.11.2 la suma de logaritmos. Dejar **una**:
  `R = Σ_t posición_t · r_{t+1}` y `R% = e^R − 1`.
- "no se consideran costos de transacción ni slippage" → "las cifras
  principales se reportan sin costos y se agrega un análisis con 5 y 10
  puntos base por cambio de posición" (S-10).
- Mover el detalle a §4.11 para no repetirlo.

### 4-45 · p. 62 · §4.9.3 · IMPORTANTE
**Dice:** "Un Sharpe Ratio mayor a 1 se considera aceptable y mayor a 2 se
considera bueno".
**Acción:** citar una fuente o quitarlo, y agregar la advertencia
relevante: con un año de datos el error estándar del Sharpe anualizado es
≈ 1 (Lo, 2002), así que un Sharpe de +0.9 en un año tiene un intervalo
aproximado de [−1.1, 2.9]. Por eso la métrica principal es la de
clasificación y las conclusiones económicas son comparativas.

### 4-46 · p. 62–63 · §4.9.4 Criterio de comparación · CRÍTICO
**Dice:** "Un modelo se considera superior a otro si su F1-Score macro es
consistentemente mayor a lo largo de los siete activos… se analiza el
desempeño por subperiodos anuales dentro del conjunto de prueba".
**Debe decir:** dos criterios separados y declarados:
1. **Comparación entre modelos:** F1-macro en la prueba 2025 del
   Experimento B, con diferencias pareadas e intervalos bootstrap; se exige
   que la dirección se repita en A y C y que no se invierta en la prueba año
   por año; las métricas económicas (Sharpe con y sin costos) son
   secundarias.
2. **Selección del modelo que se despliega:** primero se responde la
   pregunta del TT (clásicos contra redes); entre modelos que no difieren
   significativamente en varios años, se elige por parsimonia, menor
   rotación (menos costos), interpretabilidad y determinismo; la prueba
   ciega 2026 sirve de confirmación.
Texto completo: `textos/T03_justificaciones_sinodal.md` §3.
**Por qué:** es la observación de la sinodal ("¿eligen por resultados o por
desempeño?"); el documento debe declarar el criterio antes de mostrar los
resultados.

---

## 4.10 Protocolo de entrenamiento e hiperparámetros

### 4-47 · p. 63 · Introducción de 4.10 · CRÍTICO
- "Dado que se entrena un modelo independiente por cada combinación de
  activo, experimento y ventana de lookback…" → describir las 120 corridas
  (5 modelos × 3 experimentos × [1 global + 7 por acción]).
- "En todos los casos el conjunto de prueba permanece invisible durante todo
  el proceso" → **solo es cierto en la Etapa 4**. En TT1 y en la Etapa 3 el
  lookback se eligió con la prueba; en la Etapa 2 también la configuración.
  Decirlo con honestidad en el capítulo 6 (y que por eso esas cifras no son
  el resultado principal).

### 4-48 · p. 63 · §4.10.1 Búsqueda de hiperparámetros · CRÍTICO
**Dice:** búsqueda en rejilla para los clásicos y "rejilla reducida sobre
número de unidades, tasa de dropout y tasa de aprendizaje" para las redes
(contradice 4.8.3: C-08).
**Debe decir:**
- **Optuna** con el muestreador TPE (semilla 42, 25 intentos iniciales al
  azar, modo multivariado) para los cinco modelos; *MedianPruner* para las
  redes.
- Presupuesto: 150 intentos para LR y XGBoost; 80 para cada red (54, 53 y
  74 terminados; el resto podados). Hiperparámetros: 5 (LR), 9 (XGBoost),
  17–20 (redes).
- **Protocolo anidado:** en modo *dev* se entrena con 2018–2022, la época se
  elige con 2023 y la configuración con 2024; en modo *final* se entrena con
  2018–2023, la época con 2024, y 2025 se evalúa una sola vez con la
  configuración congelada. Figura `diagramas/D11_protocolo.svg`.
- Reconocer: la búsqueda es simétrica en procedimiento, no en dimensión
  (las redes buscan más hiperparámetros con menos intentos); por eso se
  afirma "una búsqueda realista no cambia el orden", no "se encontró el
  óptimo de cada red".
Tabla `tablas/T-06`; texto `textos/T04_metodologia.md` §7.

### 4-49 · p. 63 · §4.10.2 Paro temprano · CRÍTICO
**Dice:** F1 de validación, paciencia 10, máximo 100 épocas (contradice
4.8.3: pérdida, paciencia 15, 80 épocas; C-09).
**Debe decir:** "Hasta 100 épocas con paro temprano de paciencia 20 sobre el
criterio elegido por Optuna (pérdida de validación, F1 de validación o F1
promedio de tres épocas); se restauran los pesos de la mejor época. En la
Etapa 3 se usaba la pérdida de validación con paciencia 15, y el diagnóstico
mostró que restauraba la época 1 o 2 porque la pérdida de validación sube
desde el inicio; cambiar el criterio a F1 dio +0.059 a la LSTM".
- "regularización L2 sobre los pesos de las capas densas" → "*weight decay*
  de AdamW sobre todos los pesos", además de *dropout*.

### 4-50 · p. 64 · §4.10.3 Pesos de clase · IMPORTANTE
La fórmula es correcta (es `class_weight="balanced"`). Agregar: en el modelo
de la plataforma el peso de mantener se multiplica por 0.90 (pesos
efectivos: vender 1.103, mantener 0.762, comprar 1.097), elegido con origen
rodante 2019–2024 para corregir el exceso de mantener (ver 6.8). En las
redes, Optuna también podía elegir pesos "ninguno" o "raíz"; ganaron los
balanceados o fueron indiferentes.

### 4-51 · p. 64 · §4.10.4 Reproducibilidad · IMPORTANTE
- "en el backend de TensorFlow o PyTorch según corresponda" → "en PyTorch"
  (no se usó TensorFlow).
- Semillas: evaluación final con cinco semillas (42, 1, 7, 2024, 100) y
  probabilidades promediadas; Optuna con semilla 42; la LR es determinista.
- "El orden de ejecución de los tres scripts del pipeline… guía de
  reproducibilidad" → remitir al anexo de reproducibilidad (`tablas/T-16`):
  scripts por etapa, etiqueta de git `micai2026`, manifiesto de datos con
  SHA-256 (material suplementario del paper, S5) y versiones registradas.

### 4-52 · p. 64–66 · §4.11 Simulación económica · IMPORTANTE
- §4.11.1: "no se consideran costos… límite superior" → conservar como
  supuesto de las cifras principales y agregar el análisis con costos (5 y
  10 pb por cambio de posición; pasar de corto a largo paga doble).
- §4.11.2: conservar la fórmula (es la correcta) y agregar el término de
  costo: `r_neto(t) = posición_t · r_{t+1} − c · |posición_t − posición_{t−1}|`.
- §4.11.3: agregar la **rotación** (cambio medio de posición por día), que
  explica por qué los costos castigan más a XGBoost (0.65) que a la LR
  (0.38).
- **Aclarar cómo se calcula el Sharpe del modelo global:** sobre los 1 736
  retornos diarios día-acción concatenados (no es un portafolio
  equiponderado); en la Etapa 6 se reporta además el Sharpe de un portafolio
  de las siete (`scripts_opt/common.py: metricas_economicas`;
  `common_v5.py: metricas_con_costos`).
- §4.11.4: "La ausencia de costos de transacción es la limitación más
  relevante" → actualizar: ya se calcularon; las limitaciones que quedan
  son el horizonte de un día con tamaño fijo, la ejecución al cierre, la
  venta en corto sin costo de préstamo y el error estándar del Sharpe de un
  año.
