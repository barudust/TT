# Análisis del modelo actual: exceso de HOLD, percentiles 40/60, global vs por-ticker y auditoría de la plataforma

> **Fecha: 2026-09-30.** No se modificó ni reentrenó el modelo: todo lo de
> este documento es medición. Scripts:
> [`scripts_opt/analisis_hold_global.py`](../../scripts_opt/analisis_hold_global.py)
> (sin red, ~20 s) y
> [`scripts_opt/evaluar_produccion_2026.py`](../../scripts_opt/evaluar_produccion_2026.py)
> (con red, usa el mismo código que la API). Salidas en
> [`RESULTADOS_OPTIMIZADOS/analisis_hold/`](../analisis_hold/).
>
> El escrito de justificación para la defensa, que se apoya en estos
> números, está en
> [`../JUSTIFICACION_LIMITE_DEL_MODELO.md`](../JUSTIFICACION_LIMITE_DEL_MODELO.md).

Protocolo: el mismo de Vía 8 — Exp B GLOBAL, train 2018-2023, validación
2024, test 2025, LR con los hiperparámetros de producción (L2,
C = 0.000165, `class_weight="balanced"`, RobustScaler). Además de F1-macro
se reporta **kappa de Cohen**, que corrige por azar y sí es comparable entre
etiquetas con distinta proporción de clases (0 = azar, 1 = perfecto).

---

## 1. Reproducción del modelo actual

| Variante | F1 val 2024 | κ val | Sharpe val | F1 test 2025 | κ test | Sharpe test | HOLD pred. test |
|---|---:|---:|---:|---:|---:|---:|---:|
| LR 61 features (sin interactions) | 0.3255 | 0.035 | −0.38 | 0.3899 | 0.106 | +0.68 | 56.9 % |
| **LR 61 + 15 interactions** (escalador por ticker, como Vía 8) | **0.3246** | 0.030 | −0.49 | **0.4125** | 0.140 | +0.92 | 57.0 % |
| LR 61 + 15 interactions (escalador global, como `entrenar_produccion.py`) | 0.3330 | 0.036 | −0.08 | 0.4086 | 0.132 | +1.05 | 57.8 % |

Tres observaciones:

1. **Se reproduce Vía 8** (0.4125 vs 0.4133 reportado; la diferencia es de
   filas descartadas por NaN).
2. **La mejora de las interactions solo existe en 2025.** En validación
   2024 el LR con y sin interactions empatan (0.3246 vs 0.3255) y en 2026
   fuera de muestra el modelo con interactions da F1 = 0.313 (§6). Las
   interactions se eligieron mirando test 2025 (`via8_dataset.py` evalúa
   sobre `X_eval` = 2025), así que el +0.023 no está validado. Además
   `api/ml/artifacts/lr_elasticnet_global_expB.metrics.json` y el `.pkl`
   etiquetan esas cifras como "val 2024 honesto", pero son de test 2025.
3. **Desajuste de escalador:** Vía 8 evaluó con un RobustScaler por ticker;
   `entrenar_produccion.py` ajusta uno solo sobre los 7 tickers. El efecto
   es pequeño (F1 test −0.004, Sharpe +0.13), pero el modelo desplegado no
   es idéntico al evaluado.

## 2. ¿Por qué predice tanto HOLD?

### 2.1 Cuánto

| Periodo | HOLD real | HOLD predicho |
|---|---:|---:|
| Validación 2024 | 39.5 % | 64.4 % |
| Test 2025 | 42.0 % | 57.0 % |
| 2026 fuera de muestra (ene–sep, producción) | 34.7 % | 59.5 % |
| Últimos 30 días hábiles (17 ago–28 sep 2026) | 38.1 % | **94.8 %** |

Matriz de confusión, test 2025 (filas = real):

| | pred SELL | pred HOLD | pred BUY |
|---|---:|---:|---:|
| real SELL | 172 | 262 | 79 |
| real HOLD | 154 | 493 | 79 |
| real BUY | 140 | 231 | 119 |

### 2.2 Mecanismo 1 — "voto dividido"

En el **100 %** de los días que el modelo dice HOLD (test 2025 y 2026),
P(BUY) + P(SELL) > P(HOLD). Probabilidades medias en esos días: SELL 0.32,
**HOLD 0.38**, BUY 0.29. Es decir: el modelo sí cree que lo más probable es
un movimiento fuerte (0.62), pero no sabe hacia dónde; esa probabilidad se
reparte entre BUY y SELL y ninguna de las dos le gana a HOLD en el argmax.
HOLD gana siempre que P(HOLD) supere ~1/3 y la dirección esté indefinida.
Por eso el exceso de HOLD es un **síntoma** de que la dirección diaria casi
no es predecible con estos datos, no un error del código.

### 2.3 Mecanismo 2 — régimen de volatilidad del mercado

Las features con más peso son de volatilidad del mercado (VIX_norm, VIX,
SP500_vol20, …), iguales para los 7 tickers en un mismo día. Cuando el VIX
está por debajo de su media de 252 días el modelo dice HOLD para casi todo:

| Quintil de VIX_norm | HOLD pred. 2025 | HOLD real 2025 | \|retorno\| medio 2025 | HOLD pred. 2026 | HOLD real 2026 |
|---|---:|---:|---:|---:|---:|
| Q1 (VIX bajo) | 92.0 % | 54.9 % | 1.16 % | 96.5 % | 35.5 % |
| Q2 | 88.3 % | 46.9 % | 1.46 % | 82.6 % | 38.6 % |
| Q3 | 74.3 % | 47.1 % | 1.51 % | 69.5 % | 29.0 % |
| Q4 | 28.9 % | 32.9 % | 1.90 % | 46.7 % | 35.9 % |
| Q5 (VIX alto) | 0.6 % | 27.7 % | 2.57 % | 1.9 % | 34.4 % |

En 2025 la regla "VIX bajo → movimientos chicos" era real (HOLD real 55 %
vs 28 %), por eso ese año el modelo funcionó. **En 2026 dejó de cumplirse**
(HOLD real ≈ 35 % en todos los quintiles), pero el modelo la sigue
aplicando. Por mes en 2026: marzo (VIX_norm medio +1.2) → 1.9 % HOLD;
agosto (−0.9) → 97.3 % HOLD. Desde agosto el VIX está debajo de su media
anual, y por eso la plataforma muestra MANTENER en casi todo.

### 2.4 El HOLD no destruye valor

- Los días HOLD tienen movimientos ~40 % menores: \|retorno\| medio 1.31 %
  vs 2.19 % (BUY) y 2.30 % (SELL) en 2025.
- Misma estrategia forzando BUY/SELL (sin HOLD):

| | Sharpe | Win rate | Profit factor | Max DD |
|---|---:|---:|---:|---:|
| Test 2025 — modelo | +0.92 | 53.2 % | 1.29 | −52 % |
| Test 2025 — sin HOLD | +0.89 | 51.4 % | 1.18 | −61 % |
| Val 2024 — modelo | −0.49 | 45.9 % | 0.86 | −65 % |
| Val 2024 — sin HOLD | −0.71 | 47.7 % | 0.87 | −87 % |

- Contra 500 permutaciones aleatorias de las mismas señales: en 2025 solo
  el 0.4 % supera al modelo; **en 2024 el 79 % lo supera**. La señal existe
  en algunos años y no en otros (ver §6 y el walk-forward en §7).

### 2.5 Confianza

Mediana 0.378 (p25 0.360, p75 0.399); en 2026, 0.367. Con C = 0.000165 los
coeficientes son diminutos (norma 0.06–0.09 por clase), así que las
probabilidades quedan cerca de 1/3; en el 28 % de los días la señal se
decide por menos de 2 puntos porcentuales. Aun así la confianza **sí es
informativa**: accuracy 39 % con confianza ≤ 0.36 vs 56 % entre 0.40 y 0.45.

## 3. ¿Conviene 40/60 ("60/40") en vez de 30/70?

40/60 = SELL si el retorno queda en el 40 % inferior, BUY en el 40 %
superior, HOLD solo en el 20 % central. Vía 8 ya lo había probado con el LR
sin interactions (F1 0.345, HOLD pred. 53.8 %); aquí se repite con el
modelo actual y se añade validación 2024 y kappa:

| Percentiles | Real C/M/V (test) | Pred. C/M/V (test) | F1 test | κ test | Sharpe test | F1 val | κ val | Sharpe val |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 20/80 | 18.9 / 61.1 / 20.0 | 11.4 / 60.1 / 28.5 | 0.424 | 0.163 | +0.78 | 0.344 | 0.051 | −0.52 |
| 25/75 | 24.1 / 51.1 / 24.8 | 14.1 / 56.8 / 29.1 | 0.424 | 0.160 | +0.90 | 0.345 | 0.047 | −0.32 |
| **30/70 (actual)** | 28.3 / 42.0 / 29.7 | 16.0 / 57.0 / 27.0 | 0.413 | 0.140 | +0.92 | 0.325 | 0.030 | −0.49 |
| 35/65 | 33.4 / 31.8 / 34.9 | 17.0 / 54.2 / 28.8 | 0.384 | 0.107 | +0.64 | 0.318 | 0.032 | −0.22 |
| **40/60** | 39.2 / 20.3 / 40.5 | 18.3 / **53.4** / 28.2 | 0.347 | 0.077 | +0.58 | 0.297 | 0.024 | +0.13 |

Conclusión:

- **40/60 no arregla el exceso de HOLD**: con solo 20 % de HOLD real, el
  modelo sigue prediciendo HOLD el 53 % (test) y 59 % (val) de los días.
  Por el mecanismo de §2.2 — cambiar dónde se corta la etiqueta no le da
  al modelo información sobre la dirección.
- **Empeora la clasificación** en los dos años (κ −45 % en test, −20 % en
  val) y el Sharpe de test (+0.92 → +0.58). En 2024 el Sharpe mejora
  (−0.49 → +0.13), pero ese año todos los percentiles pierden contra
  comprar y mantener (+1.16), así que no es una mejora utilizable.
- Mover los percentiles hacia afuera (25/75, 20/80) sube un poco F1/κ,
  pero **aumenta** el HOLD real a 51–61 %: lo contrario de lo buscado.

**Costo de hacerlo bien para los 5 modelos:** LR tarda segundos, pero
XGBoost y los 3 profundos requieren `xgboost`/`torch` con GPU (no
instalados en este equipo), repetir el protocolo v5 (Optuna 150 trials
× 2 clásicos + 80 × 3 profundos ≈ 6–8 h de GPU según
`PLAN_MAESTRO_BUSQUEDA.md`), las 120 corridas (global + 7 por ticker × 3
experimentos), reconsolidar tablas y reescribir la tesis — y el paper
aceptado en MICAI usa 30/70. Con el mejor modelo empeorando, el valor
esperado de esa inversión es negativo.

### 3.1 Alternativa sin reentrenar: bajar el peso de HOLD al decidir

Multiplicar P(HOLD) por *k* < 1 antes del argmax (equivale a un umbral por
clase). Primer análisis, eligiendo *k* solo con validación 2024:

| k | HOLD val / test / 2026 | F1 val | F1 test | F1 2026 | Sharpe val | Sharpe test | Sharpe 2026 |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1.00 (actual) | 64 / 57 / 60 % | 0.325 | 0.413 | 0.313 | −0.49 | +0.92 | +0.38 |
| 0.95 | 55 / 49 / 51 % | 0.338 | 0.418 | 0.336 | −0.22 | +1.02 | +0.37 |
| 0.90 (mejor F1 en val) | 44 / 39 / 40 % | 0.348 | 0.416 | 0.352 | −0.34 | +0.92 | +0.27 |
| 0.85 | 32 / 28 / — | 0.347 | 0.397 | — | −0.47 | +0.95 | — |

> **Superado por §8.** Esta tabla elige *k* mirando un solo año (2024). Al
> repetirlo con validación por origen rodante en 6 años (2019–2024), el mejor
> factor fijo es k ≈ 0.99, es decir, ninguno: con k = 0.90 el F1 medio baja de
> 0.357 a 0.334. Lo que parecía una mejora era sobreajuste a 2024. El ajuste
> que sí se adoptó es otro (peso de HOLD al entrenar, §8).

## 4. Global vs por-ticker

**Sí se hizo**, dos veces, para los 5 modelos y los 3 experimentos:
v4 (el paper: 120 corridas) y v5 (protocolo corregido: otras 120, con
predicciones guardadas en `v5/preds/`). El paper resume v4 así: "agrupar
ayuda a XGBoost en 3 de 3 experimentos y a los profundos en 7 de 9, y es
indiferente para LR". Esa comparación mezcla dos métricas distintas
(F1 del global sobre las 1 736 filas juntas vs promedio de 7 F1 por
ticker). Aquí se compara manzanas con manzanas: el modelo global evaluado
sobre **las mismas filas de cada ticker** que su modelo por-ticker.

21 celdas por modelo (3 experimentos × 7 tickers), test 2025, v5:

| Modelo | F1 global | F1 por ticker | Δ | Celdas que gana global | p (signo) | Sharpe global | Sharpe por ticker |
|---|---:|---:|---:|---:|---:|---:|---:|
| **LR** | **0.394** | 0.375 | **+0.019** | **18/21** | 0.002 | **+0.88** | +0.44 |
| XGBoost | 0.359 | 0.364 | −0.005 | 10/21 | 1.00 | +0.38 | +0.38 |
| LSTM | 0.334 | 0.314 | +0.021 | 16/21 | 0.027 | −0.32 | −0.43 |
| CNN | 0.293 | 0.212 | +0.081 | 19/21 | <0.001 | −0.21 | −0.14 |
| CNN-LSTM | 0.305 | 0.330 | −0.026 | 7/21 | 0.19 | +0.05 | +0.16 |

Con la configuración de producción (LR + interactions, Exp B):

| | F1 val 2024 | Sharpe val | F1 test 2025 | Sharpe test |
|---|---:|---:|---:|---:|
| Global (1 modelo) | 0.325 | −0.49 | **0.413** | +0.92 |
| Por ticker (7 modelos) | 0.327 | +0.37 | 0.398 | +0.92 |

**Ganó el global.** Es significativamente mejor en LR, LSTM y CNN, empata
en XGBoost, y en CNN-LSTM el por-ticker queda arriba sin significancia.
Ningún modelo es significativamente mejor por ticker. Razones: 7× más
datos (≈10 500 filas vs ≈1 500), la etiqueta es un percentil del propio
ticker (las clases significan lo mismo en los 7), las features son
razones/normalizadas, y con tan poca señal un modelo por ticker se ajusta
al ruido de ese ticker. Operativamente, uno solo es más simple de mantener.

## 5. Auditoría de la plataforma web

Antes de julio la API generaba precios, señales y confianza con `random`
(confianza = 60–90 % aleatoria); eso se eliminó en el commit `9861302`. En
esta revisión ya no había valores aleatorios, pero sí datos **calculados
mal o mal etiquetados**. Todos se corrigieron:

| Qué se veía | Problema | Corrección |
|---|---|---|
| "Correcta" ✓/✗ en las últimas 10 señales | Comparaba la señal de *t* con el movimiento de *t−1* a *t* (el pasado) y umbrales fijos de ±1 % | Se compara con *t → t+1* usando la misma etiqueta del entrenamiento (`api/ml/target.py`; coincide al 100 % con el `target` del dataset una vez completa la ventana de 252 días). El día sin cierre siguiente queda "Pendiente" |
| F1 BUY / F1 SELL / F1 macro | Eran precisiones, y el "macro" era su promedio | F1 reales por clase (scikit-learn) y F1-macro de las 3 clases |
| Sharpe y Max drawdown | Se calculaban sobre el precio de la acción (buy & hold), no sobre la estrategia | Sobre la estrategia de la tesis (BUY +r, SELL −r, HOLD 0); buy & hold se muestra aparte |
| Retorno acumulado / win rate | Backtest distinto al de la tesis (solo largo, entra en BUY, sale en SELL) | Backtest de la tesis |
| Etiquetas "90d" / "último mes" | Siempre se enviaba la ventana de 30 días | Selector 30/60/90 real (`?days=`) |
| "Mercado cerrado" | Fijo en el código | `GET /market-status` (horario y feriados de NYSE) |
| "Hace unos momentos" | `lastUpdate` inválido (`+00:00Z`) → siempre ese texto | ISO válido + fecha del cierre usado (`dataDate`) |
| Señal del día durante el horario de mercado | Yahoo devuelve la vela en curso con precio intradía y se trataba como cierre | Se descarta hasta que NYSE cierra |
| Confianza | Real (probabilidad del modelo), pero sin contexto | Se muestran las 3 probabilidades y la referencia de azar (33 %) |
| "Acerca de": señales por LSTM/CNN-LSTM, TensorFlow | Falso: las genera la Regresión Logística | Texto corregido + ficha del modelo leída de `GET /model` |
| Endpoints `POST` de override | Permitían escribir señales/métricas que no salen del modelo | Desactivados (403) salvo `ENABLE_MANUAL_OVERRIDES=1` |
| Service worker de la PWA | *Cache-first* con caché fija: quien ya abrió la app se quedaba con la interfaz vieja | *Network-first* y caché `v2` |
| Sharpe con 1 operación | Daba siempre 3.00 (= √(252/28)) | Se omite con menos de 5 días con posición |

Todo lo visible sale ahora de Yahoo Finance, del modelo o de cálculos
sobre ambos; la base de datos guarda además las tres probabilidades de cada
predicción. Tests de la API: 20/20.

## 6. Modelo en producción, 2026 fuera de muestra

`python scripts_opt/evaluar_produccion_2026.py` (2 ene – 28 sep 2026,
7 tickers, 1 295 días-acción que el modelo nunca vio):

| | F1-macro | κ | Sharpe (apilado) | Sharpe portafolio | Buy & hold portafolio |
|---|---:|---:|---:|---:|---:|
| 2026 completo | 0.313 | +0.010 | +0.38 | +0.71 | +0.47 |
| Últimos 30 días | 0.214 | −0.002 | +0.33 | +0.70 | +2.66 |

La clasificación está en nivel de azar (κ ≈ 0); el Sharpe queda positivo
sobre todo porque el modelo se queda fuera del mercado la mayor parte del
tiempo.

## 7. Walk-forward de 6 años (v5)

Existe una corrida walk-forward de v5 (`v5/log_wf_v5.txt`: train 5 años,
val 1, test el año siguiente, 2020–2025) que no está citada en
`RESULTADOS_V5.md` ni en el paper. Consolidada en
`analisis_hold/5_walk_forward_v5_resumen.csv`:

| Año de test | LR | XGBoost | LSTM | CNN | CNN-LSTM | Mejor |
|---|---:|---:|---:|---:|---:|---|
| 2020 | 0.343 | **0.387** | 0.292 | 0.279 | 0.320 | XGBoost |
| 2021 | **0.388** | 0.358 | 0.264 | 0.257 | 0.274 | LR |
| 2022 | 0.314 | 0.347 | **0.366** | 0.314 | 0.351 | LSTM |
| 2023 | **0.335** | 0.330 | 0.312 | 0.316 | 0.319 | LR |
| 2024 | 0.325 | 0.356 | 0.363 | 0.359 | **0.376** | CNN-LSTM |
| 2025 | **0.394** | 0.359 | 0.284 | 0.227 | — | LR |
| **Media** | 0.350 | **0.356** | 0.314 | 0.292 | 0.328 | |
| Sharpe medio | **+0.22** | **+0.22** | −0.48 | −0.29 | −0.25 | |

Ningún modelo supera 0.394 en ningún año; LR y XGBoost empatan en
promedio (≈0.35, apenas arriba del azar) y son los únicos con Sharpe medio
positivo. El ranking cambia de año a año.

## 8. Ajuste aplicado: peso de HOLD × 0.90 al entrenar

Pedido: que el modelo no caiga tanto en HOLD **sin cambiar el target**.
Scripts: [`ajuste_hold_rolling.py`](../../scripts_opt/ajuste_hold_rolling.py)
(sin red, ~45 min por los reentrenamientos) y
[`ajuste_hold_2026.py`](../../scripts_opt/ajuste_hold_2026.py) (con red).

### 8.1 Protocolo: validación por origen rodante

Para cada año Y de 2019 a 2025 se entrena el **pipeline de producción**
(61 + 15 features, RobustScaler global, LR L2 C = 0.000165) con los 6 años
previos y se predice Y completo. Las alternativas se eligen **solo con
2019–2024**; 2025 y 2026 (modelo entrenado con 2018–2025, datos reales de
Yahoo) se usan únicamente para confirmar.

### 8.2 Qué se probó (media 2019–2024 | 2025)

| Alternativa | F1 | κ | HOLD pred. | Sharpe |
|---|---|---|---|---|
| Argmax con pesos "balanced" (modelo anterior) | 0.357 \| 0.411 | 0.063 \| 0.130 | 47 % \| 53 % | +0.52 \| +0.89 |
| Factor fijo k = 0.90 sobre P(HOLD) | 0.334 \| — | 0.050 \| — | 23 % \| — | +0.37 \| — |
| Proporción fija por año (40 %) | 0.337 \| 0.403 | 0.062 \| 0.110 | 45 % \| 35 % | +0.58 \| +0.88 |
| Proporción móvil causal, 63 días | 0.365 \| 0.389 | 0.061 \| 0.086 | 43 % \| 40 % | +0.42 \| +0.68 |
| Proporción móvil causal, 252 días | 0.367 \| 0.410 | 0.070 \| 0.122 | 41 % \| 44 % | +0.51 \| +0.81 |
| Reentrenar, peso HOLD × 0.95 | 0.360 \| 0.411 | 0.062 \| 0.122 | 42 % \| 43 % | +0.53 \| +0.88 |
| **Reentrenar, peso HOLD × 0.90** | **0.365 \| 0.395** | **0.068 \| 0.102** | **36 % \| 29 %** | **+0.54 \| +0.93** |
| Reentrenar, peso HOLD × 0.85 | 0.360 \| 0.365 | 0.062 \| 0.088 | 30 % \| 15 % | +0.46 \| +0.92 |
| Reentrenar, peso HOLD × 0.80 | 0.352 \| 0.304 | 0.061 \| 0.060 | 24 % \| 3 % | +0.41 \| +0.90 |

HOLD real: 40 % en promedio 2019–2024 y 42 % en 2025.

- **Un factor fijo no sirve**: el sesgo de HOLD cambia de signo entre años
  (2022: 13 % predicho contra 32 % real; 2023: 74 % contra 48 %).
- Entre los pesos de reentrenamiento, **× 0.90 es el mejor en F1, κ y
  Sharpe a la vez** en 2019–2024, así que la elección no depende de qué
  métrica se privilegie.
- La regla de proporción móvil (252 días) da un F1 parecido, pero menos
  Sharpe en 2025 y en 2026 (abajo).

### 8.3 Confirmación en 2026 (1 302 días-acción, ninguna decisión los vio)

| Modelo | F1 | κ | HOLD pred. (real 34.7 %) | Sharpe | Sharpe portafolio |
|---|---:|---:|---:|---:|---:|
| Pesos "balanced" (modelo anterior) | 0.313 | 0.010 | 59.7 % | +0.38 | +0.71 |
| "Balanced" + proporción móvil causal | 0.350 | 0.027 | 37.0 % | +0.16 | +0.33 |
| **Peso HOLD × 0.90 (modelo actual)** | **0.354** | **0.035** | **39.7 %** | +0.29 | +0.60 |

Comprar y mantener en el mismo periodo: Sharpe de portafolio +0.49.
HOLD por mes en 2026 con el modelo actual: 35, 5, 1, 46, 64, 16, 44, 86 y
61 % (enero–septiembre); en los meses más tranquilos sigue predominando.

### 8.4 Lectura

- Ninguna alternativa es **estadísticamente** mejor que la anterior
  (peso × 0.90: mejora el F1 en 4 de 6 años de desarrollo, Wilcoxon
  p = 0.31). Con 6 años no hay potencia para afirmarlo.
- Lo que sí se consigue es el objetivo pedido: la proporción de HOLD pasa a
  ser realista (error medio contra el real de 13 a 9 puntos en 2019–2024;
  60 % → 40 % en 2026 con 35 % real) sin perder desempeño de forma medible.
  En 2025 se pasa al otro lado (29 % contra 42 %).
- No cambia el target (30/70 a un día): solo cuánto pesa cada clase en la
  pérdida de entrenamiento.

### 8.5 Qué se cambió

- `scripts_opt/entrenar_produccion.py`: `PESO_HOLD = 0.90`; pesos
  efectivos {SELL 1.103, HOLD 0.762, BUY 1.097}; `config_id`
  `LR-v8-interactions-holdw090`. El `.metrics.json` guarda la evidencia de
  esta sección.
- `api/ml/model.py`: `MODEL_VERSION` actualizado (hay un test que exige que
  coincida con el `.pkl`); `GET /model` reporta "balanced, HOLD ×0.9".
- Reentrenar con pesos "balanced" (peso 1.0) reproduce exactamente el
  modelo anterior: el pipeline es determinista.

