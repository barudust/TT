# A5 — Redes neuronales: LSTM, CNN 1D y CNN-LSTM

> **Resumen.** Las tres redes leen una **ventana** de los últimos días (10 a
> 60) con las 61 variables de cada día. La LSTM la lee día por día con
> memoria; la CNN busca patrones locales con filtros; la CNN-LSTM hace
> primero lo de la CNN y luego lo de la LSTM. Se diseñaron en dos etapas:
> en la Etapa 3 (paper) con arquitecturas fijas y una búsqueda pequeña, y en la Etapa 4 con
> Optuna buscando 17–20 hiperparámetros, incluido el número de capas. Las
> ganadoras de la Etapa 4 tienen 2 capas LSTM (LSTM), 2 bloques convolucionales
> (CNN) y 2 bloques convolucionales + 1 capa LSTM (CNN-LSTM). **Ninguna
> configuración logró bajar la pérdida de validación del nivel del azar**:
> el límite no es el diseño de la red sino la poca señal y que las variables
> ya resumen la historia.
>
> Código: `scripts_opt/common_v5.py` (clases `LSTMNet`, `CNNNet`,
> `CNNLSTMNet`, función `entrenar`), `scripts_opt/run_v5.py` (búsqueda),
> `scripts_opt/train_all_v4.py` (versión del paper). Framework: PyTorch.

---

## 1. Por qué estas tres redes

El TT1 planteaba como pregunta si el aprendizaje profundo superaría a los
modelos clásicos (con la hipótesis de mercado eficiente como hipótesis nula
implícita). Se eligieron tres familias que
cubren las formas típicas de procesar una serie de tiempo:

| Red | Idea | Qué podría captar que la LR no |
|---|---|---|
| **LSTM** | Recurrente con memoria | Dependencias temporales: "el RSI lleva 5 días subiendo" es distinto de "subió hoy" |
| **CNN 1D** | Filtros que se deslizan en el tiempo | Patrones locales de 3–7 días en cualquier parte de la ventana |
| **CNN-LSTM** | Convoluciones y luego LSTM | Patrones locales y su orden en el tiempo |

Las tres son estándar en la literatura de predicción financiera (Fischer y
Krauss 2018 usan LSTM; Sezer et al. 2020 revisan CNN e híbridos).

---

## 2. Qué recibe cada red

- **Entrada:** un tensor `(lote, lookback, 61)` = para cada ejemplo, los
  últimos `lookback` días con sus 61 variables escaladas.
- **Salida:** 3 puntajes (*logits*) → softmax → probabilidades de VENDER,
  MANTENER y COMPRAR.
- **Escalado:** MinMaxScaler en la Etapa 3; RobustScaler (elegido por Optuna) en la Etapa 4,
  ajustado solo con entrenamiento y por acción.
- **Ejemplos de entrenamiento (Exp B global):** ~10 400 ventanas.

---

## 3. Primera etapa: las redes del paper (Etapa 3)

### 3.1 Arquitecturas

**LSTM bidireccional (592 131 parámetros):**

```
entrada (lookback × 61)
 → LSTM bidireccional, 128 unidades por dirección, 2 capas, dropout 0.3
 → último estado oculto (256)
 → LayerNorm → Dropout 0.3
 → Lineal 256 → 3
```

**CNN 1D (160 835 parámetros):**

```
entrada (61 canales × lookback)
 → [Conv1d 64 filtros, kernel 3 → BatchNorm → ReLU → Dropout 0.3]
 → [Conv1d 128, kernel 3 → BatchNorm → ReLU → Dropout 0.3]
 → [Conv1d 192, kernel 3 → BatchNorm → ReLU → Dropout 0.3]
 → promedio global + máximo global (384)
 → Lineal 384 → 128 → ReLU → Dropout → Lineal 128 → 3
```

**CNN-LSTM (301 699 parámetros):**

```
entrada
 → [Conv1d 64, k 3 → BN → ReLU → Dropout] → [Conv1d 128, k 3 → BN → ReLU → Dropout]
 → LSTM unidireccional, 128 unidades, 2 capas
 → último estado → LayerNorm → Dropout → Lineal 128 → 3
```

### 3.2 Entrenamiento

AdamW (tasa 10⁻³, weight decay 10⁻⁴), lote 128, hasta 80 épocas, paro
temprano con paciencia 15 sobre la **pérdida de validación**, reducción de
la tasa al estancarse (*ReduceLROnPlateau*), recorte de gradiente 1.0,
entropía cruzada con pesos balanceados, 3 semillas. Lookback 20 y 60. La
búsqueda de arquitectura fue una cuadrícula chica: unidades ∈ {128, 192},
capas ∈ {2, 3}, dropout ∈ {0.3, 0.4}.

### 3.3 Por qué se eligió así

- **2 capas:** la primera capta patrones de corto plazo y la segunda los
  combina; más capas en una red recurrente con ~10 000 ejemplos aumentan el
  riesgo de sobreajuste.
- **Bidireccional:** dentro de una ventana ya cerrada (todo es pasado), leer
  en ambos sentidos es válido y suele ayudar a resumir la secuencia.
- **LayerNorm y dropout:** estabilizan y regularizan.
- **Filtros 64→128→192 con kernel 3:** patrón clásico de CNN (más filtros
  conforme se sube de nivel); kernel 3 = patrones de 3 días; apilar 3 capas
  amplía el campo de visión a ~7 días.
- **Promedio + máximo global:** resume la secuencia sin depender de la
  posición exacta del patrón.

### 3.4 Lo que el diagnóstico encontró (14 de agosto)

Al revisar por qué las redes rendían menos, se midió todo
(`docs/DIAGNOSTICO_MODELOS_PROFUNDOS.md`):

| Hallazgo | Consecuencia |
|---|---|
| Un entrenamiento tarda 7–12 s en GPU | El cómputo no era la limitante; se podían hacer cientos de intentos |
| Con paro temprano por pérdida de validación, **se restauraba la época 1 o 2**: la pérdida de validación sube desde el inicio | Las redes del paper estaban entrenadas ~1 época útil |
| **La pérdida de validación nunca baja de ln 3 ≈ 1.0986** (el azar) | No extraen nada generalizable |
| **Achicar la LSTM de 592 131 a 10 275 parámetros da lo mismo** | No es problema de tamaño ni de regularización |
| En validación (2024), LR, LSTM y XGBoost quedan dentro de 0.02 | Las diferencias de la Etapa 3 podían ser ruido de un año |
| El lookback de las redes en la Etapa 3 se eligió con el F1 de **prueba** | Error de protocolo que favorecía a las redes |
| Los clásicos se reentrenaban con entrenamiento + validación; las redes no | Asimetría |
| Las redes se evaluaban sobre menos filas (perdían los primeros días) | Comparación no estricta |

Todo esto motivó el protocolo de la Etapa 4.

---

## 4. Segunda etapa: las redes de la Etapa 4 (Optuna)

### 4.1 Antes de buscar: el torneo de decisiones de protocolo (paso 4.2)

Se probaron 6 decisiones, una por una, por arquitectura (en modo dev):

| Decisión | Resultado |
|---|---|
| Criterio para elegir la época: pérdida, F1 o F1 promedio de 3 épocas | **F1 de validación vale +0.059 a la LSTM**; sin efecto en CNN y CNN-LSTM. Es la mayor mejora individual de las redes |
| Ventanas alineadas (mismas filas para todos) | Se adopta por diseño para comparar justo |
| Escalador (MinMax, Standard, Robust) | Sin efecto claro (después Optuna eligió Robust) |
| Pesos de clase (balanced, ninguno, raíz) | Sin efecto |
| Pooling (último, media+máx, atención) | Sin efecto claro |
| Reentrenar con entrenamiento + validación | **Empeora** a las tres redes (−0.024 a −0.047) |

### 4.2 Qué podía elegir Optuna

Número de capas (1–3), unidades (16–256), bidireccional sí/no, pooling,
número de bloques convolucionales (1–4), filtros, kernel (3/5/7),
dilatación, BatchNorm, tamaño de la capa densa, lookback (10/20/40/60),
dropout, tasa de aprendizaje, weight decay, lote, pesos de clase,
programador de la tasa, recorte de gradiente, escalador, función de pérdida
(entropía cruzada con *label smoothing* o *focal loss*) y criterio de
época. 80 intentos por red, 2 semillas por intento, objetivo F1 en 2024.

### 4.3 LSTM ganadora (198 480 parámetros)

```
entrada (10 días × 61 variables)
 → LSTM unidireccional, 118 unidades, 2 capas apiladas, dropout 0.43 entre capas
 → pooling por atención: una capa Lineal(118 → 1) da un peso a cada día,
   softmax sobre los 10 días, suma ponderada de los estados (118)
 → LayerNorm(118) → Dropout 0.43
 → Lineal 118 → 3
```

| Hiperparámetro | Valor | Qué significa |
|---|---|---|
| Lookback | 10 días | Ventana corta: más historia no ayudó |
| Capas | 2 | Optuna podía elegir 1–3 |
| Unidades | 118 | Tamaño de la memoria |
| Bidireccional | **No** | (En la Etapa 3 sí lo era) |
| Pooling | Atención | Decide qué días de la ventana pesan más |
| Dropout | 0.43 | Regularización fuerte |
| Pérdida | Focal, γ = 1.43 | Menos peso a ejemplos fáciles |
| Optimizador | AdamW, tasa 1.6·10⁻⁴, weight decay 7.8·10⁻⁴ | |
| Lote / programador / recorte | 64 / plateau / 5.0 | |
| Criterio de época | Pérdida de validación | |
| Escalador | Robust | |
| F1 en 2024 (dev) | 0.362 ± 0.005 | |

### 4.4 CNN 1D ganadora (67 007 parámetros)

```
entrada (61 canales × 10 días)
 → Conv1d 61 → 50 filtros, kernel 7 → ReLU → Dropout 0.16
 → Conv1d 50 → 100 filtros, kernel 7 → ReLU → Dropout 0.16
 → promedio global en el tiempo (100)
 → Lineal 100 → 101 → ReLU → Dropout 0.16 → Lineal 101 → 3
```

| Hiperparámetro | Valor |
|---|---|
| Bloques convolucionales | 2 (podía 1–4) |
| Filtros | 50 → 100 |
| Kernel | 7 días |
| BatchNorm | No |
| Pooling | Promedio global |
| Capa densa | 101 |
| Pérdida | Focal, γ = 2.48 |
| Tasa / weight decay | 1.2·10⁻⁵ / 0.056 |
| Criterio de época | F1 promedio de 3 épocas |
| Lookback / escalador | 10 / Robust |
| F1 en 2024 (dev) | 0.344 ± 0.022 |

### 4.5 CNN-LSTM ganadora (276 109 parámetros)

```
entrada (20 días × 61 variables)
 → Conv1d 61 → 77, kernel 7 → BatchNorm → ReLU → Dropout 0.42
 → Conv1d 77 → 154, kernel 7 → BatchNorm → ReLU → Dropout 0.42
 → LSTM unidireccional, 136 unidades, 1 capa (lee la secuencia de 20 pasos × 154)
 → último estado (136) → LayerNorm → Dropout 0.42 → Lineal 136 → 3
```

| Hiperparámetro | Valor |
|---|---|
| Lookback | 20 días |
| Bloques convolucionales | 2 (77 → 154 filtros, kernel 7, con BatchNorm) |
| LSTM | 1 capa, 136 unidades, unidireccional |
| Pooling | Último estado |
| Pérdida | Focal, γ = 2.01 |
| Tasa / weight decay | 4.4·10⁻⁴ / 0.018, sin programador |
| Criterio de época | Pérdida de validación |
| F1 en 2024 (dev) | 0.352 ± 0.014 |

Las convoluciones usan *padding* para que la secuencia no se acorte: la
LSTM recibe los 20 pasos.

### 4.6 Detalles comunes de entrenamiento (Etapa 4)

- Hasta 100 épocas, paro temprano con paciencia 20 sobre el criterio
  elegido; se restaura la mejor época.
- AdamW, recorte de gradiente, pesos de clase balanceados.
- Evaluación final con **5 semillas** y voto suave (promedio de
  probabilidades).
- Sin reentrenar con validación (las empeoraba).

### 4.7 ¿Por qué estos números de capas?

**Respuesta para la defensa:** no se fijaron a mano en la Etapa 4; Optuna podía
elegir entre 1 y 3 capas LSTM y entre 1 y 4 bloques convolucionales, y
eligió 2 en la LSTM, 2 en la CNN y 2+1 en la CNN-LSTM. La razón de fondo:
con ~10 000 ejemplos y poca señal, más capas solo agregan parámetros que
aprenden ruido; y el diagnóstico mostró que una LSTM de una sola capa con
16 unidades (10 275 parámetros) rinde igual que una de 592 131. El tamaño no
es lo que limita.

---

## 5. Resultados

| Red | Etapa 3, Exp B, 2025 (mejor lookback) | Etapa 4, Exp B, 2025 | Intervalo 95 % Etapa 4 | Sharpe Etapa 4 | Prueba año por año 2020–2025 |
|---|---:|---:|---|---:|---:|
| LSTM | 0.370 | 0.369 | [0.341, 0.395] | −0.35 | 0.314 |
| CNN 1D | 0.343 | 0.359 | [0.332, 0.386] | −0.46 | 0.292 |
| CNN-LSTM | 0.384 | 0.372 | [0.346, 0.395] | −0.07 | 0.328 |
| *(LR, referencia)* | *0.385* | *0.404* | *[0.379, 0.428]* | *+0.89* | *0.350* |

- Las tres redes quedan por debajo de la LR en 2025 con significancia, y
  entre ellas no hay diferencia significativa.
- Las tres tienen **Sharpe negativo** en la Etapa 4 (pierden dinero en la
  simulación) y en la prueba año por año.
- En el paper (Etapa 3) la CNN-LSTM parecía casi empatar con la LR, pero ese
  resultado tenía el lookback elegido mirando la prueba.

---

## 6. Por qué no ganaron (la explicación completa)

1. **No aprenden nada generalizable con esta entrada.** La pérdida de
   validación de un modelo que dice 1/3 a cada clase es `ln 3 ≈ 1.0986`; la
   de uno que solo conoce las proporciones 30/40/30 es 1.089. Las redes se
   quedan en ~1.09–1.10 con cualquier configuración. Todo lo que aprenden
   después de la primera época es ruido del entrenamiento (su F1 en
   entrenamiento sube a 0.45 mientras el de validación oscila 0.16–0.36).
2. **Las variables ya son resúmenes de la historia.** `ret_10d`, `mom_60d`,
   `dist_ma200`, el RSI… ya condensan varios días. Darle a la red 10 o 60
   días de esos resúmenes le entrega información redundante, no nueva.
3. **Pocos datos para su tamaño.** 67 000–276 000 parámetros contra ~10 400
   ejemplos ruidosos.
4. **La etiqueta de 1 día es casi ruido.** La dirección del día siguiente es
   casi impredecible con datos públicos (eficiencia débil del mercado).

**Cuándo podrían ganar:** con muchos más datos (cientos de acciones,
décadas), con entradas crudas (precios minuto a minuto o el libro de
órdenes, donde la red tiene que aprender las variables) o con horizontes
más largos. Ninguna de esas condiciones se cumple aquí. Es lo mismo que
dice la literatura: Gu, Kelly y Xiu (2020) obtienen ventaja de las redes con
~30 000 acciones y 60 años.

---

## 7. Una asimetría que hay que conocer: la ventana termina un día antes

**Hallazgo del 2026-10-12** (no estaba en ningún documento anterior).

En la Etapa 3 (`train_all_v4.seq`) y en la Etapa 4 (`common_v5._ventanas`), para la fila
*i* la ventana es `Z[i − lookback : i]`, es decir, los días
`i − lookback, …, i − 1`, y la etiqueta es la de la fila *i*, que describe el
movimiento de `C_i` a `C_{i+1}`. Por lo tanto:

- **Las redes predicen el movimiento de *t* a *t+1* sin ver las variables
  del día *t*** (el último cierre disponible).
- La LR y XGBoost **sí** ven el día *t*.

No es fuga de información (a las redes les falta un día, no les sobra
información futura), pero sí es una desventaja para las redes que ningún
documento menciona.

**Cuánto pesa.** Se midió con la LR: entrenada con las variables del día
*t − 1* en lugar de las del día *t*, su F1 en 2025 baja de 0.393 a 0.386
(**−0.007**) (`scripts_opt/verificar_ventana_redes.py`). La brecha entre la
LR y las redes en la Etapa 4 es de 0.032 a 0.045; en la prueba año por año, de 0.02 a
0.06. Y las redes no superan el azar en su pérdida de validación con
ninguna configuración. Por eso la asimetría **no cambia la conclusión**,
pero debe reconocerse.

**Cómo responder si te lo señalan:** "Es correcto, la ventana de las redes
termina en *t − 1*. Lo medimos: a la regresión logística, quitarle el día
*t* le cuesta 0.007 de F1, mucho menos que la diferencia con las redes, y
el diagnóstico muestra que su pérdida de validación no baja del azar. La
corrección sería construir la ventana `[i − lookback + 1, i]`; esperamos un
efecto pequeño."

---

## 8. Todo lo que se probó con las redes

| Qué | Dónde | Resultado |
|---|---|---|
| Lookback 10, 20, 40, 60 | Etapa 3, Etapa 4 | Corto (10–20) es igual o mejor |
| 1–3 capas LSTM, 16–256 unidades | Etapa 3 (cuadrícula), Etapa 4 (Optuna), diagnóstico | Sin efecto real; ganan 1–2 capas |
| Bidireccional | Etapa 3, Etapa 4 | Etapa 3 sí; Optuna eligió no |
| Pooling: último, media+máx, atención | paso 4.2, Etapa 4 | Atención para la LSTM; sin efecto claro |
| 1–4 bloques convolucionales, kernel 3/5/7, dilatación | Etapa 4 | Ganan 2 bloques con kernel 7 |
| BatchNorm | Etapa 3, Etapa 4 | La CNN prefirió sin; la CNN-LSTM con |
| Entropía cruzada, *label smoothing*, *focal loss* | Etapa 4 | Optuna eligió focal en las tres |
| Pesos de clase balanceados / ninguno / raíz | paso 4.2, Etapa 4 | Sin efecto |
| Criterio de época (pérdida, F1, F1 promedio) | paso 4.2, Etapa 4 | F1 ayuda a la LSTM (+0.059) |
| Reentrenar con entrenamiento + validación | paso 4.2 | Empeora |
| Tamaño mínimo (10 275 parámetros) | Diagnóstico | Igual que el grande |
| Variables extra de mercado (dataset Etapa 4, 93 variables) | Etapa 4 | No ayuda |
| SWA (promedio de pesos de las últimas épocas) | Etapa 5 | Mejora el Sharpe de la LSTM, no su F1; nada en CNN |
| Calibración isotónica | Etapa 5 | Baja el F1 de las redes (−0.06) |
| Mezclas con LR y XGBoost | Etapa 2, Etapa 5 | Peores que la LR sola |

**No se probaron:** GRU, Transformer, TCN, TabNet. Razón: el diagnóstico
mostró que el límite viene de la señal en los datos, no de la arquitectura
(redes muy distintas y de tamaños muy distintos llegan a la misma pérdida);
además, un Transformer necesita muchos más datos o pre-entrenamiento.

---

## 9. Cómo eran las redes en el reporte de TT1

El TT1 (18 de mayo, §3.8) fijó las arquitecturas **a priori, sin búsqueda
de hiperparámetros**, "por costo computacional":

| Red | Diseño en TT1 |
|---|---|
| LSTM | **Unidireccional**, 2 capas × 128, dropout 0.3, LayerNorm, Linear(128, 3); Adam 10⁻³, weight decay 10⁻⁴, lote 64, hasta 80 épocas, paciencia 15 sobre la pérdida de validación, ReduceLROnPlateau, recorte de gradiente 1.0 |
| CNN-LSTM | Conv1D 64 → 128 (kernel 3, BatchNorm, ReLU, dropout 0.2) → LSTM 2 × 128 → LayerNorm → Linear(128, 3). Entrada: variables filtradas + **5 canales OHLCV normalizados por ventana** (precios ÷ cierre del primer día, volumen ÷ máximo de la ventana) |
| CNN 1D | **Diseñada como ablación de la CNN-LSTM**: el mismo bloque convolucional y la misma entrada, pero promedio global + Linear(128, 64) + ReLU + LayerNorm + Dropout + Linear(64, 3). Así la diferencia entre ambas mide el aporte del bloque recurrente |
| Entrada | Solo las variables que pasaron un filtro de Spearman (25 / 10 / 3 en A / B / C) |
| Estrategia | Un modelo por acción (principal) y uno global (adicional); lookback 20 y 60 |

**Qué cambió y por qué:**

1. **Mismas variables para todos** (las 61, sin canales OHLCV): el TT1 mismo
   concluyó que la diferencia en número de variables impedía comparar
   arquitecturas (§5.6). Con la Exp C, la LSTM tenía 3 variables contra 25 de
   XGBoost.
2. **Etapa 3:** LSTM bidireccional (2 × 128), CNN de 3 bloques (64 → 128 → 192),
   AdamW, lote 128; seguía sin búsqueda.
3. **Etapa 4:** Optuna eligió capas, tamaños, ventana, pérdida y pooling
   (§4). El diagnóstico mostró que un entrenamiento tarda 7–12 s, así que el
   "costo computacional" que justificaba fijar las arquitecturas no era real.
4. **Resultado:** las redes siguen debajo de los clásicos, ahora sin la
   excusa de tener menos variables ni hiperparámetros fijos.

La idea de la CNN 1D como ablación sigue siendo útil para explicar: en
TT1, la CNN-LSTM superaba a la CNN 1D por 0.012–0.025 de F1; en la Etapa 4 sus
intervalos se traslapan (0.372 contra 0.359), así que el bloque recurrente
no aporta una diferencia significativa.

Ver [D1](../D_defensa/D1_TT1_VS_TT2.md).

---

## Preguntas de este tema

Están desarrolladas en [D4](../D_defensa/D4_PREGUNTAS_MODELOS.md).
