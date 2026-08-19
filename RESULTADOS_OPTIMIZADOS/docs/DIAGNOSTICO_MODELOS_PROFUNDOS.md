# Diagnóstico: qué está pasando realmente con los modelos profundos

> **Fecha: 2026-08-14.** Documento de evidencia. Todo lo que sigue está medido en
> esta máquina (RTX 5060 Ti, torch 2.12+cu128, optuna 4.8, sklearn 1.7.2,
> xgboost 3.2.0) o verificado leyendo el código. Reproducible con:
>
> ```bash
> python scripts_opt/diag_deep.py
> ```
>
> Tarda 2.2 min y deja las cifras crudas en `docs/diag_deep_resultados.json`.
> Con semilla fija reproduce **exactamente** (verificado corriendo dos veces).
> Ninguna medición de este documento toca el conjunto de test: todas las cifras
> propias son de train/validación. Las cifras de test que se citan salen de
> `RESULTADOS_OPTIMIZADOS/v4/resultados_v4.csv`, que ya existía.

El plan previo (`PLAN_OPTUNA_DEEP_MODELS.md`) daba por hecho que el problema era
"poca búsqueda de hiperparámetros" y que el obstáculo era el tiempo de GPU. Las
mediciones dicen que **las dos premisas son falsas**. Este documento las sustituye.

---

## Resumen en cinco hallazgos

| # | Hallazgo | Consecuencia |
|---|---|---|
| H1 | Un entrenamiento profundo completo tarda **7–12 s**, no minutos | El cómputo no es una restricción; caben miles de trials |
| H2 | El early stopping por `val_loss` **restaura la época 1–2**: los modelos del paper están entrenados ~1 época útil | La comparación del paper no mide "LSTM bien entrenado vs LR" |
| H3 | La `val_loss` **nunca baja de forma apreciable de ln(3)=1.0986** en ninguna configuración probada | Los modelos profundos no extraen nada generalizable de esta representación |
| H4 | En **validación**, LR (0.356), LSTM (0.357) y XGBoost (0.374) están dentro de 0.02 | El orden del paper aparece solo en test y podría ser ruido de un único año |
| H5 | El lookback "mejor" se eligió con **F1 de test**, no de validación (`consolidar_v4.py:35`) | Contradice lo que dice `paper.tex` y sesga al alza a los modelos profundos |

---

## H1 — El cómputo no es el cuello de botella

Medido sobre GLOBAL, Exp B, con la configuración exacta de `train_all_v4.py`
(80 épocas máx., paciencia 15, batch 128, AdamW lr=1e-3, `ReduceLROnPlateau`):

| Modelo | lookback | Parámetros | s/época | Épocas hasta parar | **Segundos por entrenamiento** |
|---|---:|---:|---:|---:|---:|
| LSTM (bi) | 20 | 592 131 | 0.51 | 16 | **10.0** |
| CNN 1D | 20 | 160 835 | 0.45 | 16 | **7.2** |
| CNN-LSTM | 20 | 301 699 | 0.48 | 17 | **8.2** |
| LSTM (bi) | 60 | 592 131 | 0.71 | 17 | **12.1** |
| LSTM per-ticker (AAPL) | 20 | 592 131 | 0.073 | 21 | **1.5** |

Tamaños: GLOBAL Exp B lb=20 → train (10 423, 20, 61), val (1 624, …), test
(1 596, …). Preparar los datos tarda 0.2 s.

Referencias de los modelos clásicos sobre los mismos datos: **XGBoost 2.0–2.5 s
por fit** (GPU 2.5 s, CPU 1.9 s — a este tamaño la GPU no ayuda), **LR saga 4.0 s
por fit**.

> **Lo que esto cambia:** el plan anterior recomendaba "15–20 trials" por miedo al
> costo. Con 10 s por entrenamiento, **150 trials de Optuna × 2 semillas = 50 min**.
> Todo el pipeline profundo de v4 (3 arquitecturas × 3 exps × 2 lookbacks ×
> 8 modalidades × 3 semillas) cabe en ~20 min. El recurso escaso de este proyecto
> **no es la GPU, es la potencia estadística** (ver H4).

---

## H2 — Los modelos del paper están entrenados una época

`entrenar_dl()` (`train_all_v4.py:179`) guarda el `state_dict` de la época con
**menor `val_loss`** y lo restaura al final. Medido:

| Modelo | Época restaurada (mín. `val_loss`) | Época del mejor `val_f1` | val_f1 restaurado | val_f1 máximo | Δ |
|---|---:|---:|---:|---:|---:|
| LSTM lb20 | **1** | 1 | 0.3467 | 0.3467 | 0.0000 |
| CNN lb20 | **1** | 9 | 0.3181 | 0.3507 | **+0.0326** |
| CNN-LSTM lb20 | **2** | 2 | 0.3641 | 0.3641 | 0.0000 |
| LSTM lb60 | **2** | 9 | 0.3181 | 0.3378 | **+0.0197** |

La `val_loss` sube casi monótonamente desde la primera época, así que su mínimo
cae siempre al principio; la paciencia de 15 solo hace que el bucle corra 16–17
épocas antes de rendirse, pero el modelo que se evalúa es el de la época 1 o 2.

Dos consecuencias:

1. La frase del paper *"the deep models train for up to 80 epochs … early stopping
   with patience 15"* es literalmente cierta pero **describe algo que no ocurre**:
   ningún modelo profundo del paper entrenó más de 2 épocas efectivas.
2. Cambiar el criterio de selección de época de `val_loss` a `val_f1` es gratis y
   vale **+0.033 de F1 en el CNN** y **+0.020 en el LSTM lb60** — más que la
   distancia entre el CNN (0.359) y el LSTM (0.376) en la tabla del paper.

---

## H3 — No es sobreajuste: es que no aprenden

Se entrenó el LSTM 40 épocas **sin early stopping** con cinco configuraciones,
midiendo train y val en cada época (`diag_deep.py --solo curvas`).
`ln(3) = 1.0986` es la pérdida de un modelo que predice al azar.

| Config | Parámetros | `train_loss` ep40 | `train_f1` ep40 | **mín. `val_loss`** | mejor `val_f1` |
|---|---:|---:|---:|---:|---:|
| A: lr=1e-3, h=128, 2 capas (v4) | 592 131 | 1.0378 | 0.4544 | **1.0985** | 0.3467 (ep 1) |
| B: lr=3e-4, h=128, 2 capas | 592 131 | 1.0607 | 0.4232 | **1.1026** | 0.3539 (ep 29) |
| C: lr=1e-4, h=128, 2 capas | 592 131 | 1.0670 | 0.4194 | **1.0975** | 0.3574 (ep 3) |
| D: lr=3e-4, h=32, 1 capa | 24 643 | 1.0684 | 0.4092 | **1.1019** | 0.3248 (ep 2) |
| E: lr=1e-3, h=16, 1 capa | 10 275 | 1.0600 | 0.4241 | **1.0978** | 0.3385 (ep 23) |

Lecturas:

- **Ninguna configuración logra una `val_loss` mejor que el azar.** El mejor valor
  de las cinco (1.0975) está 0.0011 por debajo de ln(3). Como estimador de
  probabilidades, el LSTM en validación es indistinguible del azar.
- **No se arregla haciendo el modelo más chico.** Un LSTM de 10 275 parámetros
  (57× más chico) rinde igual que el de 592 131. Por eso *no* es un problema de
  capacidad ni de regularización — que es justo lo que el grid manual de `CONFIGS`
  estaba moviendo (`hidden ∈ {128,192}`, `layers ∈ {2,3}`, `dropout ∈ {0.3,0.4}`).
- Sí hay una brecha train/val que crece (ep40: `train_f1` 0.45 vs `val_f1` ~0.33),
  pero es lenta y **no es la restricción activa**: la restricción es que la
  validación no mejora nunca, ni siquiera al principio.
- El `val_f1` **oscila entre 0.16 y 0.36 de una época a otra** dentro de la misma
  corrida. Esa amplitud (±0.05) es mayor que toda la distancia entre el primero y
  el último modelo de la tabla global del paper (0.411 vs 0.343).

**Descartado como causa raíz: el escalador.** La sospecha razonable era que el
`MinMaxScaler` ajustado en train aplastara las features o dejara test fuera de
rango. Medido (Exp B, escalado por ticker, como hace el pipeline): desviación
estándar mediana tras escalar = **0.151** (mín. 0.063 en `VIX_change`, máx. 0.388),
**0 de 61 features quedan casi constantes**, y solo el **1.00 %** de los valores de
test cae fuera de [0, 1] (rango real de test: −0.22 a 4.28). Para comparar,
`StandardScaler` deja test entre −7.4 y +15.3. El MinMax no es el problema; puede
probarse como variante, pero no como explicación.

> **Interpretación:** las 61 features ya son agregados multi-día (`ret_10d`,
> `mom_60d`, `dist_ma200`, medias móviles…). Apilar 20 o 60 días de esas features
> le da a la red una entrada enormemente redundante y con poca señal marginal, y la
> etiqueta (percentil 30/70 del retorno de 1 día) es casi ruido. Ese es el escenario
> típico en el que un modelo secuencial no tiene nada que extraer. Esto **apoya** la
> conclusión del paper, pero por una razón distinta a la que el paper argumenta.

---

## H4 — En validación no hay diferencia entre modelos

Mismos datos (Exp B, GLOBAL), F1-macro:

| Modelo | F1 **validación** (2024) | F1 **test** (2025), reportado en el paper |
|---|---:|---:|
| LR elasticnet C=1.0 | **0.3559** | 0.3847 |
| LR elasticnet C=0.1 | 0.3478 | — |
| LR elasticnet C=0.01 | 0.3503 | — |
| XGBoost (parámetros por defecto) | **0.3738** | 0.3862 |
| Mejor LSTM de las 5 configs de H3 | **0.3574** | 0.3700 |
| CNN (mejor época) | 0.3507 | 0.3434 |
| CNN-LSTM (mejor época) | 0.3641 | 0.3835 |

LR llega a `train_f1` = 0.415–0.427 frente a `val_f1` = 0.348–0.356: **LR tampoco
generaliza bien**, solo generaliza *menos mal*.

En validación los cinco modelos caben en una banda de ~0.02 y el que manda es
XGBoost, no LR. En test manda LR. Con ~1 600–1 760 filas de test y una oscilación
medida de ±0.05, **la hipótesis de que las diferencias del paper sean ruido de un
único año de test no está descartada — y hoy no hay en el paper ninguna prueba
estadística que la descarte.**

> Advertencia: las filas de validación no son idénticas entre modelos (1 764 para
> LR/XGB, 1 624 para lb=20, 1 344 para lb=60). Ver H5(c).

---

## H5 — Tres asimetrías que rompen la comparación del paper

Verificado leyendo el código, no inferido:

**(a) El lookback se eligió con test.** `consolidar_v4.py:35` y `plots_extra.py:55`
hacen `groupby(...)["test_f1_macro"].idxmax()`: para LSTM/CNN/CNN-LSTM se reporta
el **máximo entre lb=20 y lb=60 medido en test**. `resultados_v4.csv` no contiene
ninguna columna de validación (19 columnas, todas `test_*`), así que la selección
no *pudo* hacerse en validación. `paper.tex:198` afirma lo contrario: *"best
lookback is selected on the validation set"*. Hay que arreglar el pipeline o
corregir la frase; tal como está, es una observación fácil de hacer para un revisor
y difícil de defender.

**(b) LR y XGBoost reentrenan con train+val; los profundos no.** En
`train_all_v4.py`, `run_lr()` y `run_xgb()` ajustan el modelo final sobre
`Xfull = vstack([X_tr, X_va])` (líneas 250 y 310): ven 2024 completo antes de
predecir 2025. `run_dl()` nunca reentrena. Los modelos profundos compiten con **un
año menos de datos**, y justo el año pegado al test.

**(c) Los modelos no se evalúan sobre las mismas filas de test.**
`prep_seq_ticker()` construye las ventanas *dentro de cada split*, así que se
pierden las primeras `lookback` filas de val y de test:

| Modelo | Filas de test por ticker | Total |
|---|---:|---:|
| LR / XGBoost | 248 | 1 736 |
| LSTM/CNN/CNN-LSTM lb=20 | 228 | 1 596 |
| LSTM/CNN/CNN-LSTM lb=60 | 188 | 1 316 |

Con lb=60 los profundos se evalúan sobre el **76 %** de los días que LR/XGBoost, y
sobre un tramo distinto (les faltan enero–marzo de 2025). Las columnas de la tabla
del paper no son estrictamente comparables. Es corregible sin leakage: construir
las ventanas sobre la serie continua y **después** cortar por fecha — una ventana
de test puede mirar hacia atrás a días de validación, que es información pasada, no
futura. Lo único que debe ajustarse solo con train es el escalador.

---

## Qué implica esto para el pedido del Revisor #2

El revisor pidió una búsqueda de hiperparámetros seria para los modelos profundos.
Hacerla **sigue siendo necesario** (es barata y cierra el comentario), pero
**por sí sola no va a cambiar nada**: si un LSTM de 10 k parámetros y uno de 592 k
rinden igual, y ninguno mejora al azar en `val_loss`, mover `hidden` y `dropout`
dentro de esos rangos no va a producir un salto.

Lo que sí puede mover la aguja, en orden de expectativa:

1. **Arreglar el protocolo** (criterio de época, alineación de filas, reentrenar
   con train+val, seleccionar en validación). Es gratis y ya sabemos que vale
   hasta +0.033 en un modelo.
2. **Darle más datos a los modelos profundos**: el universo de entrenamiento se
   puede ampliar de 7 a 50+ tickers sin salir de Yahoo Finance.
3. **Enriquecer la entrada** con las series que Yahoo sí publica y hoy no se usan
   (curva de tasas, estructura temporal del VIX, dólar, crédito, sectores).
4. **Medir la incertidumbre** (walk-forward + bootstrap) para saber cuáles de las
   diferencias reportadas son reales.

El plan de ejecución de esos cuatro puntos está en
**[`PLAN_MAESTRO_BUSQUEDA.md`](PLAN_MAESTRO_BUSQUEDA.md)**.
