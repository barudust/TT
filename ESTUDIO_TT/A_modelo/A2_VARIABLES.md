# A2 — Las 76 variables (61 base + 15 interacciones)

> **Resumen.** Todas las variables se calculan con precios y volumen
> diarios de la acción, más SPY y VIX. Ninguna usa información posterior al
> cierre del día. Se agrupan en 9 familias. Están definidas en
> `scripts_v1/01_build_raw_dataset.py` y copiadas idénticas en
> `api/ml/features.py` (la API debe calcularlas igual que el entrenamiento;
> si no, las predicciones en vivo no serían comparables).
>
> Notación: `C` cierre, `O` apertura, `H` máximo, `L` mínimo, `V` volumen;
> `C_{t-k}` = cierre de hace *k* días; `MA_n` = media de los últimos *n*
> cierres; `ln` = logaritmo natural.

---

## 1. Panorama

| # | Familia | Cuántas | Qué le dice al modelo |
|---|---|---:|---|
| 1 | Retornos logarítmicos | 5 | Cuánto se movió el precio en los últimos días |
| 2 | Momentum | 4 | Velocidad y dirección de la tendencia |
| 3 | Medias móviles | 9 | Dónde está el precio respecto a su tendencia |
| 4 | Volatilidad | 8 | Qué tan agitado está el precio |
| 5 | Osciladores | 9 | Si la acción está "sobrecomprada" o "sobrevendida" |
| 6 | Volumen y flujo | 8 | Si el movimiento viene con convicción (mucho volumen) |
| 7 | Forma de la vela | 7 | Cómo fue la sesión del día |
| 8 | Calendario | 5 | Día de la semana, mes, semana del mes |
| 9 | Contexto de mercado | 6 | Qué hacen el S&P 500 y el VIX |
| | **Total base** | **61** | |
| | Interacciones (Etapa 5) | 15 | Productos de pares de variables importantes |
| | **Total en producción** | **76** | |

### ¿Por qué tantas formas de normalizar?

Casi todas las variables son **razones o porcentajes** (por ejemplo,
distancia a la media en %), no precios. Así un valor significa lo mismo en
una acción de $20 y en una de $900, y un **modelo global** puede mezclar
las 7 acciones.

---

## 2. Familia 1 — Retornos logarítmicos (5)

| Variable | Fórmula | Qué mide |
|---|---|---|
| `ret_1d` | `ln(C_t / C_{t-1})` | Movimiento de hoy |
| `ret_2d` | `ln(C_t / C_{t-2})` | Últimos 2 días |
| `ret_3d` | `ln(C_t / C_{t-3})` | Últimos 3 días |
| `ret_5d` | `ln(C_t / C_{t-5})` | Última semana |
| `ret_10d` | `ln(C_t / C_{t-10})` | Últimas dos semanas |

**Por qué varias escalas:** a corto plazo los precios tienden a revertirse
(si cayó mucho hoy, puede rebotar) y a plazo medio tienden a continuar. Con
varias escalas el modelo puede captar ambos efectos.

## 3. Familia 2 — Momentum (4)

| Variable | Fórmula | Qué mide |
|---|---|---|
| `mom_5d` | `C_t / C_{t-4} − 1` | Cambio en ~1 semana |
| `mom_10d` | `C_t / C_{t-9} − 1` | ~2 semanas |
| `mom_20d` | `C_t / C_{t-19} − 1` | ~1 mes |
| `mom_60d` | `C_t / C_{t-59} − 1` | ~1 trimestre |

**Diferencia con los retornos:** son cambios porcentuales simples y llegan
más lejos (60 días). Hay redundancia intencional con la familia 1; la
regularización se encarga de repartir el peso.

## 4. Familia 3 — Medias móviles (9)

| Variable | Fórmula | Qué mide |
|---|---|---|
| `dist_ma10` | `C_t / MA10 − 1` | % arriba/abajo de la media de 10 días |
| `dist_ma20` | `C_t / MA20 − 1` | ídem, 20 días (~1 mes) |
| `dist_ma30` | `C_t / MA30 − 1` | ídem, 30 días |
| `dist_ma50` | `C_t / MA50 − 1` | ídem, 50 días (~1 trimestre) |
| `dist_ma200` | `C_t / MA200 − 1` | ídem, 200 días (~1 año): tendencia de fondo |
| `cruce_ma10_ma50` | `MA10 / MA50 − 1` | Si la tendencia corta va arriba de la media |
| `cruce_ma20_ma50` | `MA20 / MA50 − 1` | ídem |
| `cruce_ma50_ma200` | `MA50 / MA200 − 1` | "Golden cross" (>0) o "death cross" (<0) |
| `pendiente_ma20` | `(MA20_t − MA20_{t-5}) / MA20_{t-5}` | Si la media de 20 días va subiendo o bajando |

**Por qué:** una media móvil suaviza el ruido y muestra la tendencia. Usar
la *distancia* (y no la media misma) la hace comparable entre acciones.
Los periodos 10/20/50/200 son los estándar del análisis técnico.

## 5. Familia 4 — Volatilidad (8)

| Variable | Fórmula | Qué mide |
|---|---|---|
| `atr_14` | Promedio de 14 días del *true range* = máx(H−L, \|H−C_{t-1}\|, \|L−C_{t-1}\|) | Amplitud típica del movimiento diario, incluyendo saltos entre días |
| `atr_norm` | `atr_14 / C_t` | Lo mismo en % del precio (comparable entre acciones) |
| `vol_5d` | desv. est. de `ret_1d` en 5 días × √252 | Volatilidad de la última semana, anualizada |
| `vol_10d` | ídem, 10 días | |
| `vol_20d` | ídem, 20 días | |
| `vol_60d` | ídem, 60 días | |
| `vol_ratio_5_20` | `vol_5d / vol_20d` | ¿La volatilidad está subiendo (>1) o bajando? |
| `vol_ratio_20_60` | `vol_20d / vol_60d` | ídem a plazo más largo |

**Por qué es tan importante:** la volatilidad se agrupa en el tiempo (días
agitados siguen a días agitados). Eso hace predecible la **magnitud** del
próximo movimiento, aunque no su dirección. Es la información que más usa
el modelo.

## 6. Familia 5 — Osciladores (9)

| Variable | Fórmula | Qué mide |
|---|---|---|
| `rsi_14` | `100 − 100/(1 + G/P)`, G y P = promedios exponenciales de subidas y bajadas en 14 días (Wilder) | Fuerza relativa: >70 sobrecomprado, <30 sobrevendido |
| `rsi_7` | ídem con 7 días | Versión más rápida |
| `macd` | `(EMA12 − EMA26) / C_t` | Diferencia entre tendencia corta y larga, en % del precio |
| `macd_sig` | `EMA9(MACD) / C_t` | Línea de señal (MACD suavizado) |
| `macd_hist` | `(MACD − señal) / C_t` | Si el MACD acelera o frena |
| `stoch_k` | `100 · (C_t − mín L 14d) / (máx H 14d − mín L 14d)` | Dónde está el cierre dentro del rango de 14 días |
| `stoch_d` | media de 3 días de `stoch_k` | Versión suavizada |
| `stoch_diff` | `stoch_k − stoch_d` | Si el estocástico acelera |
| `williams_r` | `−100 · (máx H 14d − C_t) / (máx H 14d − mín L 14d)` | Como el estocástico, escala −100 a 0 |

**Por qué varios parecidos:** cada uno captura algo un poco distinto
(ventana, suavizado). Están correlacionados, pero la regularización reparte
el peso entre ellos. Se probó quitar los redundantes con filtros
estadísticos y fue peor (ver [A6](A6_ETAPAS_DEL_PROYECTO.md)).

**Nota:** el MACD se divide entre el precio para que sea comparable entre
acciones (el MACD clásico está en dólares).

## 7. Familia 6 — Volumen y flujo (8)

| Variable | Fórmula | Qué mide |
|---|---|---|
| `vol_log` | `ln(V_t + 1)` | Volumen del día (en logaritmo, para comprimir valores extremos) |
| `vol_ratio` | `V_t / media de V en 20 días` | Volumen inusual (>1 = más de lo normal) |
| `obv_ratio` | `OBV_t / \|media OBV 20d\| − 1` | Si el volumen acumulado acompaña a la tendencia |
| `obv_pendiente` | cambio de 5 días del OBV ÷ precio | Dirección reciente del flujo |
| `vwap_dist` | `(C_t − VWAP20) / VWAP20` | Distancia al precio promedio ponderado por volumen de 20 días |
| `cmf_20` | Chaikin Money Flow, 20 días | Presión compradora (+) o vendedora (−) |
| `mfi_14` | Money Flow Index, 14 días | RSI ponderado por volumen |
| `vol_trend` | `media V 20d / media V 60d − 1` | Si el volumen viene creciendo |

**Por qué:** un movimiento con mucho volumen suele ser más "real" que uno
con poco. *OBV* (On-Balance Volume) suma el volumen en días de subida y lo
resta en días de bajada; como crece sin límite, se usa normalizado.

## 8. Familia 7 — Forma de la vela (7)

| Variable | Fórmula | Qué mide |
|---|---|---|
| `rango_rel` | `(H − L) / C` | Qué tan amplia fue la sesión |
| `cambio_intra` | `(C − O) / O` | Si el día cerró arriba o abajo de donde abrió |
| `cuerpo_rel` | `\|C − O\| / (H − L)` | Qué parte del rango fue movimiento "neto" |
| `sombra_sup` | `(H − máx(O, C)) / ATR14` | Rechazo en máximos (presión vendedora) |
| `sombra_inf` | `(mín(O, C) − L) / ATR14` | Rechazo en mínimos (presión compradora) |
| `gap_apertura` | `(O_t − C_{t-1}) / C_{t-1}` | Salto entre el cierre de ayer y la apertura de hoy |
| `hl_ratio` | `(C − L) / (H − L)` | Dónde cerró dentro del rango (0 = en el mínimo, 1 = en el máximo) |

**Por qué:** el análisis técnico da mucha importancia a las figuras de
velas (martillo, doji, envolvente). Estas variables las describen con
números continuos en vez de reglas.

## 9. Familia 8 — Calendario (5)

| Variable | Fórmula | Qué mide |
|---|---|---|
| `dia_sin`, `dia_cos` | `sin(2π·d/5)`, `cos(2π·d/5)`, *d* = día de la semana | Día de la semana como un punto en un círculo |
| `mes_sin`, `mes_cos` | `sin(2π·m/12)`, `cos(2π·m/12)` | Mes del año, en círculo |
| `semana_mes` | `(semana del mes − 2.5) / 2.5` | Inicio, mitad o fin de mes |

**Por qué seno y coseno:** el calendario es circular. Con números 1–5, el
lunes (1) y el viernes (5) parecerían lejanos; en el círculo quedan
cerca. Con *one-hot* (una columna por día) serían todos igual de
distintos. Se incluyen por efectos de calendario conocidos (fin de mes,
rebalanceos), aunque su peso en el modelo es pequeño.

## 10. Familia 9 — Contexto de mercado (6)

| Variable | Fórmula | Qué mide |
|---|---|---|
| `SP500_ret` | `ln(SPY_t / SPY_{t-1})` | Qué hizo el mercado hoy |
| `SP500_vol20` | desv. est. 20d de `SP500_ret` × √252 | Volatilidad del mercado |
| `SP500_mom20` | `SPY_t / SPY_{t-19} − 1` | Tendencia del mercado en un mes |
| `VIX` | cierre del VIX | Nivel de nerviosismo |
| `VIX_change` | cambio % diario del VIX | Si el nerviosismo sube o baja |
| `VIX_norm` | `(VIX − media 252d) / desv. 252d` | VIX comparado con su último año (puntuación *z*) |

**Son las más importantes del modelo final.** Las 10 variables con mayor
coeficiente (en valor absoluto) al entrenar fueron: `VIX_norm`, `vol_log`,
`VIX`, `SP500_vol20`, `SP500_ret`, `rango_rel`, `atr_norm`, `vol_ratio`,
`SP500_mom20` y `sombra_sup`. Casi todas son de volatilidad o de mercado.

Consecuencia: como estas variables son **iguales para las 7 acciones** en
un mismo día, el modelo tiende a dar la misma señal a todas cuando el VIX
está bajo (MANTENER en bloque).

---

## 11. Las 15 interacciones (Etapa 5, en producción)

### Qué son

Una interacción es el producto de dos variables: `a × b`. Una Regresión
Logística es lineal: el efecto de cada variable es fijo. Con `a × b`, el
efecto de `a` puede depender de `b` (por ejemplo, el volumen inusual puede
significar algo distinto si el mercado está nervioso).

### Cómo se eligieron

1. Se tomaron las 10 variables con mayor |coeficiente| en el entrenamiento
   (lista de arriba).
2. De todos los pares posibles entre ellas se **sortearon 15** con semilla
   fija (42).
3. Se agregaron como columnas nuevas.

La elección de **cuáles** variables no miró la prueba; la decisión de
**adoptarlas** sí (se compararon en 2025). Por eso su "mejora" no se
presenta como tal (ver abajo).

### Las 15 parejas

| # | Interacción | Idea |
|---|---|---|
| 1 | `VIX_norm × SP500_vol20` | Nerviosismo esperado × volatilidad real del mercado |
| 2 | `atr_norm × vol_ratio` | Amplitud de la acción × volumen inusual |
| 3 | `VIX × vol_ratio` | Miedo × volumen inusual |
| 4 | `SP500_ret × SP500_mom20` | Movimiento de hoy × tendencia del mes |
| 5 | `VIX_norm × SP500_mom20` | Miedo relativo × tendencia |
| 6 | `SP500_ret × vol_ratio` | Mercado de hoy × volumen de la acción |
| 7 | `VIX_norm × SP500_ret` | Miedo × movimiento del mercado |
| 8 | `SP500_ret × atr_norm` | Mercado × amplitud de la acción |
| 9 | `vol_log × vol_ratio` | Nivel × anomalía de volumen |
| 10 | `SP500_ret × rango_rel` | Mercado × amplitud de la sesión |
| 11 | `vol_log × SP500_mom20` | Volumen × tendencia del mercado |
| 12 | `atr_norm × SP500_mom20` | Amplitud × tendencia del mercado |
| 13 | `SP500_vol20 × SP500_ret` | Volatilidad × movimiento del mercado |
| 14 | `SP500_vol20 × atr_norm` | Volatilidad del mercado × de la acción |
| 15 | `atr_norm × sombra_sup` | Amplitud × rechazo en máximos |

Archivo fuente de verdad: `api/ml/artifacts/interaction_pairs.json`.

### Qué aportaron (honestamente)

| Evaluación | Sin interacciones | Con interacciones |
|---|---:|---:|
| Prueba 2025 (donde se eligieron) | 0.390 | **0.413** |
| Validación 2024 | 0.326 | 0.325 |
| Origen rodante 2019–2024 (media de 6 años) | 0.354 | 0.357 |
| Sharpe medio en esos 6 años | +0.53 | +0.52 |

La mejora solo aparece en el año en que se decidió adoptarlas. En
validación y en 6 años de origen rodante **empatan**. Se mantuvieron porque
no empeoran, pero se presentan como **equivalentes**, no como mejora. Es un
ejemplo de por qué no hay que elegir mirando el año de prueba.

---

## 11b. Cómo se usaban las variables en el TT1 (y por qué cambió)

**Conteo.** El texto del TT1 habla de **54 características** (resumen, §3.2,
§3.3) y de "ocho" de medias móviles, pero su propia Tabla 4 lista **61** (con
9 de medias móviles), que son las que calcula el código. En el documento
final hay que decir 61.

**Selección por modelo (TT1 §3.4).** En TT1 cada modelo recibía un
subconjunto distinto, elegido en el entrenamiento de cada experimento, con
la condición de cumplir el criterio en al menos 3 de las 7 acciones:

| Modelo | Método | Variables A / B / C |
|---|---|---|
| Regresión Logística | Pearson (p < 0.05) + VIF ≤ 10 | 8 / 4 / 3 (en C: `SP500_ret`, `cmf_20`, `sombra_sup`) |
| XGBoost | Media absoluta de SHAP | 24 / 23 / 25 |
| LSTM | Spearman (p < 0.05) | 25 / 10 / 3 (en C: `rsi_7`, `stoch_k`, `williams_r`) |
| CNN-LSTM y CNN 1D | Spearman + 5 canales OHLCV normalizados por ventana | igual que LSTM + 5 |

Además se guardaba la unión de las variables usadas por algún modelo (46)
en la tabla `features_daily` de la base de datos.

**Por qué se abandonó.** (1) El propio TT1 concluyó que la diferencia en el
número de variables impedía comparar arquitecturas (§5.6: "un modelo con 25
características supere a uno con 3 no permite concluir que su arquitectura
sea mejor"). (2) Al medirlo, usar las 61 fue mejor que el filtro en 11 de 15
casos (§12 y [A6](A6_ETAPAS_DEL_PROYECTO.md)). (3) Para la LR el cambio fue
grande: en el Exp B por acción pasó de 0.355 (4 variables) a 0.392 (61). Con
las mismas variables para todos, los clásicos siguen arriba: la asimetría no
explicaba la diferencia.

**Canales OHLCV.** En TT1 la CNN-LSTM y la CNN 1D recibían además
apertura/máximo/mínimo/cierre divididos entre el cierre del primer día de la
ventana y el volumen dividido entre el máximo de la ventana, para aprender
formas de velas. Desde la Etapa 3 ninguna red los recibe (misma entrada para los
cinco). El paper todavía los menciona en su §4; el código de la Etapa 3 no los usa.

---

## 12. Lo que se probó agregar y no sirvió

| Variante | Qué se agregó | Resultado |
|---|---|---|
| Etapa 2 (94 variables) | Curva de tasas, dólar, oro, petróleo, sectores (XLK, XLF, XLY, XLE) | Sin mejora; más sobreajuste |
| Etapa 4 (93 variables) | Bonos (SHY, IEI, IEF, TLT), VVIX, crédito (HYG, LQD), dólar, oro, petróleo, sectores e índices | Optuna prefirió las 61 originales |
| Rezagos (Etapa 5) | Top-10 variables de hace 1, 3 y 5 días (+30) | Peor (−0.004) |
| Multi-escala (Etapa 5) | Top-10 en ventanas de 5 y 20 días (+20) | Neutro (−0.002) |
| Entre activos (Etapa 5) | Beta contra SPY, correlación con XLK, ranking del retorno (+3) | Marginal (+0.003) |

Y quitar variables con filtros estadísticos (Pearson, VIF, Spearman, SHAP)
fue peor en 11 de 15 casos. Conclusión: **el límite no está en las
variables, está en la poca señal del problema**.

---

## 13. Escalado

Antes de entrenar, las variables se escalan con un escalador ajustado
**solo con el periodo de entrenamiento**:

| Escalador | Cómo | Dónde se usó |
|---|---|---|
| StandardScaler | `(x − media) / desv. est.` | LR en la Etapa 3; XGBoost (no le hace falta, se mantuvo por convención) |
| MinMaxScaler | `(x − mín) / (máx − mín)` | Redes en la Etapa 3 |
| **RobustScaler** | `(x − mediana) / (P75 − P25)` | Elegido por Optuna en la Etapa 4 para LR y las tres redes; **producción** |

**Por qué RobustScaler:** los retornos tienen colas pesadas (días como
marzo de 2020). Con la media y la desviación estándar, esos días inflan la
escala y aplastan al resto; la mediana y el rango intercuartílico no se
alteran.

**Global o por acción:** en la investigación se ajustó un escalador por
acción; en producción hay uno solo para las 7. Se midió la diferencia:
F1 0.4125 contra 0.4086 en 2025, despreciable.

---

## Preguntas de este tema

Están desarrolladas en [D3](../D_defensa/D3_PREGUNTAS_DATOS.md).
