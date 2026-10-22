# A3 — Protocolo de entrenamiento, búsqueda de hiperparámetros y métricas

> **Resumen.** Los datos se separan siempre por tiempo (pasado para
> entrenar, el año siguiente para validar, el último para probar). Hay tres
> experimentos que comparten el año de prueba 2025. En la Etapa 4, toda decisión se
> toma con 2024 y 2025 se evalúa **una sola vez**. Los cinco modelos se
> ajustan con la misma herramienta (Optuna) y se evalúan sobre las mismas
> filas. Se mide con F1-macro (clasificación), kappa (acuerdo sobre el
> azar) y una simulación económica (Sharpe, drawdown, win rate, profit
> factor). La incertidumbre se mide con bootstrap por bloques, pruebas de
> permutación, prueba año por año de 6 años y una evaluación real en 2026.
>
> Código: `scripts_opt/common_v5.py` (datos, redes, entrenamiento),
> `scripts_opt/run_v5.py` (búsqueda, evaluación final, estadística),
> `scripts_opt/common.py` (métricas).

---

## 1. Por qué separar por tiempo y nunca al azar

Si se mezclan los días al azar, el modelo entrena con días de 2023 y se
evalúa con días de 2022: está "viendo el futuro". Además, días seguidos se
parecen (la volatilidad de hoy se parece a la de ayer), así que un día de
prueba tendría a su vecino en el entrenamiento. Los resultados saldrían
inflados. Por eso:

> **Entrenamiento < validación < prueba, siempre en orden cronológico.**

| Conjunto | Para qué se usa | Para qué NO |
|---|---|---|
| Entrenamiento | Que el modelo aprenda | — |
| Validación | Elegir hiperparámetros y la mejor época de las redes | Reportar resultados |
| Prueba (test) | Medir el resultado final, una vez | Tomar cualquier decisión |

---

## 2. Los tres experimentos (A, B, C)

| Experimento | Entrenamiento | Validación | Prueba | Años de entrenamiento |
|---|---|---|---|---:|
| A | 2014–2023 | 2024 | 2025 | 10 |
| **B (principal)** | **2018–2023** | **2024** | **2025** | **6** |
| C | 2020–2023 | 2024 | 2025 | 4 |

- **Por qué el mismo año de prueba en los tres:** para que la única
  diferencia sea cuántos años de historia se usan. Antes de la Etapa 3, el
  experimento A tenía otro periodo de prueba y la comparación era injusta.
- **Por qué tres:** responden "¿más historia ayuda o el mercado viejo ya
  no sirve?". Resultado: no hay una tendencia clara; la LR sale bien en los
  tres (Etapa 4: 0.406 / 0.404 / 0.401).
- **Por qué B es el principal:** 6 años es un punto medio razonable entre
  cantidad de datos y vigencia del régimen, y es el que usa producción.

Cada experimento se corre en dos modalidades: **global** (un modelo para
las 7 acciones, ~10 500 filas de entrenamiento en B) y **por acción** (7
modelos, ~1 500 filas cada uno). 5 modelos × 3 experimentos × 8
modalidades = **120 corridas** por versión.

---

### Cómo era en el TT1

| TT1 (§3.5, §3.10) | Ahora |
|---|---|
| Exp A: 2014–2021 / 2022–2023 / **2024–2025** | 2014–2023 / 2024 / 2025 |
| Estrategia principal: un modelo por acción; global como adicional | Global como principal |
| LR y XGBoost: búsqueda en cuadrícula en validación y reentrenar con entrenamiento + validación | Optuna (Etapa 4) en un año de decisión separado |
| Redes: arquitectura e hiperparámetros fijos "por costo computacional" | Optuna con 17–20 hiperparámetros (un entrenamiento tarda 7–12 s) |
| Lookback 20 o 60: el texto dice "mejor en validación", los resultados usan el mejor **en la prueba** | Etapa 4: el lookback lo elige Optuna en 2024 |
| Sin pruebas de significancia; "análisis por subperiodos" = comparar A, B y C | Bootstrap, permutación, prueba año por año, 2026 |
| Líneas base: clase mayoritaria y aleatoria estratificada | Se siguen usando como referencia |
| Métricas: F1-macro, F1 por clase, F1 ponderado, accuracy, matriz de confusión; win rate, retorno, Sharpe, drawdown, profit factor, Calmar | + kappa, AUC-ROC y balanced accuracy; costos |

---

## 3. El protocolo anidado de la Etapa 4 (cómo se evita tocar la prueba)

| Modo | Entrena | Elige la época (redes) | Elige la configuración | Evalúa |
|---|---|---|---|---|
| **dev** | 2018–2022 | 2023 | **2024** | — |
| **final** | 2018–2023 | 2024 | — (ya congelada) | **2025, una sola vez** |

**Por qué hace falta:** si con el mismo año se elige la época y la
configuración, ese año deja de ser independiente. Y si se mira 2025 para
decidir algo, 2025 deja de ser una prueba.

Otras reglas de la Etapa 4 (corrigen problemas de la Etapa 3):

1. **Ventanas alineadas:** las secuencias de las redes se construyen sobre la
   serie continua y se asignan al conjunto por la fecha de la etiqueta. Así
   los cinco modelos se evalúan sobre **las mismas 1 736 filas** de 2025
   (antes, las redes perdían los primeros 20 o 60 días de cada conjunto).
2. **El escalador se ajusta solo con entrenamiento**, por acción.
3. **Los clásicos (LR, XGBoost) se reentrenan con entrenamiento +
   validación** antes de predecir la prueba. Para las redes se probó y las
   empeoraba (−0.024 a −0.047), así que no se hace.
4. **Se replicó Etapa 3 dentro del código nuevo** antes de cambiar nada: 18 de 18
   celdas idénticas. Así se sabe que las diferencias vienen del protocolo y
   no de un error de reimplementación.

---

## 4. Búsqueda de hiperparámetros con Optuna

### 4.1 Qué es Optuna y TPE

Optuna prueba configuraciones (*trials*) y aprende de las anteriores cuáles
regiones del espacio dan mejores resultados (algoritmo **TPE**,
*Tree-structured Parzen Estimator*). Es más eficiente que probar una
cuadrícula completa (*grid search*), que crece exponencialmente con el
número de hiperparámetros, y que probar al azar.

Configuración usada: TPE con semilla 42, 25 intentos iniciales al azar,
modo multivariado. Para las redes, además, **MedianPruner**: abandona un
intento si a mitad del entrenamiento va peor que la mediana de los
anteriores.

### 4.2 Presupuesto (simétrico en procedimiento)

| Modelo | Intentos | Hiperparámetros buscados | Semillas por intento |
|---|---:|---:|---:|
| LR | 150 | 5 (penalización, C, l1_ratio, pesos de clase, escalador) | 1 (es determinista) |
| XGBoost | 150 | 9 | 1 |
| LSTM | 80 (54 terminados, el resto podados) | 17 | 2 |
| CNN 1D | 80 (53 terminados) | 20 | 2 |
| CNN-LSTM | 80 (74 terminados) | 19 | 2 |

**Objetivo de todos:** F1-macro en 2024 (modo dev).

**Lo que hay que reconocer:** la búsqueda es simétrica en *procedimiento*
(misma herramienta, mismo año de decisión), no en *dimensión*: las redes
tienen más hiperparámetros con menos intentos. Por eso la afirmación es
"una búsqueda realista no cambia el orden", no "se encontró el óptimo
global de cada red". Además, el diagnóstico mostró que ninguna
configuración de red baja la pérdida de validación del nivel del azar
([A5](A5_REDES_NEURONALES.md)), así que más intentos no prometían cambiar
nada.

### 4.3 Espacios de búsqueda

**LR:** penalización ∈ {L1, L2, elasticnet}; C ∈ [10⁻⁴, 10³] (escala
logarítmica); l1_ratio ∈ [0, 1] si elasticnet; pesos ∈ {balanced, ninguno};
escalador ∈ {Standard, Robust}.

**XGBoost:** árboles 150–800; profundidad 2–10; tasa de aprendizaje
0.005–0.3; submuestreo de filas 0.5–1 y de columnas 0.3–1;
min_child_weight 1–15; gamma 0–3; reg_alpha 0–5; reg_lambda 0.1–8.

**Redes (comunes):** criterio de época ∈ {val_loss, val_f1, val_f1_ma3};
lookback ∈ {10, 20, 40, 60}; dropout 0–0.6; tasa de aprendizaje 10⁻⁵–3·10⁻³;
weight decay 10⁻⁶–10⁻¹; lote ∈ {64, 128, 256, 512}; pesos ∈ {balanced,
ninguno, raíz}; programador ∈ {plateau, coseno, ninguno}; recorte de
gradiente ∈ {0.5, 1, 5}; escalador ∈ {MinMax, Standard, Robust}; pérdida ∈
{entropía cruzada (+ label smoothing 0–0.2), focal (γ 0.5–3)}.
**LSTM / CNN-LSTM:** unidades ocultas 16–256, capas 1–3, bidireccional sí/no,
pooling ∈ {último, media+máx, atención}. **CNN:** bloques 1–4, filtros base
16–256 (se duplican por bloque), kernel ∈ {3, 5, 7}, dilatación ∈ {1, 2},
BatchNorm sí/no, capa densa 32–256, pooling ∈ {GAP+GMP, GAP, aplanar}.
**CNN-LSTM:** filtros base 16–128 (2 bloques), kernel ∈ {3, 5, 7}.

Ganadores: ver [A4](A4_MODELOS_CLASICOS.md) y [A5](A5_REDES_NEURONALES.md).

### 4.4 Varias semillas

En la evaluación final cada modelo se entrena con **5 semillas** (42, 1, 7,
2024, 100) y se promedian las probabilidades (voto suave). Reduce la
variación por azar del entrenamiento (en las redes, ±0.02 de F1 entre
semillas). La LR es prácticamente determinista (desviación entre semillas:
0.000).

---

## 5. Validaciones adicionales (más allá de un año de prueba)

### 5.1 Prueba año por año (Etapa 4)

Para cada año de prueba *T* de 2020 a 2025: entrenar con los 5 años
`[T−6, T−2]`, validar con `T−1` y probar con `T`. La ventana es del mismo
tamaño en todos los años, así que solo cambia el año de prueba. Resultado
en [A7](A7_RESULTADOS_Y_LIMITES.md): el ranking cambia de año a año y
ningún modelo pasa de 0.394.

### 5.2 Origen rodante (septiembre)

Para cada año *Y* de 2019 a 2024: entrenar el pipeline de producción con los
6 años anteriores y predecir *Y* completo. Se usó para elegir el ajuste de
MANTENER y para comparar con y sin interacciones sin mirar 2025.

### 5.3 Evaluación en vivo 2026

El modelo final (entrenado con 2018–2025) se evalúa con datos reales de
enero a septiembre de 2026 (~1 300 días-acción). Ninguna decisión los usó.

---

## 6. Métricas de clasificación

### 6.1 F1-macro (principal)

Para cada clase *k*:

- **Precisión** = de los días en que el modelo dijo *k*, cuántos eran *k*.
- **Recall** = de los días que eran *k*, cuántos detectó.
- **F1_k** = `2 · precisión · recall / (precisión + recall)`.

**F1-macro** = promedio simple de F1_VENDER, F1_MANTENER y F1_COMPRAR.

**Por qué macro y no ponderado:** el ponderado premia acertar MANTENER (la
clase más frecuente), que no genera ganancia; el macro trata a las tres
clases igual.

**Valores de referencia** (para 2025, con 42 % MANTENER real):

| Estrategia trivial | F1-macro |
|---|---:|
| Decir siempre MANTENER | ≈ 0.20 |
| Al azar con las proporciones reales | ≈ 0.33 |
| LR (Etapa 4) | 0.404 |

### 6.2 Por qué no accuracy

Decir siempre MANTENER da ~42 % de exactitud sin aprender nada. El F1-macro
lo detecta (F1 de COMPRAR y VENDER = 0). Los colapsos sí ocurrieron en
algunas redes: en la Etapa 4, la CNN y la CNN-LSTM del experimento A no predijeron
ni un MANTENER (F1 0.26 y 0.24), y en la Etapa 3 la CNN-LSTM del experimento C
predecía COMPRAR solo el 4.9 % de los días.

### 6.3 Kappa de Cohen

`κ = (p_o − p_e) / (1 − p_e)`, donde `p_o` es la exactitud y `p_e` la
exactitud que se esperaría por azar con las proporciones de lo real y de lo
predicho. 0 = azar, 1 = perfecto; menos de 0.20 es "acuerdo leve" (Landis y
Koch, 1977).

**Por qué se agregó (septiembre):** a diferencia del F1, sí es comparable
entre etiquetas con distinta proporción de clases (30/70 contra 40/60) y
dice directamente cuánto por encima del azar se está: 0.14 en 2025 y 0.035
en 2026.

Ejemplo de cálculo (2025): `p_o = 0.453`;
`p_e = 0.297·0.270 + 0.420·0.570 + 0.283·0.160 = 0.365`;
`κ = (0.453 − 0.365) / (1 − 0.365) = 0.14`.

---

## 7. Simulación económica (backtest)

### 7.1 La regla

- Al cierre del día *t* el modelo da la señal.
- COMPRAR → posición +1; VENDER → −1; MANTENER → 0.
- La posición se abre al cierre de *t* y se cierra al cierre de *t+1*.
- Retorno de la estrategia: `r_strat(t) = posición(t) · ln(C_{t+1}/C_t)`.
- Sin costos ni deslizamiento en las cifras principales.

### 7.2 Métricas

| Métrica | Fórmula | Cómo leerla |
|---|---|---|
| **Sharpe anualizado** | `√252 · media(r_strat) / desv(r_strat)` | Ganancia por unidad de riesgo. >0 gana; >1 bueno |
| **Win rate** | días con `r_strat > 0` / días con posición | 50 % ≈ azar |
| **Profit factor** | Σ ganancias / \|Σ pérdidas\| | >1 gana |
| **Máximo drawdown** | `mín (capital_t − pico_t) / pico_t` | La peor caída desde un máximo |

### 7.3 Por qué medir en dinero además de F1

Un modelo puede tener buen F1 acertando días con movimientos pequeños y
perder dinero en los grandes, o al revés. El TT reporta ambos tipos de
métrica.

### 7.4 Costos de transacción (Etapa 4)

Se descuentan 5 o 10 pb por cada **cambio de posición** (pasar de corto a
largo cuenta doble). La **rotación** (cambio medio de posición por día) de
la LR es 0.38 y la de XGBoost 0.65, por eso los costos castigan más a
XGBoost:

| Modelo (Exp B, 2025) | Sharpe sin costos | 5 pb | 10 pb |
|---|---:|---:|---:|
| LR | +0.89 | +0.76 | +0.62 |
| XGBoost | +0.46 | +0.23 | +0.01 |

### 7.5 Limitación del Sharpe de un año

Con un año de datos, el error estándar del Sharpe anualizado es ≈ 1
(Lo, 2002). Un Sharpe de +0.9 en un año tiene un intervalo de ~[−1.1, 2.9].
Por eso las conclusiones económicas son comparativas y la métrica
principal es la de clasificación.

---

## 8. Cómo se prueba que no es suerte

| Prueba | Qué hace | Resultado clave |
|---|---|---|
| **Bootstrap por bloques** | Remuestrea 2 000 veces bloques de 20 días consecutivos del año de prueba; los percentiles 2.5 y 97.5 dan el intervalo. Bloques (no días sueltos) para respetar que los días están correlacionados | LR 2025: [0.379, 0.428]; supera a las otras cuatro (las diferencias pareadas excluyen el cero) |
| **Permutación** | Baraja 500 veces las señales del modelo entre días (misma cantidad de cada señal, sin relación con lo que pasó) | 2025: solo 0.4 % de las permutaciones supera al modelo. 2024: el 79 % lo supera |
| **Prueba año por año** | 6 años de prueba | Ningún modelo pasa de 0.394; LR y XGBoost ≈ 0.35 |
| **Prueba de signo / Wilcoxon** | Compara pares (global contra por acción en la misma acción y experimento) | Global gana en LR 18 de 21, p = 0.002 |
| **2026 en vivo** | Año no usado para nada | F1 0.354, κ 0.035 |

**Lectura honesta:** hay señal, es débil y depende del año.

---

## 9. Fuga de información: todas las protecciones

1. Variables calculadas solo con datos hasta el cierre del día.
2. Umbrales de la etiqueta con `shift(1)` (solo días anteriores).
3. Escalador ajustado solo con entrenamiento.
4. Pesos de clase calculados con entrenamiento.
5. Separación cronológica estricta.
6. En la Etapa 4, ninguna decisión mira 2025.
7. En la plataforma, se descarta la vela del día mientras el mercado está
   abierto (su "cierre" sería un precio intermedio).

**Lo único que falta en rigor:** la etiqueta del último día de cada periodo
usa el cierre del primer día del siguiente. López de Prado recomienda
"purgar" ese día. Es 1 de ~250 días por corte y no revela etiquetas de
prueba; el efecto es despreciable, pero si lo preguntan, se reconoce.

---

## Preguntas de este tema

Están desarrolladas en [D5](../D_defensa/D5_PREGUNTAS_ESTADISTICA.md).
