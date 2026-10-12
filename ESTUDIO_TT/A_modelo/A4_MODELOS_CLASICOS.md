# A4 — Modelos clásicos: Regresión Logística y XGBoost

> **Resumen.** La **Regresión Logística (LR)** combina linealmente las
> variables y las convierte en tres probabilidades; con regularización L2 muy
> fuerte (C = 0.000165) es el modelo ganador y el que está en producción.
> **XGBoost** es un conjunto de árboles de decisión entrenados uno tras otro;
> es muy competitivo (empata con la LR en el walk-forward), pero opera más y
> por eso pierde cuando hay costos. Ninguno de los dos "lee" la secuencia de
> días: miran solo la fila del día, que ya resume la historia.

---

## 1. Regresión Logística multinomial

### 1.1 Cómo funciona

Para cada clase *k* (VENDER, MANTENER, COMPRAR) calcula un puntaje lineal:

```
z_k = β_k · x + b_k          (x = las 76 variables del día, ya escaladas)
```

y los convierte en probabilidades con **softmax**:

```
p_k = e^{z_k} / (e^{z_VENDER} + e^{z_MANTENER} + e^{z_COMPRAR})
```

La señal es la clase con mayor probabilidad (*argmax*). La confianza que
muestra la plataforma es esa probabilidad máxima.

"Multinomial" = las tres clases se modelan juntas (no tres modelos
"uno contra todos").

### 1.2 Cómo aprende

Minimiza la **entropía cruzada** (qué tan baja es la probabilidad que dio a
la clase correcta), ponderada por clase, más una penalización:

```
pérdida = Σ_i w_{y_i} · (−log p_{y_i}(x_i))  +  (1/C) · ½ ‖β‖²
```

- `w_y` = peso de la clase del ejemplo (ver §1.5).
- El segundo término es la **regularización L2**: castiga coeficientes
  grandes. C es el *inverso* de su fuerza.

### 1.3 Regularización: L1, L2 y elasticnet

| Tipo | Penaliza | Efecto | Cuándo conviene |
|---|---|---|---|
| **L2 (Ridge)** | Σ β² | Encoge todos los coeficientes hacia 0, sin volverlos 0 | Cuando muchas variables aportan un poco y están correlacionadas: reparte el peso |
| **L1 (Lasso)** | Σ \|β\| | Vuelve exactamente 0 algunos coeficientes (selección de variables) | Cuando solo unas pocas importan |
| **Elasticnet** | Mezcla de las dos (`l1_ratio`) | Selecciona y reparte | Punto intermedio |

**Qué se usó:**

| Versión | Penalización | C | Escalador | Cómo se eligió |
|---|---|---|---|---|
| TT1 | L2, **one-vs-rest** (un clasificador binario por clase), lbfgs | {0.001, 0.01, 0.1, 1, 10, 100} | StandardScaler | Cuadrícula en validación; solo con 3–8 variables filtradas |
| v4 (paper §7) | Elasticnet, l1_ratio = 0.5 | 0.01, 0.1 o 1 | StandardScaler | Cuadrícula de 3 valores en validación |
| **v5 y producción** | **L2** | **0.000165** | **RobustScaler** | Optuna, 150 intentos, objetivo F1 en 2024 |

Optuna podía elegir L1, L2 o elasticnet y eligió **L2**. Con una
regularización tan fuerte, la parte L1 no agrega nada: todos los
coeficientes ya son diminutos.

### 1.4 ¿Por qué C = 0.000165 es tan pequeño y qué implica?

- C pequeño = regularización enorme (λ = 1/C ≈ 6 000).
- Lectura bayesiana: equivale a suponer de antemano que los coeficientes
  están muy cerca de 0 (un *prior* gaussiano muy concentrado) y moverse de
  ahí solo con evidencia fuerte.
- **Por qué es lo óptimo aquí:** con tan poca señal, alejarse poco de "no sé
  nada" es lo que mejor generaliza. Un modelo que reacciona a todo aprende
  ruido.
- **Consecuencia visible:** las probabilidades quedan cerca de 1/3 (la
  confianza típica está entre 0.36 y 0.45). En el 28 % de los días la señal
  se decide por menos de 2 puntos porcentuales.
- **Aun así la confianza informa:** con confianza ≤ 0.36 acierta 39 % de
  las veces; entre 0.40 y 0.45 acierta 56 %.

### 1.5 Pesos de clase

- **"balanced"**: `w_k = n / (3 · n_k)`. Con 30/40/30, MANTENER pesa 0.83 y
  COMPRAR/VENDER 1.11. Evita que el modelo aprenda "decir siempre
  MANTENER".
- **Producción (desde el 30 de septiembre):** balanced con MANTENER × 0.90.
  Pesos efectivos: VENDER 1.103, MANTENER 0.762, COMPRAR 1.097. Corrige el
  exceso de MANTENER sin cambiar la etiqueta (ver [A7 §4](A7_RESULTADOS_Y_LIMITES.md#4-el-exceso-de-mantener-y-su-ajuste)).

### 1.6 Algoritmo de optimización (solver)

- **lbfgs** en la investigación v5 cuando la penalización es L2.
- **SAGA** en producción y cuando hay L1 o elasticnet (es el único de
  scikit-learn que soporta elasticnet multinomial).
- Como el problema es convexo (un solo mínimo), ambos llegan a la misma
  solución.

### 1.7 Cuántos parámetros tiene

`3 clases × 76 variables + 3 interceptos = 231` (186 con las 61 variables
base). Frente a ~10 500–14 000 filas de entrenamiento, es un modelo
pequeño. (Como softmax no cambia si se suma lo mismo a los tres puntajes,
en rigor hay 154 grados de libertad.)

### 1.8 Ventajas y desventajas

| Ventajas | Desventajas |
|---|---|
| Entrena en segundos | Solo relaciones lineales (por eso se probaron interacciones) |
| Determinista: el mismo resultado cada vez | Necesita variables escaladas |
| Interpretable: cada coeficiente dice cuánto empuja una variable hacia cada clase | |
| Pocos parámetros: difícil que sobreajuste | |
| Opera menos (rotación 0.38): mejor con costos | |

### 1.8b ¿Por qué en el TT1 ganaba XGBoost y ahora la LR?

En TT1 la LR recibía solo 3–8 variables (filtradas con Pearson + VIF) y
XGBoost 23–25, y la estrategia principal era por acción (~1 500 filas). Al
darles las mismas 61 variables, la LR por acción en el Exp B pasó de 0.355 a
0.392 y XGBoost se quedó en 0.37; con el modelo global y la búsqueda de v5
la LR llegó a 0.404. El filtro le quitaba a la LR información que su
propia regularización sabe aprovechar. Aun así, en el walk-forward de seis
años ambos empatan (0.350 contra 0.356).

### 1.9 Por qué ganó

1. **Poca señal:** en el balance sesgo–varianza, aquí domina la varianza.
   Un modelo rígido y muy regularizado acepta un poco de sesgo y casi no
   tiene varianza.
2. **Las variables ya hacen el trabajo no lineal:** RSI, MACD, ATR o la
   distancia a la media de 200 días ya son transformaciones no lineales de
   la historia. Combinarlas linealmente captura casi toda la señal
   disponible.
3. **Pocos datos para modelos grandes:** ~10 500 filas no alcanzan para
   ajustar cientos de miles de parámetros sin aprender ruido.
4. Coincide con la literatura sobre datos tabulares (Grinsztajn et al.,
   2022) y con estudios de mercado con muestras de tamaño parecido (Patel et
   al., 2015). Donde las redes ganan (Gu, Kelly y Xiu, 2020) hay ~30 000
   acciones y 60 años.

### 1.10 El modelo en producción, paso a paso

`scripts_opt/entrenar_produccion.py`:

1. Carga las 7 acciones de 2018 a 2025 (14 063 filas).
2. Agrega las 15 interacciones.
3. Ajusta un RobustScaler con todas las filas.
4. Calcula los pesos de clase (balanced, MANTENER × 0.90).
5. Entrena `LogisticRegression(penalty="l2", C=0.000165, solver="saga",
   max_iter=5000, random_state=42)`.
6. Guarda en `api/ml/artifacts/lr_elasticnet_global_expB.pkl` el modelo, el
   escalador, la lista de variables y los metadatos (hiperparámetros, rango
   de entrenamiento, evidencia del ajuste de MANTENER).

El nombre del archivo dice "elasticnet" por historia (así se llamaba en
v4); el modelo actual es L2.

---

## 2. XGBoost

### 2.1 Cómo funciona

Un **árbol de decisión** hace preguntas del tipo "¿VIX_norm > 0.5?" y
"¿vol_ratio > 1.3?" hasta llegar a una hoja con una predicción.
**Gradient boosting** entrena cientos de árboles en secuencia: cada árbol
nuevo se ajusta para corregir los errores que dejaron los anteriores (el
gradiente de la pérdida). La predicción final es la suma de todos:

```
F(x) = Σ_m  η · árbol_m(x)          (η = tasa de aprendizaje)
```

Para 3 clases usa el objetivo `multi:softprob`: produce 3 puntajes y los
pasa por softmax.

### 2.2 Cómo se regulariza

| Mecanismo | Qué hace |
|---|---|
| `max_depth` | Limita cuántas preguntas seguidas hace un árbol |
| `min_child_weight` | Exige un mínimo de ejemplos en cada hoja |
| `gamma` | Exige una mejora mínima para hacer una división |
| `reg_alpha` / `reg_lambda` | Penalizaciones L1 / L2 sobre los valores de las hojas |
| `subsample` / `colsample_bytree` | Cada árbol ve una parte al azar de las filas / columnas |
| `learning_rate` | Pasos pequeños: cada árbol corrige poco |

### 2.3 Configuraciones

| Versión | Búsqueda | Detalles |
|---|---|---|
| TT1 | Cuadrícula: árboles {100…500}, profundidad {3, 4, 6}, tasa {0.01, 0.05, 0.1}, submuestreo {0.6, 0.8, 1} | Sin escalado, `scale_pos_weight`, 23–25 variables filtradas con SHAP |
| v4 (paper §7) | Optuna, 20–40 intentos por configuración | Pesos balanceados por muestra, varias semillas promediadas |
| **v5** | Optuna, **150 intentos**, objetivo F1 2024 | Ganador abajo |

Ganador v5: 485 árboles, profundidad 9, tasa 0.074, submuestreo de filas
0.97 y de columnas 0.93, min_child_weight 2, gamma 0.035, reg_alpha 1.70,
reg_lambda 5.23, `tree_method="hist"` en GPU, pesos balanceados por
muestra, 5 semillas promediadas. **Sin paro temprano**: el número de árboles
lo fija Optuna.

El escalador no le afecta (los árboles solo comparan valores); se dejó
StandardScaler por uniformidad.

### 2.4 Resultados

| Evaluación | XGBoost | LR |
|---|---:|---:|
| v4, Exp B, 2025 | 0.386 | 0.385 |
| v5, Exp B, 2025 | 0.359 | **0.404** |
| Walk-forward 2020–2025 (media) | **0.356** | 0.350 |
| Sharpe 2025 sin costos / con 10 pb | +0.46 / +0.01 | +0.89 / +0.62 |
| Rotación | 0.65 | 0.38 |

**Lectura:** XGBoost y la LR están prácticamente empatados en clasificación
a lo largo de 6 años. La LR gana en 2025 con significancia y, sobre todo,
gana con costos porque cambia de posición mucho menos.

### 2.5 Mejoras que se le probaron

- **Calibración isotónica (Vía 7):** F1 0.359 → 0.371, Sharpe +0.46 → +0.60.
  Es la única técnica posterior que ayudó a algún modelo. No cambia el
  ganador.
- **LightGBM** (otra implementación de boosting): F1 parecido. No aporta.
- **Mezclas con la LR:** siempre peores que la LR sola.

### 2.6 Ventajas y desventajas

| Ventajas | Desventajas |
|---|---|
| Captura relaciones no lineales e interacciones sin construirlas a mano | Muchos hiperparámetros: más formas de sobreajustar |
| Insensible a la escala y a valores extremos | 485 árboles no se interpretan a simple vista |
| Rápido en GPU (2–3 s por entrenamiento) | Más rotación → más costos |

---

## 3. ¿Por qué no Random Forest, SVM, Naive Bayes, k-NN, CatBoost?

**No se corrieron.** El TT fijó cinco modelos y ya cubren las familias
principales. Razones para no esperar cambios:

| Modelo | Razón |
|---|---|
| Random Forest | Otro conjunto de árboles (en paralelo en vez de en secuencia); en datos tabulares el boosting suele igualarlo o superarlo |
| CatBoost | Boosting de árboles; su ventaja (variables categóricas) no aplica porque todas son numéricas |
| SVM lineal | Misma frontera lineal que la LR, con otra pérdida, y sin probabilidades nativas |
| SVM con kernel | Costo entre O(n²) y O(n³) y sin probabilidades sin calibración extra |
| Naive Bayes | Supone variables independientes; aquí están muy correlacionadas |
| k-NN | Lento al predecir y se degrada con 61 dimensiones |

Nunca digas que se probaron. Sí se probó **LightGBM**.

---

## Preguntas de este tema

Están desarrolladas en [D4](../D_defensa/D4_PREGUNTAS_MODELOS.md).
