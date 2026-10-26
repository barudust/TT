# C02 — Capítulo 2: Marco teórico (p. 10–26)

> El capítulo está bien en general. Los cambios son de tres tipos:
> (1) frases que anticipan un resultado que no ocurrió ("la CNN-LSTM es la
> más viable", "la LR no se espera que gane"), (2) errores en fórmulas y
> referencias cruzadas, y (3) dos secciones nuevas que hacen falta para el
> capítulo 4: validación estadística y multicolinealidad.

## Resumen de puntos

| ID | Página | Sección | Tema | Prioridad |
|---|---|---|---|---|
| 2-01 | 10 | 2 | Número de bloques del capítulo | FORMA |
| 2-02 | 11 | 2.1.2 | "≈30 % del S&P 500" sin fuente | IMPORTANTE |
| 2-03 | 12 | 2.1.2 | "cada activo es tratado de forma independiente" | CRÍTICO |
| 2-04 | 12 | 2.1.3 | Título y primera persona | FORMA |
| 2-05 | 13 | 2.1.4 | Wilder sin referencia | IMPORTANTE |
| 2-06 | 15–16 | 2.2 | Agregar figura de la etiqueta | IMPORTANTE |
| 2-07 | 17 | 2.3.1 | "}" suelto | FORMA |
| 2-08 | 17 | 2.3.1 | "ventaja estructural" del LSTM | IMPORTANTE |
| 2-09 | 17–18 | 2.3.2 | Ventana: definición contra implementación | IMPORTANTE |
| 2-10 | 18 | 2.3.2 | "exploramos distintos W para cada activo" | IMPORTANTE |
| 2-11 | 18–19 | 2.3.4 | "se descartan las primeras W−1" | CRÍTICO |
| 2-12 | 19 | 2.4.1 | Fórmula softmax con índices mal | IMPORTANTE |
| 2-13 | 19 | 2.4.1 | Falta regularización y pesos de clase | IMPORTANTE |
| 2-14 | 19 | 2.4.1 | "su inclusión no responde a la expectativa de que alcance el mejor desempeño" | CRÍTICO |
| 2-15 | 20 | 2.4.2 | Fórmula de XGBoost | FORMA |
| 2-16 | 20 | 2.4.2 | Afirmación con cita que no la respalda | IMPORTANTE |
| 2-17 | 20–22 | 2.5.1 | Sin referencias; α como "regularización" | IMPORTANTE |
| 2-18 | 22 | 2.5.1 | "converge a un mínimo global o local" | IMPORTANTE |
| 2-19 | 22 | 2.5.1 | Pérdida: faltan pesos y focal loss | IMPORTANTE |
| 2-20 | 23 | 2.5.2 | Solo "último estado" | FORMA |
| 2-21 | 24 | 2.5.3 | *Max pooling* contra 4.8.5 | IMPORTANTE |
| 2-22 | 24–25 | 2.5.4 | "la arquitectura más viable… aportación central" | CRÍTICO |
| 2-23 | 25 | 2.6.1 | Referencia a 2.5 y "desbalance" | IMPORTANTE |
| 2-24 | 26 | 2.6.1 | Faltan kappa, AUC, exactitud balanceada, log-loss | IMPORTANTE |
| 2-25 | 26 | 2.6.2 | C ∈ ℝ³ˣ³ | FORMA |
| 2-26 | 26 | 2.6.3 | **Vender = liquidar; mantener = conservar posición** | CRÍTICO |
| 2-27 | Nuevo | 2.8 | Validación estadística | IMPORTANTE |
| 2-28 | Nuevo | 2.9 | Multicolinealidad y regularización | IMPORTANTE |

---

### 2-01 · p. 10 · Introducción del capítulo · FORMA
**Dice:** "Se organiza en seis bloques temáticos".
**Acción:** actualizar el número si se agregan 2.8 y 2.9.

### 2-02 · p. 11 · §2.1.2 · IMPORTANTE
**Dice:** "Estas empresas representan aproximadamente el 30% de la
capitalización total del índice S&P 500".
**Acción:** agregar fuente y fecha ("a finales de 2024, según…"). Usar una
fuente verificable (hoja de datos del índice o un artículo con fecha). Sin
fuente, quitar la cifra.

### 2-03 · p. 12 · §2.1.2, último párrafo · CRÍTICO
**Dice:** "Cada uno de los siete activos es tratado de forma independiente,
generando un caso por acción…".
**Debe decir:** "Se entrena un modelo global con las siete acciones y, como
comparación, un modelo por acción; los resultados también se desglosan por
acción para analizar si el desempeño varía con el perfil de cada serie".
**Por qué:** desde la Etapa 3 la estrategia principal es el modelo global
(en TT1 ya ganaba en 4 de 5 modelos, Tabla 21) y la plataforma usa uno solo.
Ver C-34.

### 2-04 · p. 12 · §2.1.3 · FORMA
- Título "Hipótesis formulada por Eugene Fama" → "Hipótesis de los mercados
  eficientes".
- "No asumimos que los mercados son eficientes…; por el contrario,
  exploramos…" → impersonal: "En este trabajo no se asume…; se evalúa si…".
- La frase "con valor predictivo estadísticamente significativo" queda bien
  **si** el capítulo 4 describe las pruebas estadísticas (hoy dice que no
  hay; ver 4-04 y C-16). Agregar al final: "La evaluación de esta hipótesis
  se describe en la sección 4.x (validación estadística)".

### 2-05 · p. 13 · §2.1.4 · IMPORTANTE
**Dice:** "El índice de fuerza relativa (RSI), desarrollado por Wilder…".
**Acción:** citar a Wilder (1978), *New Concepts in Technical Trading
Systems*. También se usa su suavizado para el ATR (§4.3.4). Ver
`correcciones/C08`.

### 2-06 · p. 15–16 · §2.2.2 · IMPORTANTE
**Acción:** agregar la figura `diagramas/D10_etiqueta.svg` (cómo se
construyen los umbrales con la ventana de 252 días y el desplazamiento de un
día). El texto y las fórmulas son correctos y coinciden con el código
(`scripts_v1/01_build_raw_dataset.py`, `api/ml/target.py`).

### 2-07 · p. 17 · §2.3.1, final del párrafo 3 · FORMA
**Dice:** "…que tratan cada observación de forma independiente.}".
**Acción:** quitar la llave "}".

### 2-08 · p. 17 · §2.3.1, párrafo 3 · IMPORTANTE
**Dice:** "…los modelos de aprendizaje profundo con memoria (en particular
el LSTM) tienen la capacidad de capturar implícitamente esta dependencia…,
lo que representa una ventaja estructural frente a los modelos de ML
clásico".
**Debe decir:** "…lo que en principio les daría una ventaja. Sin embargo,
las características de volatilidad (vol_5d a vol_60d, ATR, razones de
volatilidad) ya resumen ese agrupamiento para los modelos clásicos, por lo
que la ventaja es una hipótesis que este trabajo pone a prueba".
**Por qué:** el resultado (cap. 6) muestra que no hubo tal ventaja; el
marco teórico no debe afirmarla como hecho.

### 2-09 · p. 17–18 · §2.3.2 · IMPORTANTE
**Dice:** `X_t = [x_{t−W+1}, …, x_t]` y "la señal a predecir corresponde
estrictamente al día de cotización siguiente al último día de la ventana".
**Acción:** la definición es correcta como concepto, pero la implementación
(Etapas 1 a 4) construye la ventana `[t−W, t−1]` para la etiqueta del día *t*
(§4.7.1 del propio documento). Conservar la definición y explicar la
diferencia en la sección de construcción de secuencias (ver 4-32): las redes
no ven las características del día *t*; se midió que eso cuesta ≈ 0.007 de
F1 y no cambia la conclusión.
**Fuente:** `ESTUDIO_TT/A_modelo/A5` §7; `scripts_opt/verificar_ventana_redes.py`.

### 2-10 · p. 18 · §2.3.2, último párrafo · IMPORTANTE
**Dice:** "En este trabajo terminal exploramos distintos valores de W como
parte del proceso de ajuste de hiperparámetros, buscando el balance óptimo…
para cada uno de los siete activos".
**Debe decir:** "El tamaño de la ventana se trató como hiperparámetro: en el
protocolo final, Optuna eligió entre 10, 20, 40 y 60 días usando solo el año
de validación; las configuraciones ganadoras usan 10 días (LSTM y CNN 1D) y
20 días (CNN-LSTM)".

### 2-11 · p. 18–19 · §2.3.4, último párrafo · CRÍTICO
**Dice:** "las primeras W − 1 observaciones de cada segmento no pueden
utilizarse… estas observaciones se descartan al inicio de cada segmento".
**Debe decir:** "Las ventanas se construyen sobre la serie continua y cada
ejemplo se asigna al conjunto según la fecha de su etiqueta. Así, la ventana
del primer día de prueba incluye días del final de la validación, lo cual no
es fuga de información porque solo mira hacia atrás y el escalador se ajustó
con el entrenamiento. Con este diseño los cinco modelos se evalúan sobre
exactamente las mismas filas".
**Por qué:** es lo que hace el protocolo final; con el descarte, las redes
se evaluaban sobre 228 o 188 días y la LR sobre 248, que es precisamente la
comparación injusta que señaló la sinodal. Ver C-05.
**Agregar:** la única fuga residual reconocida: la etiqueta del último día
de cada periodo usa el cierre del primer día del siguiente (1 de ~250 días);
López de Prado recomienda purgarlo; su efecto es despreciable.

### 2-12 · p. 19 · §2.4.1, fórmula · IMPORTANTE
**Dice:** `P(y=k|x) = e^{W_k^T x + b_k} / Σ_{j=1}^{k} e^{W_k^T x + b_k}`.
**Debe decir:** `P(y=k|x) = e^{w_k^T x + b_k} / Σ_{j=1}^{K} e^{w_j^T x + b_j}`,
con *K* = 3. El denominador suma sobre *j* hasta *K* (no *k*) y usa `w_j`, `b_j`.

### 2-13 · p. 19 · §2.4.1 · IMPORTANTE
**Agregar** la función objetivo que realmente se optimiza:
`L(W) = −Σ_i w_{y_i} · log P(y_i | x_i) + (1/2C) · ‖W‖²`,
donde `w_y` es el peso de la clase y `C` el inverso de la fuerza de
regularización L2. Explicar en una línea que un `C` pequeño acerca las
probabilidades a la proporción base y que eso es lo que mejor generaliza
con poca señal (el modelo final usa C = 0.000165).
**Fuente:** `ESTUDIO_TT/A_modelo/A4` §1.2–1.5.

### 2-14 · p. 19 · §2.4.1, último párrafo · CRÍTICO
**Dice:** "la regresión logística cumple el rol de modelo baseline mínimo:
su inclusión no responde a la expectativa de que alcance el mejor
desempeño…".
**Debe decir:** "La regresión logística se incluye como referencia lineal
e interpretable. Si un modelo de aprendizaje profundo no la supera de forma
consistente, la complejidad adicional no está justificada para el problema
(criterio que se aplica en el capítulo 6)". Quitar "no responde a la
expectativa de que alcance el mejor desempeño".
**Por qué:** la LR fue el mejor modelo y el desplegado; la frase actual hace
parecer que el resultado es una sorpresa o un error. El razonamiento del
resto del párrafo es bueno y justamente justifica la elección.

### 2-15 · p. 20 · §2.4.2, fórmula · FORMA
**Dice:** `ℓ(y_t, y^{t(m−1)} + f_m(x_t))`.
**Debe decir:** `ℓ(y_t, ŷ_t^{(m−1)} + f_m(x_t))`. Para tres clases, XGBoost
produce tres puntajes por árbol (objetivo `multi:softprob`) y los pasa por
softmax; vale la pena una línea.

### 2-16 · p. 20 · §2.4.2, último párrafo · IMPORTANTE
**Dice:** "XGBoost es consistentemente el modelo de ML clásico de mayor
desempeño en problemas de clasificación sobre datos financieros tabulares
[3]".
**Acción:** la referencia [3] (López de Prado) no respalda esa afirmación.
Reformular: "XGBoost es una referencia fuerte en datos tabulares [Chen y
Guestrin, 2016; Grinsztajn et al., 2022], lo que lo convierte en el rival
más exigente dentro de los modelos clásicos".

### 2-17 · p. 20–22 · §2.5.1 · IMPORTANTE
- La subsección no tiene ninguna cita. Citar Goodfellow et al. (2016), que
  ya está en la lista como [21] y nunca se cita.
- **Dice:** "…previamente escalado por un hiperparámetro de regularización
  conocido como tasa de aprendizaje α".
  **Debe decir:** "…escalado por la tasa de aprendizaje α (el tamaño del
  paso de optimización)". La tasa de aprendizaje no regulariza; la
  regularización viene del *dropout*, el *weight decay* y el paro temprano.
- Quitar el tono promocional ("esta capacidad es vital") del párrafo 2.

### 2-18 · p. 22 · §2.5.1, último párrafo · IMPORTANTE
**Dice:** "El proceso concluye cuando la función de pérdida converge hacia un
mínimo global o local aceptable".
**Debe decir:** "En la práctica se usa un optimizador adaptativo (AdamW en
este trabajo) y el entrenamiento se detiene con paro temprano: se conserva
la época con mejor desempeño en validación". Relevante porque el diagnóstico
de la Etapa 4 mostró que la pérdida de validación sube desde la primera
época (ver `ESTUDIO_TT/A_modelo/A5` §3.4).

### 2-19 · p. 22 · §2.5.1, fórmula de pérdida · IMPORTANTE
**Agregar:** la entropía cruzada ponderada por clase y la *focal loss*
(`−(1 − p_t)^γ · log p_t`), que es la que eligió Optuna para las tres redes
del protocolo final (γ entre 1.4 y 2.5).

### 2-20 · p. 23 · §2.5.2, último párrafo · FORMA
**Dice:** "El estado oculto del último paso de tiempo h_W se conecta a una
capa densa…".
**Agregar:** "Alternativamente, los estados de todos los pasos pueden
resumirse con un promedio, un máximo o un mecanismo de atención; la LSTM
final usa atención (sección 4.x)".

### 2-21 · p. 24 · §2.5.3, párrafo 3 · IMPORTANTE
**Dice:** "…se consolidan mediante una operación de *max pooling* temporal,
la cual retiene únicamente la activación máxima de cada mapa".
**Contradice** §4.8.5 (Global Average Pooling). Ver C-07.
**Debe decir:** "…se resumen con un *pooling* global en el tiempo (promedio,
máximo o ambos), que reduce cada mapa a un valor". Las configuraciones
reales: Etapa 3, promedio + máximo; Etapa 4, promedio.
También: "lo que nos da a optar por la arquitectura híbrida" → "lo que
motiva la arquitectura híbrida".

### 2-22 · p. 24–25 · §2.5.4 · CRÍTICO
**Dice:** "Esta complementariedad hace del CNN-LSTM la arquitectura más
viable de las tres propuestas y, potencialmente, la más adecuada…" y "El
CNN-LSTM es la aportación arquitectónica central de la comparativa…
cuya explotación conjunta puede tener como resultado una mejora
estadísticamente significativa".
**Debe decir:** "Por esta complementariedad, la CNN-LSTM se planteó como la
arquitectura con mayor potencial. La hipótesis de que la explotación
conjunta de patrones locales y dependencias secuenciales produce una mejora
significativa respecto a cada arquitectura por separado y a los modelos
clásicos se evalúa en el capítulo 6".
**Por qué:** en la Etapa 4 la CNN-LSTM (0.372) no supera significativamente
a la LSTM ni a la CNN 1D y queda por debajo de la LR con significancia.

### 2-23 · p. 25 · §2.6.1 · IMPORTANTE
**Dice:** "como se discutió en la sección 2.5, la distribución de clases en
series financieras es inherentemente desbalanceada".
**Debe decir:** "como se discutió en la sección 2.2.1, con un umbral fijo la
distribución de clases es desbalanceada; el etiquetado por percentiles la
acerca a 30/40/30, pero un modelo que predice siempre mantener todavía
alcanza ≈ 40 % de exactitud".

### 2-24 · p. 26 · §2.6.1 · IMPORTANTE
**Agregar** las métricas que el trabajo reporta para los cinco modelos
(respuesta a la sinodal sobre métricas justas): exactitud balanceada, kappa
de Cohen, AUC macro uno contra todos y pérdida logarítmica. Definiciones
listas en `textos/T02_marco_teorico_nuevo.md` §1.

### 2-25 · p. 26 · §2.6.2 · FORMA
**Dice:** `C ∈ ℝ^{3×3}`.
**Debe decir:** `C ∈ ℕ^{3×3}` (son conteos).

### 2-26 · p. 26 · §2.6.3 · CRÍTICO
**Dice:** "una señal vender implica liquidar la posición o mantener
efectivo, y una señal mantener preserva la posición existente sin
modificación".
**Debe decir:** "una señal comprar abre una posición larga (+1), una señal
vender abre una posición corta (−1) y una señal mantener deja el capital
fuera del mercado (0). La posición se abre al cierre del día de la señal y
se cierra al cierre del día siguiente; el retorno de la estrategia es
`posición_t · ln(C_{t+1}/C_t)`".
**Por qué:** es lo que dicen el resumen, §2.2, §4.9.3 y §4.11, y lo que hace
el código (`scripts_opt/common.py: metricas_economicas`). Ver C-13.
**Agregar:** costos por cambio de posición y rotación (ver
`textos/T02_marco_teorico_nuevo.md` §2).

### 2-27 · Nuevo · §2.8 Validación estadística · IMPORTANTE
Hace falta la base teórica de las pruebas que usa el capítulo 6: bootstrap
por bloques (Künsch, 1989), prueba de permutación, prueba de Wilcoxon y de
signo, y el error estándar del Sharpe (Lo, 2002). Borrador en
`textos/T02_marco_teorico_nuevo.md` §3.

### 2-28 · Nuevo · §2.9 Multicolinealidad y regularización · IMPORTANTE
La definición del VIF hoy está en §4.4.2, que desaparece. Moverla aquí y
explicar por qué la multicolinealidad afecta la interpretación de los
coeficientes pero no la predicción, y por qué la penalización L2 la maneja.
Borrador en `textos/T02_marco_teorico_nuevo.md` §4.
