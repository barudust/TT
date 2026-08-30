# Guía de defensa del Trabajo Terminal

> **Documento de estudio y defensa.** Todo lo que se hizo en el TT, explicado
> desde la intuición, con la teoría detrás de cada decisión y un banco de
> preguntas anticipadas para revisores/sinodales.
>
> El paper enviado a MICAI 2026 es una **extensión** de este TT (un producto
> extra). El TT es el trabajo original. Ambos comparten el pipeline, pero el
> alcance del TT es más amplio: incluye las Vías 7 y 8 (refinamiento y
> exploración de dataset) que no fueron al paper por límite de páginas.
>
> Última actualización: 2026-08-30.

---

## Cómo usar esta guía

1. **Cap. 1-5** — El problema y los datos. Léelos primero.
2. **Cap. 6-8** — Teoría de cada modelo y las técnicas. Aquí está la carne para preguntas conceptuales.
3. **Cap. 9-14** — Qué se probó y qué no, con justificación.
4. **Cap. 15** — **Banco de preguntas típicas + respuestas.** Estudia esto la noche antes.
5. **Cap. 16** — Trabajo futuro (para preguntas de "¿qué sigue?").

Cada capítulo termina con **⚠️ Puntos débiles** (dónde te van a picar) y **🎯 Preguntas que podrían hacer**.

---

## Índice

- [Cap. 1 — El problema](#cap-1--el-problema)
- [Cap. 2 — Dataset](#cap-2--dataset)
- [Cap. 3 — Target (etiqueta)](#cap-3--target-etiqueta)
- [Cap. 4 — Features (los 61 indicadores)](#cap-4--features-los-61-indicadores)
- [Cap. 5 — Splits temporales](#cap-5--splits-temporales)
- [Cap. 6 — Regularización (L1, L2, elasticnet)](#cap-6--regularización-l1-l2-elasticnet)
- [Cap. 7 — Los 5 modelos, uno por uno](#cap-7--los-5-modelos-uno-por-uno)
- [Cap. 8 — Métricas (por qué esas y no otras)](#cap-8--métricas-por-qué-esas-y-no-otras)
- [Cap. 9 — Búsqueda de hiperparámetros](#cap-9--búsqueda-de-hiperparámetros)
- [Cap. 10 — Selección de features (probada y descartada)](#cap-10--selección-de-features-probada-y-descartada)
- [Cap. 11 — Ensembles (probados y descartados)](#cap-11--ensembles-probados-y-descartados)
- [Cap. 12 — Alternativas descartadas](#cap-12--alternativas-descartadas)
- [Cap. 13 — Iteraciones v0 → v8](#cap-13--iteraciones-v0--v8)
- [Cap. 14 — Ganador y por qué](#cap-14--ganador-y-por-qué)
- [Cap. 15 — Banco de preguntas de defensa](#cap-15--banco-de-preguntas-de-defensa)
- [Cap. 16 — Trabajo futuro](#cap-16--trabajo-futuro)

---

# Cap. 1 — El problema

## 1.1 Enunciado en una línea

**Cada día de mercado, decidir si conviene comprar (BUY), vender en corto (SELL) o no operar (HOLD) para cada una de 7 acciones tecnológicas.**

## 1.2 Formalización matemática

Sea `t` un día de trading y `C_t` el precio de cierre.

- **Retorno logarítmico forward**: `r_fwd(t) = ln(C_{t+1} / C_t)`

Queremos una función `f(features_t) → {BUY, HOLD, SELL}` que, dada la información disponible al cierre del día `t`, decida qué hacer.

El backtest asume que:
- Al cierre de `t`, ejecutas la señal.
- Cierras al cierre de `t+1`.
- BUY → PnL = `+r_fwd(t)`
- SELL → PnL = `-r_fwd(t)`
- HOLD → PnL = `0`

## 1.3 Por qué es un problema difícil

- **Ruido dominante**: en horizontes cortos (1 día), el ratio señal/ruido es muy bajo. Fama (1970) predice cero predictibilidad; en la práctica hay una pequeña señal explotable pero enterrada bajo mucho ruido.
- **No estacionariedad**: la distribución cambia con el régimen (bull, bear, sideways).
- **Clases desbalanceadas si mal definidas**: BUY es raro si defines "movimiento fuerte al alza"; abundante si defines "al menos un poquito arriba". Elegir bien el target es 50 % del trabajo.

## 1.4 Por qué clasificación y no regresión

**Alternativa considerada:** predecir el valor exacto de `r_fwd(t)` (regresión).

**Por qué se descartó:**
1. Regresión requiere modelar toda la distribución del ruido, que es enorme.
2. Las decisiones de trading son discretas (compras o no), no continuas.
3. El error cuadrático medio de una regresión no se traduce cleanly a PnL.
4. La clasificación con umbrales adaptativos separa mejor el "arriba" del "abajo" sin desperdiciar capacidad en el "ni tanto".

## 1.5 Por qué 3 clases (BUY / HOLD / SELL) y no 2 o más

**Alternativa 1: binaria (subir / bajar).**
- ✗ Ignora el hecho de que a veces conviene no operar (evitar comisiones, evitar ruido).
- ✗ Genera trades diarios forzosos → alto turnover → altos costos.

**Alternativa 2: 5 clases (fuerte-BUY / débil-BUY / HOLD / débil-SELL / fuerte-SELL).**
- ✗ Requiere umbrales adicionales que aumentan la complejidad.
- ✗ Las clases débiles son casi HOLD; añaden confusión sin señal nueva.

**Elección: 3 clases.** Es el mínimo que permite "abstenerse" (HOLD) y elimina la falsa dicotomía de la binaria.

## ⚠️ Puntos débiles del planteamiento

- El "cierre al día siguiente" es idealización — en mercado real habría slippage, comisiones, spread bid-ask.
- Solo probamos horizonte de 1 día (excepto en Vía 8 target ablation).
- 7 tickers de un solo sector (tech) — no generaliza a otros sectores/mercados.

## 🎯 Preguntas típicas

**P: ¿Por qué eligieron clasificar en 3 clases?**
R: Porque permite modelar la decisión de no operar (HOLD), que es necesaria para evitar overtrading en días de bajo signal. Binaria fuerza operar todos los días, 5 clases añade complejidad sin señal nueva.

**P: ¿Por qué no regresión?**
R: Regresión requiere modelar toda la distribución del retorno (dominada por ruido). Las decisiones de trading son discretas; la clasificación es más directa para el objetivo.

**P: ¿No pierden información al discretizar?**
R: Sí, pero es intencional: el ruido diario domina a la señal, y separar "arriba fuerte" de "abajo fuerte" es más aprendible que estimar el valor exacto.

**P: ¿Por qué asumen que se cierra al día siguiente?**
R: Es la horizonte más simple para clasificación diaria y permite comparación limpia. Trabajos futuros considerarían horizontes mayores (Vía 8 target ablation lo explora).

---

# Cap. 2 — Dataset

## 2.1 Fuente única: Yahoo Finance

**Todos los datos son de Yahoo Finance vía la librería `yfinance`.** Cero datos de pago.

### Por qué esa restricción

1. **Reproducibilidad**: cualquiera con Python puede correr el pipeline sin licencias.
2. **Alcance del TT**: no es un TT de acceso a datos privados; es de metodología con datos públicos.
3. **Justificación pedagógica**: mostrar que se puede obtener resultados razonables sin pagar $30-100 USD/mes por proveedores premium.

### Qué NO se usó (y por qué)

| Fuente descartada | Por qué |
|---|---|
| **Noticias / sentiment (FinBERT)** | Sale del scope del TT (procesamiento de lenguaje). Se documenta como trabajo futuro. |
| **Datos intradía (1min, 5min)** | Yahoo solo da últimos 60 días para 1min. Para 12 años se necesita proveedor pagado. |
| **Fundamentales (earnings, márgenes)** | Frecuencia trimestral, no cabe en target diario. |
| **Opciones (IV surface)** | Yahoo tiene solo intradía, no histórico. Provedores $100+/mes. |
| **Order book / L2** | No accesible gratuito. |
| **Macro FRED** | Sí es accesible gratis pero fuera del alcance definido. Trabajo futuro. |

## 2.2 Activos: los 7 tech gigantes

| Ticker | Empresa | Sector | Por qué se eligió |
|---|---|---|---|
| AAPL | Apple | Tech | Mayor cap. de EE.UU. |
| NVDA | NVIDIA | Tech/AI | Alta volatilidad, boom AI |
| TSLA | Tesla | Auto/Tech | Muy tradeada, alto interés |
| AMZN | Amazon | Tech/Consumer | Diversificada |
| MSFT | Microsoft | Tech | Estable, alta cap |
| GOOGL | Alphabet | Tech | Comparación con MSFT |
| META | Meta | Tech | Volatilidad, sentiment-driven |

### Por qué solo 7 y por qué solo tech

**Ventaja:**
- Sector homogéneo → modelo global tiene sentido (pooling ayuda).
- Alta liquidez → menos ruido de precio artificial.
- Cobertura mediática extensa → si hubiera news, sería fácil de sumar.

**Desventaja (limitación explícita):**
- No sabemos si los resultados generalizan a small caps, otros sectores o mercados internacionales. Se documenta en Limitations del paper.

## 2.3 Rango temporal

- **2013-12-31 a 2025-12-29** — aproximadamente 12 años, ~3,020 días de mercado por ticker.
- **Total combinado (7 tickers)**: ~21,140 filas.

### Por qué desde 2014

- Antes de 2014 hay menor cobertura del ETF SPY y VIX en formato uniforme.
- 2014 marca el fin del post-crisis; ambos regímenes (recuperación, bull market largo, COVID crash, recovery, 2022 bear, 2024-25) están cubiertos.

### Por qué hasta 2025 diciembre

- 2025 es el año más reciente completo cuando armamos el pipeline.
- Elegimos 2025 como test para tener el año más "reciente y difícil" fuera del entrenamiento.

## 2.4 OHLCV — qué es cada cosa

Los datos crudos de Yahoo por día:

| Campo | Significado | Ejemplo AAPL 2025-01-02 |
|---|---|---|
| **Open** | Precio de apertura | 240.50 |
| **High** | Precio máximo intradía | 243.20 |
| **Low** | Precio mínimo intradía | 239.80 |
| **Close** | Precio de cierre (ajustado) | 242.10 |
| **Volume** | Número de acciones tradeadas | 45,120,000 |

**El "close ajustado"** ajusta por splits y dividendos → dos precios en fechas distintas son comparables como si fueran la misma acción.

## 2.5 Contexto de mercado: SPY y VIX

**SPY** = ETF que replica el índice S&P 500. Representa "el mercado" en general.
**VIX** = "Índice del miedo". Mide la volatilidad implícita de opciones a 30 días del S&P 500. Alto VIX = mercado nervioso.

### Por qué agregar SPY/VIX a los features

Aunque las 7 acciones son tech, no son independientes del mercado:
- Si SPY sube fuerte, todas suben con probabilidad alta.
- Si VIX explota, todos los tickers caen (correlación en pánico).
- Sin esa información, el modelo solo ve la acción aislada y pierde el "clima".

## ⚠️ Puntos débiles

- **Sesgo de survivorship**: los 7 tickers están vivos y crecieron. Si un ticker hubiera quebrado, no está en el dataset. La conclusión "el modelo predice bien tech" está condicionada a "tech que sobrevivió".
- **Sesgo de sector**: 7 tech ≠ mercado entero.
- **Rango temporal específico**: 2014-2025 incluye COVID y AI boom; podría no generalizar a régimen distinto.

## 🎯 Preguntas típicas

**P: ¿Por qué solo Yahoo Finance? ¿No es "poco serio" para una tesis?**
R: (1) Reproducibilidad — cualquier revisor puede correr el pipeline. (2) El TT es sobre metodología comparativa, no sobre construir el mejor trading system. (3) La calidad de OHLCV de Yahoo es adecuada para daily; los problemas conocidos son en intradía. (4) Los proveedores pagados costarían $30-100/mes sin cambiar la conclusión (LR gana con los datos que hay).

**P: ¿Por qué solo 7 tickers?**
R: Es el balance entre (a) tener suficiente historia por ticker (~1500 días cada uno), (b) sector homogéneo para que el modelo global pooling ayude, (c) alta liquidez para reducir ruido. Ampliar a 50+ tickers está documentado como trabajo futuro (López de Prado 2018).

**P: ¿Y el sesgo de survivorship?**
R: Es una limitación explícita en el TT. Los 7 tickers están vivos y crecieron; un backtest riguroso al estilo López de Prado incluiría delisted stocks. En trabajo futuro se propone extender a S&P 500 completo con datos históricos de composición.

**P: ¿Cómo justifican meter SPY y VIX si el problema es predecir 7 tickers individuales?**
R: Porque los 7 tickers NO son independientes del mercado — sus retornos están correlacionados con SPY (>0.7 típicamente) y con VIX de manera negativa. Meter contexto sistémico reduce el ruido idiosincrático.

---

# Cap. 3 — Target (etiqueta)

Esta es la sección más importante para defender — el target define TODO el problema.

## 3.1 Definición formal

```
r_fwd(t) = ln(C_{t+1} / C_t)          # retorno log a 1 día

Sobre ventana rodante de 252 días previos (SOLO datos anteriores a t):
q30(t) = percentil 30 de r_fwd en [t-252, t-1]
q70(t) = percentil 70 de r_fwd en [t-252, t-1]

Etiqueta:
y_t = BUY  (2)  si r_fwd(t) >= q70(t-1)
y_t = SELL (0)  si r_fwd(t) <= q30(t-1)
y_t = HOLD (1)  en otro caso
```

Traducción a español:
- **BUY**: el retorno del día siguiente está en el top 30 % de lo visto en el último año.
- **SELL**: está en el peor 30 % del último año.
- **HOLD**: cualquier otra cosa.

## 3.2 Por qué usar retorno logarítmico y no simple

**Retorno simple**: `(C_{t+1} - C_t) / C_t`
**Retorno log**: `ln(C_{t+1} / C_t)`

**Ventajas del log:**
1. **Aditivo**: suma de log-returns = log-return acumulado. Muy útil para backtest.
2. **Simétrico**: subir 50 % y luego bajar 33 % te deja igual. En log, +0.405 y -0.405.
3. **Compatible con distribución lognormal** (que los precios sí siguen aproximadamente).

## 3.3 Por qué percentiles rodantes y no un threshold fijo

**Alternativa mala #1**: `r_fwd >= 0.01` (arriba del 1 %).
- ✗ En 2020 (COVID) los movimientos diarios eran ±5 %; en 2022 (bear) eran ±3 %; en 2017 (calma) eran ±0.5 %.
- ✗ Con threshold fijo, el 90 % de los días serían "HOLD" en 2017 y "BUY/SELL" en 2020.

**Alternativa mala #2**: `r_fwd >= α · σ_móvil` (arriba de α desviaciones estándar).
- ✗ σ_móvil también no es estacionaria.
- ✗ Elegir α es arbitrario.
- ✗ La normalidad implícita falla en colas.

**Solución elegida: percentiles rodantes 30/70.**
- ✅ **Auto-adaptativo**: en años tranquilos, q70 es pequeño; en años volátiles es grande.
- ✅ **Distribución garantizada ~30/40/30** en cualquier régimen.
- ✅ **Sin parámetros arbitrarios** (30 y 70 son la elección más natural).
- ✅ **Interpretable**: "BUY = top 30 % del año pasado".

## 3.4 Por qué ventana de 252 días

- **252** = días de trading en un año (aprox). NYSE opera ~252 días/año.
- Suficiente para capturar un ciclo estacional completo.
- No tan corto que sea ruidoso (30 días → percentiles inestables).
- No tan largo que no se adapte a cambios de régimen (5 años → lento).

## 3.5 Por qué percentiles 30/70 (y no 20/80 o 40/60)

Vía 8 ablation lo probó empíricamente:

| Percentiles | F1-macro (LR) | Interpretación |
|---|---:|---|
| 20/80 (extremos) | 0.418 | Clases muy separadas pero pocos BUY/SELL |
| **30/70 (baseline)** | **0.390** | **Balance clásico** |
| 33/67 | 0.389 | Casi 30/70, similar |
| 40/60 (cercanos) | 0.345 | HOLD casi desaparece, F1 baja |

30/70 es el estándar por dos razones:
1. Da ~30 % de BUY y SELL cada uno, suficiente para entrenar sin desbalance.
2. Es lo que usa la mayoría de la literatura (Fischer & Krauss 2018, Sezer 2020).

## 3.6 Anti-leakage: el shift crítico

Fíjate en `q70(t-1)` — el percentil se calcula con datos hasta `t-1`, no hasta `t`.

**Sin ese shift**, el modelo vería el retorno del día `t` para decidir la etiqueta del día `t`. Sería trampa (data leakage).

Con el shift, el modelo solo usa información que existía al cierre de `t-1` para etiquetar `t`. Es honesto.

## ⚠️ Puntos débiles del target

1. **1 día es muy ruidoso**. Vía 8 mostró que h=5-7 días da F1 hasta 0.43. Pero cambiar el horizonte cambia el problema.
2. **No captura la magnitud**. Un BUY con r=+0.5 % vale lo mismo que uno con r=+3 %. Para PnL sí importa.
3. **Percentiles rodantes tienen memoria**. Un mes de crash sube q70 y baja q30 → menos BUY/SELL en las semanas siguientes.

## 🎯 Preguntas típicas

**P: ¿Por qué percentiles rodantes y no un threshold fijo?**
R: Porque la volatilidad no es estacionaria. Un threshold de 1 % funcionaría en 2017 (calma) pero clasificaría casi todo como HOLD, y en 2020 (COVID) clasificaría casi todo como BUY/SELL. Los percentiles se auto-ajustan a la volatilidad del régimen.

**P: ¿Por qué 30 y 70 y no otros percentiles?**
R: Es el balance estándar en la literatura (Fischer & Krauss 2018). Da ~30 % de BUY y SELL cada uno. Probamos 20/80, 25/75, 33/67 y 40/60 (Vía 8, tabla de ablation); 30/70 mantiene F1 competitivo con distribución de clases balanceada.

**P: ¿Por qué ventana de 252 días?**
R: Es un año de trading (aprox). Captura un ciclo estacional completo (Enero effect, seasonality de earnings, verano tranquilo, Q4 volátil). Ventanas más cortas dan percentiles inestables; ventanas de 2-5 años se adaptan lento a cambios de régimen.

**P: ¿Cómo evitan el look-ahead bias?**
R: El percentil en el día `t` usa `q_70(t-1)`, calculado solo con los 252 días previos. El modelo nunca ve el retorno futuro para decidir la etiqueta actual.

**P: ¿Por qué log-return y no return simple?**
R: (1) Es aditivo — cumulative return es la suma. (2) Es simétrico ante ganancias/pérdidas equivalentes. (3) Los precios siguen aproximadamente distribución lognormal, así que log-returns son aproximadamente gaussianos.

**P: ¿No perdemos información al no distinguir un BUY grande de uno pequeño?**
R: Sí, es una simplificación intencional. Modelar la magnitud sería regresión, y el ruido del día 1 domina. La clasificación es más aprendible; para el PnL real se debería agregar sizing (Kelly, vol targeting), documentado como trabajo futuro.

---

# Cap. 4 — Features (los 61 indicadores)

Los 61 features son indicadores técnicos calculados solo desde OHLCV + SPY + VIX. **Ninguno usa datos futuros.**

## 4.1 Panorama: 9 familias

| # | Familia | # features | Qué mide |
|---|---|---:|---|
| 1 | Log returns | 5 | Retorno reciente en distintas escalas |
| 2 | Momentum | 4 | Cuánta velocidad trae el precio |
| 3 | Medias móviles | 9 | Tendencia y cruces |
| 4 | Volatilidad | 8 | Qué tan turbulento está el precio |
| 5 | Osciladores | 9 | Sobrecomprado / sobrevendido |
| 6 | Volumen / flujo | 8 | Conviction del movimiento |
| 7 | Patrones de vela | 7 | Forma de la sesión |
| 8 | Estacionalidad | 5 | Día de la semana, mes |
| 9 | Contexto mercado | 6 | Qué hace el S&P 500 y el VIX |
| — | **Total** | **61** | |

## 4.2 Familia 1: Log returns (5)

- `ret_1d`, `ret_2d`, `ret_3d`, `ret_5d`, `ret_10d`

Retorno logarítmico acumulado hacia atrás.

```
ret_kd(t) = ln(C_t / C_{t-k})
```

**Qué le dice al modelo:** cómo ha ido el precio en los últimos 1, 2, 3, 5 y 10 días.

**Justificación:** múltiples escalas para que el modelo detecte tanto reversal de corto plazo (ret_1d) como continuación de tendencia (ret_10d).

## 4.3 Familia 2: Momentum (4)

- `mom_5d`, `mom_10d`, `mom_20d`, `mom_60d`

```
mom_kd(t) = (C_t - C_{t-k}) / C_{t-k}
```

**Diferencia con returns:** `ret` es logarítmico; `mom` es porcentaje simple. Redundancia intencional (algunos modelos lineales aprovechan la diferencia; los árboles son invariantes).

**Momentum de 60 días** captura tendencia trimestral, típicamente asociada a la persistencia post-earnings.

## 4.4 Familia 3: Medias móviles (9)

- Distancias a MA: `dist_ma10`, `dist_ma20`, `dist_ma30`, `dist_ma50`, `dist_ma200`
- Cruces: `cruce_ma10_ma50`, `cruce_ma20_ma50`, `cruce_ma50_ma200`
- Pendiente: `pendiente_ma20`

```
dist_ma_k(t) = (C_t - MA_k(t)) / MA_k(t)   # % arriba/abajo de la MA
cruce_ma_a_b = MA_a(t) - MA_b(t)           # positivo = cruz alcista
```

**MA200** es el marker "bull vs bear" clásico. Si el precio está arriba de MA200, es tendencia alcista secular.

**Golden cross** (MA50 > MA200) = señal alcista fuerte, tradicional en análisis técnico.

**Justificación de usar 5 escalas:** capturar tanto reversales cortos (MA10) como tendencia secular (MA200).

## 4.5 Familia 4: Volatilidad (8)

- **ATR(14)**: Average True Range, mide amplitud diaria promedio.
- **atr_norm**: ATR dividido por el precio (normalizado, comparable entre tickers).
- **vol_5d, vol_10d, vol_20d, vol_60d**: desviación estándar rodante del log-return.
- **vol_ratio_5_20, vol_ratio_20_60**: volatilidad reciente / volatilidad más larga → detecta explosión o calma.

**ATR** vs **vol**: ATR usa el rango high-low (más robusto a gaps); vol usa returns (más estadístico).

**Por qué múltiples ventanas:** volatilidad expandiéndose (vol_5d > vol_20d) suele preceder movimientos grandes.

## 4.6 Familia 5: Osciladores (9)

Los "indicadores clásicos" del análisis técnico. Cada uno normaliza el precio a un rango acotado.

### RSI (Relative Strength Index)

- `rsi_14`, `rsi_7` — dos ventanas.

```
RSI = 100 - 100 / (1 + Ganancias promedio / Pérdidas promedio)
```

**Interpretación:**
- RSI > 70 → sobrecomprado (posible reversión bajista).
- RSI < 30 → sobrevendido (posible reversión alcista).

### MACD (Moving Average Convergence Divergence)

- `macd`, `macd_sig`, `macd_hist`.

```
MACD = EMA12 - EMA26
Signal = EMA9(MACD)
Hist = MACD - Signal
```

**Cruce MACD > Signal** → señal alcista. Hist > 0 alcista, < 0 bajista.

### Stochastic

- `stoch_k`, `stoch_d`, `stoch_diff`.

Similar a RSI pero basado en la posición del cierre dentro del rango high-low de los últimos días.

### Williams %R

- `williams_r`.

Otra variante de stochastic, escala inversa.

**Por qué tantos osciladores:** son parcialmente redundantes (correlacionados) pero cada uno captura una asimetría distinta. La regularización se encarga de descartar los inútiles.

## 4.7 Familia 6: Volumen y flujo (8)

- **OBV** (On-Balance Volume): acumulador que suma volumen en días alcistas y resta en bajistas. Detecta divergencias precio/volumen.
- **VWAP distance**: qué tan lejos está el precio del "precio promedio ponderado por volumen".
- **CMF(20)** (Chaikin Money Flow): flujo de dinero, positivo = compradores dominan.
- **MFI(14)** (Money Flow Index): RSI ponderado por volumen.
- **vol_log, vol_ratio, obv_ratio, obv_pendiente, vol_trend**: derivadas.

**Por qué volumen importa:** un movimiento con volumen bajo es sospechoso ("nadie está tradeando"), uno con volumen alto es "convicción".

## 4.8 Familia 7: Patrones de vela (7)

- **rango_rel** = (H - L) / L: cuán ancha fue la sesión.
- **cambio_intra** = (C - O) / O: cambio dentro del día.
- **cuerpo_rel** = |C - O| / (H - L): qué tan "grueso" es el cuerpo de la vela.
- **sombra_sup, sombra_inf**: longitudes de las mechas.
- **gap_apertura**: (O - C_prev) / C_prev.
- **hl_ratio**: H / L.

**Justificación**: análisis técnico tradicional pone mucho peso en formas de vela (doji, hammer, engulfing). Estas features codifican esas formas de manera continua.

## 4.9 Familia 8: Estacionalidad (5)

- `dia_sin`, `dia_cos`: día de la semana codificado como sin/cos.
- `mes_sin`, `mes_cos`: mes del año.
- `semana_mes`: qué semana del mes es.

**Por qué sin/cos y no one-hot**: para que "viernes" y "lunes" queden cerca (son adyacentes en el ciclo semanal), no ortogonales.

**Por qué estacionalidad importa**: efectos conocidos como el "Monday effect", "Sell in May", "January effect", earnings de fin de trimestre.

## 4.10 Familia 9: Contexto de mercado (6)

- **SP500_ret, SP500_vol20, SP500_mom20**: retorno, volatilidad y momentum del SPY.
- **VIX, VIX_change, VIX_norm**: nivel del VIX, cambio y normalizado.

**Por qué:** cada ticker se mueve con el mercado. Sin esto, el modelo no distingue "AAPL cayó porque hubo mala noticia" vs "AAPL cayó porque todo cayó".

## 4.11 Por qué 61 features y no más ni menos

### Alternativas probadas

| # features | Cómo | Resultado |
|---|---|---|
| **61 (baseline)** | Solo OHLCV+SPY+VIX | F1 = 0.404 (LR) |
| 94 (v3) | + Yield curve, DXY, gold, oil, sectores | Sin mejora — overfitting |
| 93 (v5 contexto) | + Bonos (SHY/IEI/IEF/TLT), VVIX, HYG/LQD | Sin mejora |
| 76 (v8 + interactions) | 61 + 15 productos de top-10 | **F1 = 0.413** ⭐ (única que sube) |

### Justificación de las 61

- **No es un número mágico**: es el resultado de agotar las categorías "razonables" de indicadores técnicos.
- **Más features no ayudan** porque el modelo overfittea (evidencia empírica en v3).
- **La regularización interna (elasticnet en LR) selecciona implícitamente** las útiles.

## ⚠️ Puntos débiles

- Alta correlación entre features (RSI y stochastic miden cosas similares).
- Redundancia intencional para dar redundant coverage a la regularización.
- Sesgo hacia "lo que la comunidad de análisis técnico cree que funciona".

## 🎯 Preguntas típicas

**P: ¿Por qué 61 y no otro número?**
R: Es el resultado de cubrir las 9 familias estándar de indicadores técnicos (returns, momentum, MAs, volatilidad, osciladores, volumen, velas, estacionalidad, mercado). No es un número mágico; es lo que produce cubrir esas categorías. Probamos con 94 (v3) y 93 (v5) y no mejora — el problema no es falta de features sino ruido inherente.

**P: ¿No hay features redundantes? ¿Por qué no las quitan?**
R: Sí, hay correlación (RSI y stochastic, por ejemplo). Lo probamos formalmente en Vía 0 con Pearson, VIF, Spearman y SHAP: en 11 de 15 casos usar las 61 completas es mejor que filtrar. La regularización elasticnet del modelo hace la selección implícita mejor que un filtro externo.

**P: ¿Por qué usan sin/cos para día de la semana?**
R: Para que "viernes" (día 5) y "lunes" (día 1) queden cerca en el espacio de features, respetando la periodicidad. One-hot los tratería como ortogonales, perdiendo esa estructura cíclica.

**P: ¿No es sospechoso incluir SPY y VIX cuando el problema es predecir 7 tickers?**
R: No, porque los 7 tickers no son independientes del mercado. Correlación típica AAPL-SPY es ~0.75. Sin contexto de mercado, el modelo confunde ruido idiosincrático con ruido sistémico.

**P: ¿Cómo eligieron los períodos de las MAs (10, 20, 50, 200)?**
R: Son los estándar de análisis técnico. MA50 vs MA200 es el "golden/death cross" clásico. MA10 y MA20 son de corto plazo típicas. No hicimos búsqueda porque ampliar más introducía overfitting.

**P: ¿Por qué RSI de 7 Y de 14?**
R: RSI(14) es el estándar (Wilder, 1978). RSI(7) es más reactivo, capturando reversales más cortos. Los dos son parcialmente redundantes, pero la regularización descarta el menos útil sin costo.

---

# Cap. 5 — Splits temporales

## 5.1 Por qué split temporal (no aleatorio)

**Alternativa mala**: dividir aleatoriamente train/test.
- ✗ En series temporales, esto MEZCLA fechas del pasado y futuro en train y test.
- ✗ El modelo puede "aprender del futuro" si un día de 2023 está en train y otro de 2022 en test.

**Solución correcta**: split cronológico. Train ≤ Val ≤ Test estrictamente en el tiempo.

## 5.2 Los 3 experimentos (A, B, C)

Los 3 experimentos comparten **el mismo año de test (2025)**. Solo varía cuánto pasado usan para train:

| Experimento | Train | Val | Test | Años train |
|---|---|---|---|---:|
| A | 2014-01-01 → 2023-12-31 | 2024 | 2025 | **10** |
| B (principal) | 2018-01-01 → 2023-12-31 | 2024 | 2025 | **6** |
| C | 2020-01-01 → 2023-12-31 | 2024 | 2025 | **4** |

### Por qué mismo test (2025) en los 3

Esto es CRÍTICO. Sin esto, cada experimento se compararía sobre distintos datos y no podríamos aislar el efecto de la cantidad de train.

**Antes de v4** (que fue el paper original), el Exp A tenía test 2024-2025 y B/C test 2025 solo. Eso hacía que Exp A pareciera "mejor" por evaluar sobre 2024 que fue más fácil. En v4 corregimos.

### Por qué train diferente (10 / 6 / 4 años)

Responde a la pregunta empírica: **¿más historia ayuda o hace overfitting?**

- **Exp A (10y)**: hipótesis "más datos siempre ayuda".
- **Exp B (6y)**: sweet spot — post-COVID, régimen relativamente moderno.
- **Exp C (4y)**: hipótesis "solo importa lo reciente".

**Resultado empírico**: la relación no es monótona. LR gana con 10y (0.411) pero también con 4y (0.401); Exp B (0.385) es el más difícil por razones de composición.

## 5.3 Rol de validación (2024)

Val se usa para:
1. **Elegir hiperparámetros** (Optuna optimiza F1 en val).
2. **Elegir la mejor época** (para deep models con early stopping).
3. **Nunca** para reportar resultados.

## 5.4 Rol de test (2025)

- Solo se toca UNA VEZ por configuración congelada.
- Los números que van al paper son de test.
- Si tocaras test varias veces, tus resultados se sesgan hacia esa año.

## 5.5 Anti-leakage en el preprocesamiento

Todo estadístico ajustado se hace **solo con train**:
- **StandardScaler / RobustScaler**: fit con train, transform en val y test.
- **Percentiles del target**: rolling window desplazado, solo usa pasado.
- **Class weights**: calculados con train.

## ⚠️ Puntos débiles

- **Un solo año de test**. Es la limitación más grande. Un buen protocolo sería walk-forward con 5+ ventanas.
- **2025 es un año particular**. Aunque el paper argumenta que es representativo (§3), no cubre todos los regímenes posibles.
- **Los 3 experimentos comparten Val (2024)**. Eso significa que Val no es una muestra independiente entre experimentos.

## 🎯 Preguntas típicas

**P: ¿Por qué no usan cross-validation?**
R: En series temporales, k-fold clásico rompe el orden temporal y mete leakage del futuro. Existen variantes (walk-forward, purged k-fold de López de Prado), pero requieren 10× más compute. Se documenta como trabajo futuro; el paper usa bootstrap block-resampling (§6) para atacar el mismo problema sin recomputar.

**P: ¿Por qué elegir 2025 como test y no otro año?**
R: Es el más reciente completo, cubre un régimen no visto por el modelo (post-COVID recovery + expectativa Trump 2.0), y tiene volatilidad arriba de la mediana histórica — no es el año fácil que flatterearía a un modelo largo-biased. El paper analiza en §3 si 2025 es representativo.

**P: ¿Por qué 3 experimentos y no 1?**
R: Para aislar la variable "cantidad de historia de train". Si solo hicieramos B (6 años), no sabríamos si con más historia el resultado cambia (Exp A) o si solo lo reciente importa (Exp C). Es un ablation de la ventana de train.

**P: ¿Val y Test siempre son los mismos?**
R: Val = 2024, Test = 2025, en los 3 experimentos. Solo el train cambia. Esta es la corrección clave que hicimos en v4 respecto a versiones anteriores (donde Exp A tenía Test más largo).

**P: ¿No es problema que Val sea la misma en los 3?**
R: Es una limitación menor. Val se usa para elegir hyperparams por experimento; que el año Val sea el mismo no filtra información entre experimentos. La preocupación real sería reusar Test, y eso NO se hace.

**P: ¿Cómo aseguran que no hay leakage temporal?**
R: (1) Split estricto: train < val < test cronológicamente. (2) Percentiles del target usan solo datos hasta t-1. (3) Escaladores fit solo con train. (4) Todas las estadísticas rolling usan solo pasado. En v5 esto se validó con un experimento de replicación bit-exact vs el pipeline anterior.

---

# Cap. 6 — Regularización (L1, L2, elasticnet)

Esta sección es la que la profesora exigente va a preguntar más. Aquí está a fondo.

## 6.1 ¿Qué es la regularización y por qué?

**Problema:** con muchos features (aquí 61) y pocos datos (~10,500 por modelo global), un modelo puede aprender los datos de train demasiado bien y fallar en test → **overfitting**.

**Solución:** penalizar la complejidad del modelo. En regresión logística, penalizar coeficientes grandes.

### Función de pérdida sin regularización

Regresión logística multinomial minimiza la log-verosimilitud negativa (cross-entropy):

```
L(β) = -Σᵢ Σₖ  yᵢₖ · log(pᵢₖ)
```

donde `pᵢₖ` = probabilidad de clase k para muestra i, calculada como softmax de `βₖ · xᵢ`.

Solo con esto, si tienes muchos features y pocos datos, `β` se hace grande y el modelo memoriza.

### Función de pérdida CON regularización

```
L_reg(β) = L(β) + λ · R(β)
```

donde `R(β)` es la "penalización" y `λ` controla qué tan fuerte castigar.

Hay 3 opciones principales para R(β): L1, L2, elasticnet.

## 6.2 Regularización L2 (Ridge)

```
R(β) = ||β||²₂ = Σⱼ βⱼ²
```

**Efecto**: penaliza cuadráticamente los coeficientes grandes. Los ENCOGE (shrinkage) hacia 0 pero **nunca los hace exactamente 0**.

**Intuición geométrica**: la penalización L2 es una "campana" que empuja a `β` hacia el origen. Sin bordes puntiagudos.

**Cuándo usar L2:**
- Cuando crees que **todos los features aportan algo** (aunque poco).
- Cuando hay **multicolinealidad** (features correlacionados): L2 los "reparte" en vez de elegir uno.
- Estable numéricamente.

## 6.3 Regularización L1 (Lasso)

```
R(β) = ||β||₁ = Σⱼ |βⱼ|
```

**Efecto**: penaliza linealmente el valor absoluto. **Hace algunos coeficientes exactamente 0** → selección de features implícita.

**Intuición geométrica**: la penalización L1 es un "rombo" que tiene esquinas en los ejes. Cuando la solución óptima está en una esquina, algunos `βⱼ = 0`.

**Cuándo usar L1:**
- Cuando crees que **solo un subconjunto de features es útil** (sparse solution).
- Cuando quieres selección automática de features.
- Cuando quieres un modelo interpretable ("solo estos 5 indicadores importan").

## 6.4 Elasticnet (combinación de L1 + L2)

```
R(β) = ρ · ||β||₁ + (1-ρ) · ½ · ||β||²₂
```

`ρ` es `l1_ratio` (entre 0 y 1):
- `ρ = 0` → puro L2 (Ridge)
- `ρ = 1` → puro L1 (Lasso)
- `ρ = 0.5` → mezcla balanceada

**Ventaja sobre L1 puro:**
- L1 puro con features correlacionados elige uno arbitrariamente y descarta los demás. Poco estable.
- Elasticnet "reparte" entre correlacionados (como L2) pero también hace sparsity (como L1).

**Referencia:** Zou & Hastie (2005) "Regularization and variable selection via the elastic net".

### En este TT: ¿qué elegimos?

- **v1-v4**: elasticnet con `l1_ratio=0.5` y `C=0.01`. Búsqueda por grid.
- **v5 (Optuna)**: el ganador fue **L2 puro con C = 0.000165**. Se prefirió L2 solo porque con `C` tan chico (regularización muy fuerte), L1 no aporta valor extra.

### El parámetro C

En sklearn:

```
C = 1 / λ
```

`C` grande → poca regularización (modelo complejo, riesgo overfit).
`C` chico → mucha regularización (modelo simple, riesgo underfit).

**En nuestro caso**: C = 0.000165 significa λ ≈ 6,060. Regularización EXTREMA.

**¿Por qué tan extremo?** Con muchos features correlacionados y target ruidoso, el modelo óptimo tiene coeficientes muy pequeños. Un modelo casi "flat" evita reaccionar a ruido.

## 6.5 Solver SAGA

Para resolver el problema de optimización, sklearn usa distintos solvers. **SAGA** es el único que soporta elasticnet multinomial.

**Ventajas de SAGA:**
- Converge rápido para problemas de tamaño medio.
- Estable con datos escalados.
- Soporta L1, L2 y elasticnet.

**Desventaja:** requiere features escalados (StandardScaler o RobustScaler).

## 6.6 Regularización en los OTROS modelos

### XGBoost

Regulariza de 3 formas simultáneas:
1. **`reg_alpha`**: penalización L1 sobre pesos de hojas.
2. **`reg_lambda`**: penalización L2 sobre pesos de hojas.
3. **`gamma`**: mínima reducción de pérdida requerida para split adicional → poda árboles pequeños.
4. **`max_depth`**: profundidad máxima → limita complejidad.
5. **`subsample` / `colsample_bytree`**: muestreo estocástico de filas y columnas → tipo dropout.

**Ganador Optuna v5:**
- `reg_alpha = 1.70`, `reg_lambda = 5.23`, `gamma = 0.035`.
- `max_depth = 9` (moderado), `min_child_weight = 2`.

### Deep models (LSTM / CNN / CNN-LSTM)

Regularizan de 4 formas:
1. **Dropout**: apagar aleatoriamente unidades → previene co-adaptación.
2. **Weight decay** (L2 en pesos): mismo espíritu que Ridge.
3. **Early stopping**: parar entrenamiento cuando val_loss empeora.
4. **Batch normalization**: normaliza activaciones → regulariza implícitamente.

## 6.7 Class weights (regularización de otro tipo)

Todos los modelos usan **class_weight="balanced"**: el peso de cada clase es inversamente proporcional a su frecuencia.

**Por qué**: si HOLD tiene 40 % y BUY/SELL 30 % cada uno, sin balancing el modelo aprendería "digan siempre HOLD" (que da 40 % de accuracy trivialmente). Balancing empuja al modelo a aprender BUY y SELL bien.

## ⚠️ Puntos débiles de la regularización

- **Tuning de C es sensible al escalado**. Si cambias RobustScaler por StandardScaler, C óptimo cambia.
- **L1 puede ser inestable** — pequeños cambios en train pueden hacer que otros features "sobrevivan".
- **Regularización extrema (C=0.000165)** puede indicar que el problema es tan ruidoso que casi ninguna feature vale.

## 🎯 Preguntas típicas

**P: Explique qué es L1 y L2.**
R: Son dos formas de penalizar la magnitud de los coeficientes de un modelo lineal. L2 (Ridge) penaliza el cuadrado, `||β||²₂ = Σβⱼ²`, encogiendo todos los coeficientes hacia 0 sin hacerlos exactamente 0. L1 (Lasso) penaliza el valor absoluto, `||β||₁ = Σ|βⱼ|`, haciendo que algunos coeficientes se hagan exactamente 0 → selección implícita de features. L2 es estable con multicolinealidad; L1 produce modelos sparse.

**P: ¿Qué es elasticnet?**
R: Es la combinación lineal de L1 y L2: `R(β) = ρ·||β||₁ + (1-ρ)·½·||β||²₂`. Con `ρ = l1_ratio` entre 0 y 1. Combina las ventajas de ambas: hace sparsity como L1 pero reparte entre features correlacionados como L2. Zou & Hastie (2005).

**P: ¿Por qué elasticnet y no L1 puro?**
R: Con features correlacionados (como RSI y stochastic), L1 puro elige uno arbitrariamente y descarta los demás — inestable a pequeños cambios en train. Elasticnet reparte entre correlacionados manteniendo sparsity.

**P: ¿Por qué el C óptimo es tan chico (0.000165)?**
R: Optuna probó 150 valores de C sobre validación 2024. El óptimo es extremo porque el ratio señal/ruido del problema es bajo — un modelo casi "flat" (coeficientes muy chicos) no reacciona a ruido. Es evidencia de que el problema es intrínsecamente difícil, no falta de tuning.

**P: ¿Qué es SAGA y por qué ese solver?**
R: SAGA es un algoritmo estocástico para regresión logística. Es el único de sklearn que soporta elasticnet multinomial (multi-clase). Converge rápido con datos escalados y es estable.

**P: ¿Cómo regularizan XGBoost?**
R: 5 mecanismos: (1) `reg_alpha` L1 en pesos de hojas, (2) `reg_lambda` L2 en pesos de hojas, (3) `gamma` mínima ganancia para split (poda), (4) `max_depth` limita profundidad, (5) `subsample`/`colsample_bytree` muestreo estocástico. Optuna balancea todos.

**P: ¿Cómo regularizan los deep models?**
R: (1) Dropout en cada capa (ganador 0.16-0.43 según arquitectura), (2) weight decay tipo L2 (0.0007 a 0.056), (3) early stopping sobre val_loss/val_f1, (4) batch normalization en CNN. Focal loss (variante de cross-entropy) también regulariza indirectamente al bajar el peso de ejemplos fáciles.

**P: ¿Qué es class_weight balanced y por qué lo usan?**
R: Asigna a cada clase un peso inversamente proporcional a su frecuencia en train. Sin esto, el modelo aprende "predecir HOLD siempre" (que da 40 % de accuracy trivial dada la distribución 30/40/30). Balancing fuerza al modelo a aprender BUY y SELL a pesar de ser menos frecuentes.

---

# Cap. 7 — Los 5 modelos, uno por uno

## 7.1 Regresión Logística (LR) — el ganador

### Qué es matemáticamente

Modelo lineal multiclase. Para cada clase `k`:

```
score_k(x) = β_k · x + b_k               (combinación lineal de las 61 features)

p(y=k | x) = exp(score_k) / Σⱼ exp(score_j)   (softmax)
```

Predicción: `argmax_k p(y=k | x)`.

### Qué hace intuitivamente

Combina linealmente los 61 indicadores con pesos aprendidos. Cada peso `β_kj` dice "cuánto contribuye el indicador j a la clase k".

**No usa la secuencia temporal**: solo mira el snapshot del día actual.

### Hyperparams del ganador Optuna v5

| Parámetro | Valor | Significado |
|---|---|---|
| `penalty` | `l2` | Ridge puro |
| `C` | 0.000165 | Regularización muy fuerte |
| `class_weight` | `balanced` | Balancea BUY/HOLD/SELL |
| `solver` | `SAGA` | Único que soporta elasticnet multinomial |
| `max_iter` | 5000 | Iteraciones máximas |
| escalador | `RobustScaler` | Robusto a outliers |

### Ventajas

- **Rapidísimo**: entrena en < 1 segundo.
- **Interpretable**: puedes leer los coeficientes.
- **Estable**: producer resultados casi idénticos entre corridas.
- **Sin memoria temporal explícita**: pero los features ya son transformaciones históricas (retornos de N días, MA de N días).

### Desventajas

- **Solo relaciones lineales**: no puede modelar `RSI * MACD` a menos que agreguemos esa interacción explícita (Vía 8 lo hace).
- **Requiere escalado** para converger bien.

### Por qué ganó

En nuestro caso, ganó porque:
1. **Overfitting-resistente**: con 61 features y ~10,500 samples, el modelo lineal + regularización fuerte tiene bias correcto.
2. **Los features ya son transformaciones ricas**: RSI, MACD, momentum — son no linealidades por sí solas.
3. **El ratio señal/ruido es bajo**: modelos complejos memorizan ruido; el LR es "conservador" y no lo hace.

---

## 7.2 XGBoost — segundo lugar

### Qué es matemáticamente

Ensamble de árboles de decisión. Cada árbol nuevo intenta corregir los errores del anterior:

```
F_M(x) = Σ_m=1^M   η · h_m(x)
```

donde `h_m(x)` es el m-ésimo árbol (débil learner), `η` es la tasa de aprendizaje, y `F_M(x)` es la predicción combinada.

Cada árbol se entrena para minimizar el gradiente de la pérdida en el punto donde `F_{m-1}` está actualmente. Por eso "gradient boosting".

Para clasificación multiclase, usa `multi:softprob`: cada árbol produce 3 salidas (una por clase) y aplica softmax.

### Qué hace intuitivamente

Aprende una jerarquía de reglas del tipo "if RSI > 65 and vol_ratio > 1.5 then classe = SELL". Cada árbol es una regla simple; combinar 500 árboles produce una regla compleja.

**No usa secuencia temporal**: como LR, mira solo el snapshot.

### Hyperparams del ganador Optuna v5

| Parámetro | Valor | Significado |
|---|---|---|
| `n_estimators` | 485 | Número de árboles |
| `max_depth` | 9 | Profundidad máxima |
| `learning_rate` | 0.074 | Tamaño de paso |
| `subsample` | 0.97 | % filas por árbol |
| `colsample_bytree` | 0.93 | % features por árbol |
| `min_child_weight` | 2 | Mínimo peso para nodo hijo |
| `gamma` | 0.035 | Mín. ganancia para split |
| `reg_alpha` | 1.70 | L1 en hojas |
| `reg_lambda` | 5.23 | L2 en hojas |
| escalador | `StandardScaler` | (XGB no escala pero se usó por convención) |

### Ventajas

- **Captura no linealidades**: cada árbol es una función escalón, la combinación es no lineal.
- **Robusto a outliers**: los árboles no se ven afectados por valores extremos.
- **Feature importance directo**: puedes ver qué features usa más.
- **GPU friendly**: XGBoost tiene `device="cuda"`.

### Desventajas

- **Overfitting** si no se regulariza bien (usamos alpha, lambda, gamma).
- **Más lento** que LR (30 s vs 1 s por entrenamiento).
- **Menos interpretable** que LR — 485 árboles son opacos.

### Por qué quedó segundo

XGBoost es MUY competitivo con LR (F1 = 0.386 vs 0.404, diferencia significativa pero pequeña). Perdió porque:
- El overhead de árboles no vale la pena cuando los features ya son transformaciones ricas.
- Requiere más regularización — más hyperparams que fallar.

---

## 7.3 LSTM Bidireccional — tercer/cuarto

### Qué es matemáticamente

**LSTM** (Long Short-Term Memory) es una red neuronal recurrente diseñada para procesar secuencias sin sufrir el problema del gradiente que desaparece.

Cada celda LSTM tiene 4 componentes:
- **Forget gate** (`f_t`): decide qué olvidar del estado anterior.
- **Input gate** (`i_t`): decide qué añadir al estado.
- **Cell state** (`c_t`): la "memoria" de largo plazo.
- **Output gate** (`o_t`): decide qué del estado exponer.

```
f_t = σ(W_f · [h_{t-1}, x_t] + b_f)
i_t = σ(W_i · [h_{t-1}, x_t] + b_i)
c_t = f_t ⊙ c_{t-1} + i_t ⊙ tanh(W_c · [h_{t-1}, x_t] + b_c)
o_t = σ(W_o · [h_{t-1}, x_t] + b_o)
h_t = o_t ⊙ tanh(c_t)
```

**Bidireccional (BiLSTM)** = dos LSTMs, una que lee hacia adelante y otra hacia atrás. Combina ambos contextos.

**Referencia:** Hochreiter & Schmidhuber (1997).

### Qué hace intuitivamente

Lee la secuencia de las últimas `lookback` días (ganador: 10 días). Cada día el LSTM actualiza su "memoria" con lo nuevo. Al final produce un vector que resume toda la secuencia, y ese vector predice la clase.

**Usa secuencia temporal explícita** (a diferencia de LR y XGBoost).

### Hyperparams del ganador Optuna v5

| Parámetro | Valor | Significado |
|---|---|---|
| `lookback` | 10 | Días de historia |
| `hidden` | 118 | Tamaño del estado oculto |
| `layers` | 2 | Capas LSTM apiladas |
| `dropout` | 0.43 | Regularización |
| `bidir` | False | Unidireccional (Optuna eligió) |
| `pooling` | `attn` | Attention pooling |
| `loss` | `focal` | Focal loss γ=1.43 |
| `lr` | 1.6e-4 | Tasa de aprendizaje |
| `weight_decay` | 7.8e-4 | L2 sobre pesos |
| `optimizer` | AdamW | |
| `escalador` | RobustScaler | |

### Ventajas

- **Modela dependencias temporales explícitas**: puede aprender que "RSI subiendo por 5 días" es distinto de "RSI subió una vez".
- **Bidireccional captura contexto** de ambos lados de la ventana.

### Desventajas

- **Muchos parámetros**: 118 hidden × 2 capas × 4 gates × features → ~590K parámetros. Con 10,500 samples eso es propenso a overfitting.
- **Lento**: 50 segundos por semilla.
- **Sensible a inicialización**: variance entre semillas es alta.

### Por qué no ganó

- El problema no requiere memoria de largo plazo que los features no capturen ya (`ret_10d`, `mom_60d` son "memoria" enlatada).
- 10 días de lookback × 61 features es un espacio grande para overfitting con 10,500 muestras.
- Focal loss ayudó (Optuna la eligió sobre CE), pero no bastó para vencer al modelo lineal.

---

## 7.4 CNN 1D — cuarto/quinto

### Qué es matemáticamente

**Convolutional Neural Network** aplicada a series unidimensionales.

Cada convolución 1D aplica un filtro sobre la secuencia:

```
y_t = Σ_k=0^{K-1}   w_k · x_{t+k} + b
```

donde `w_k` es el kernel de tamaño K (aquí K=7).

Se apilan varias capas de conv+ReLU+dropout+pool. Al final, un global pooling colapsa la secuencia a un vector que va a un cabezal denso.

**Referencia:** LeCun et al. (1989) — originalmente para reconocimiento de código postal.

### Qué hace intuitivamente

Detecta **patrones locales** en la secuencia. Por ejemplo, un filtro puede aprender "RSI que sube fuerte en 3 días" y activarse cuando ve eso en cualquier posición de la secuencia.

**Sin recurrencia**: procesa toda la secuencia en paralelo (más rápido que LSTM).

### Hyperparams del ganador Optuna v5

| Parámetro | Valor | Significado |
|---|---|---|
| `lookback` | 10 | Días |
| `filtros` | [50, 100] | # filtros por capa |
| `kernel` | 7 | Tamaño del filtro |
| `dropout` | 0.16 | |
| `batchnorm` | False | (Optuna eligió no usar) |
| `pool_cnn` | `gap` | Global average pooling |
| `fc_dim` | 101 | Dense final |
| `criterio` | `val_f1_ma3` | Selector de época |
| `loss` | `focal` | γ=2.48 |
| `lr` | 1.2e-5 | |
| `weight_decay` | 0.056 | |

### Ventajas

- **Rápido**: paralelo, no recurrente.
- **Traducción invariante**: detecta el mismo patrón en cualquier posición temporal.

### Desventajas

- **Sin memoria de largo plazo explícita**: solo ve la ventana de kernel × capas.
- **Más difícil de interpretar** que LR.

### Por qué no ganó

- Los patrones locales que detecta (secuencias de 7 días) ya están representados en los features (`ret_5d`, `mom_10d`).
- CNN es más útil para señales crudas (imágenes, audio) donde no hay feature engineering previo.

---

## 7.5 CNN-LSTM — híbrido

### Qué es matemáticamente

Composición secuencial: CNN → LSTM → dense.

1. CNN detecta patrones locales.
2. La salida de CNN es una nueva secuencia (más corta que la original).
3. LSTM procesa esa secuencia.
4. Dense produce logits.

### Qué hace intuitivamente

CNN reduce la secuencia larga a "eventos" locales (por ejemplo, "bandera bajista en día 3-5"). LSTM procesa la secuencia de eventos como memoria más larga.

### Hyperparams del ganador Optuna v5

| Parámetro | Valor |
|---|---|
| `lookback` | 20 |
| `filtros` | [77, 154] |
| `hidden` | 136 (LSTM) |
| `layers` | 1 |
| `dropout` | 0.42 |
| `bidir` | False |
| `pooling` | `last` |
| `pool_cnn` | `gap_gmp` |
| `loss` | `focal` γ=2.01 |
| `lr` | 4.4e-4 |
| `weight_decay` | 0.018 |

### Por qué no ganó

- Combina las desventajas de ambos: parámetros CNN + parámetros LSTM = más overfitting.
- El beneficio de composición no compensa el aumento de complejidad con solo 10,500 muestras.

## ⚠️ Puntos débiles de los deep models

- **Alta varianza entre semillas** (por eso promediamos 3).
- **Requieren cuidado con inicialización, LR, batch, criterio de selección de época**.
- **Sensibles a implementación**: en Vía 5 descubrimos que una diferencia de coma flotante en la evaluación (torch.from_numpy en cada época vs DataLoader preconstruido) mueve F1 en ±0.023.

## 🎯 Preguntas típicas sobre los modelos

**P: Explique qué es una regresión logística multinomial.**
R: Es una generalización de la regresión logística binaria a múltiples clases (aquí 3). Para cada clase k, calcula un score lineal `βₖ · x + bₖ`, aplica softmax para convertir los 3 scores en probabilidades, y predice la clase con mayor probabilidad. Se entrena minimizando la log-verosimilitud negativa (cross-entropy).

**P: ¿Qué es XGBoost y por qué funciona bien?**
R: Es un ensemble de árboles de decisión con boosting: cada árbol nuevo se entrena para corregir los residuos del anterior. Funciona bien porque (1) captura no linealidades sin necesidad de features hechos a mano, (2) es robusto a outliers, (3) tiene regularización interna vía max_depth, gamma, alpha, lambda.

**P: ¿Qué es una LSTM y por qué "bidireccional"?**
R: LSTM (Long Short-Term Memory) es una red recurrente con 3 compuertas (forget, input, output) y un estado de celda que actúa como memoria de largo plazo. Bidireccional = dos LSTMs, una lee la secuencia hacia adelante y otra hacia atrás. Combinar ambos contextos captura mejor las dependencias temporales.

**P: ¿Qué es focal loss y por qué la usaron?**
R: Focal loss es una variante de cross-entropy que reduce el peso de ejemplos fáciles (bien clasificados) para enfocar el entrenamiento en los difíciles. `FL(p) = -(1-p)^γ · log(p)`. Optuna la eligió para los deep models porque ayuda con desbalance leve y ejemplos ruidosos.

**P: ¿Por qué CNN 1D y no CNN 2D?**
R: Porque los datos son series temporales unidimensionales (61 features por 20 días). 2D es para imágenes con espacialidad. 1D convolutions capturan patrones locales a lo largo del tiempo.

**P: ¿Cómo funciona el "pooling attn" (attention pooling) del LSTM?**
R: En vez de tomar el último estado oculto de la secuencia, aprende una combinación ponderada de todos los estados. Los pesos son aprendidos, así el modelo decide qué días "importan" más. Similar al concepto de attention en Transformers.

**P: ¿Cuántos parámetros tiene cada modelo?**
R: LR: 61 × 3 + 3 = ~186. XGBoost 485 árboles × ~50 nodos = ~24K. LSTM ganador: hidden 118 × 4 gates × (118+61) × 2 capas ≈ ~180K. CNN: ~50K. CNN-LSTM: ~120K. Todos son grandes comparados con las ~10,500 muestras — de ahí la importancia de regularizar.

**P: ¿Por qué agregar dos capas al LSTM y no solo una?**
R: Optuna lo eligió (buscó entre 1 y 3). Dos capas capturan jerarquías: la primera captura patrones locales, la segunda combina esos patrones. Con más overfittea (más parámetros); con menos underfittea.

**P: ¿Qué es "dropout" y cómo funciona?**
R: Durante entrenamiento, en cada forward apaga aleatoriamente una fracción p de neuronas. Previene co-adaptación: el modelo no puede depender fuertemente de una neurona específica porque puede desaparecer. Reduce overfitting.

**P: ¿Por qué el LR ganó a los deep models?**
R: Tres razones: (1) el ratio señal/ruido del problema es bajo, y modelos complejos memorizan ruido; (2) los 61 features ya son transformaciones no lineales ricas (RSI, MACD), las capas ocultas no aportan; (3) 10,500 samples es pequeño para modelos con >100K parámetros. Es coherente con la literatura sobre datos tabulares (Grinsztajn et al. 2022).

---

# Cap. 8 — Métricas (por qué esas y no otras)

## 8.1 F1-macro (métrica primaria)

**Fórmula:**

```
F1_k = 2 · precision_k · recall_k / (precision_k + recall_k)   (por clase k)
F1_macro = (F1_BUY + F1_HOLD + F1_SELL) / 3
```

- **Precision_k** = TP_k / (TP_k + FP_k): de los que predije como k, cuántos eran realmente k.
- **Recall_k** = TP_k / (TP_k + FN_k): de los que eran realmente k, cuántos capturé.

**Macro** = promedio simple sin ponderar por frecuencia de clase.

### Por qué macro y no weighted

- **Weighted** pondera por frecuencia de clase. Si HOLD es 40 %, weighted premia predecir bien HOLD.
- **Macro** trata a las 3 clases igual. **Es lo que queremos porque el interés económico está en BUY y SELL** (HOLD no genera PnL).

## 8.2 Por qué NO usamos accuracy

Con distribución 30/40/30:
- Predecir siempre HOLD → 40 % accuracy (baseline trivial).
- Predecir aleatoriamente → 33 % accuracy.
- Un modelo "bueno" saca 41-42 % accuracy pero con distribución degenerada.

**F1-macro detecta el colapso**: si predices todo HOLD, F1_BUY = F1_SELL = 0 → F1_macro ≈ 0.19. Accuracy no lo detectaría.

## 8.3 Métricas económicas (backtest)

### Win Rate

```
Win_Rate = # días con PnL > 0  /  # días con posición ≠ 0
```

**Interpretación**: de los días que operas, qué fracción ganan. Baseline aleatorio = 0.5.

### Profit Factor (PF)

```
PF = Σ ganancias / |Σ pérdidas|
```

- PF > 1: rentable.
- PF = 2: por cada $1 perdido, ganas $2.

### Maximum Drawdown (MaxDD)

```
DD_t = (equity_t - peak_t) / peak_t
MaxDD = min(DD_t)  (siempre ≤ 0)
```

Peor caída porcentual desde el pico. Es una medida de "peor momento" de la estrategia.

**Por qué importa**: si tu MaxDD es -50 %, muchos inversores ya se salieron antes.

### Sharpe Ratio (anualizado)

```
Sharpe = √252 · mean(r_strat) / std(r_strat)
```

Riesgo-ajustado. Ratio de retorno / volatilidad.

- Sharpe > 1: bueno.
- Sharpe > 2: excelente.
- Sharpe < 0: perdedor.

**El √252 anualiza** (aprox. 252 días de trading por año).

## 8.4 Por qué NO incluimos costos de transacción

**Limitación explícita** del TT. Un backtest con costos ~5-10 basis points por trade reduciría Sharpe en 0.3-0.5.

Se documenta como trabajo futuro. La comparación entre modelos sigue siendo válida (todos pagan lo mismo).

## 8.5 Por qué NO usamos Kelly o vol targeting

**Position sizing binario** (±1, 0). Un position sizing dinámico (Kelly, vol-targeted) mejoraría Sharpe pero:
- Añade otro grado de libertad → más sensibilidad a hyperparams.
- Cambia el problema de "predecir dirección" a "predecir dirección + magnitud".
- Se documenta como trabajo futuro.

## ⚠️ Puntos débiles

- Sharpe anualizado con √252 asume returns independientes — realidad tiene autocorrelación.
- Sin costos, los modelos que trades mucho parecen mejores de lo que serían.
- Un solo test year → Sharpe puede ser fortuito.

## 🎯 Preguntas típicas

**P: ¿Por qué F1-macro y no accuracy?**
R: Porque con distribución de clases 30/40/30, un modelo que predice siempre HOLD saca 40 % accuracy sin aportar nada. F1-macro promedia el F1 de cada clase por igual — un modelo colapsado a HOLD tendría F1_BUY = F1_SELL = 0 y F1-macro ≈ 0.19, detectando el problema.

**P: ¿Qué diferencia hay entre macro-F1 y weighted-F1?**
R: Macro promedia el F1 de cada clase sin ponderar. Weighted pondera por frecuencia. Elegimos macro porque las clases BUY y SELL (aunque menos frecuentes) son las importantes económicamente — HOLD no genera PnL.

**P: ¿Qué es el Sharpe ratio?**
R: Ratio riesgo-ajustado: retorno promedio dividido entre volatilidad. Anualizamos multiplicando por √252 (días de trading por año). Sharpe > 1 es considerado bueno, > 2 excelente, < 0 pierde dinero.

**P: ¿Por qué no incluyen costos de transacción?**
R: Limitación explícita del TT. Añadir costos (5-10 bp por trade) reduciría Sharpe en 0.3-0.5. La comparación relativa entre modelos sigue siendo válida (todos pagan lo mismo). Se documenta como trabajo futuro.

**P: ¿Qué es el drawdown máximo y por qué importa?**
R: Peor caída porcentual desde un pico anterior en la curva de equity. Importa porque en la práctica un inversor con MaxDD del 50 % probablemente cerrará la estrategia antes de recuperarse. Es medida de "peor momento" del sistema.

**P: ¿Qué es el profit factor?**
R: Suma de ganancias dividida entre suma absoluta de pérdidas. PF = 2 significa que por cada $1 perdido, ganas $2. PF > 1 es rentable.

**P: ¿Cómo definen "ganar" vs "perder" un día?**
R: Un día con predicción BUY gana si `r_fwd(t) > 0`. Un día SELL gana si `r_fwd(t) < 0`. HOLD no cuenta para win rate (no se opera). El PnL es simplemente `position(t) · r_fwd(t)`.

---

# Cap. 9 — Búsqueda de hiperparámetros

## 9.1 Grid search (v0-v4)

Búsqueda exhaustiva en una grid pequeña:
- Para LR: `C ∈ {0.01, 0.1, 1.0}`, `l1_ratio = 0.5`.
- Para XGBoost: n_estimators ∈ {100, 500}, depth ∈ {3, 6, 9}, etc.
- Para deep: solo probaron lookback ∈ {20, 60}.

**Limitación**: la grid deep era muy chica (no incluía learning rate). Esto sesgó los resultados contra deep models.

## 9.2 Optuna TPE (v5)

**Optuna** es una librería de optimización bayesiana. Usa **TPE** (Tree-structured Parzen Estimator) para modelar la distribución de "qué hyperparams dan buen F1" y muestrear los siguientes trials de esa distribución.

**Referencia:** Akiba et al. (2019).

### Budget usado

| Modelo | Trials | Hyperparams |
|---|---:|---:|
| LR | 150 | 5 (penalty, C, l1_ratio, class_weight, escalador) |
| XGBoost | 150 | 9 |
| LSTM | 80 | 17 |
| CNN | 80 | 20 |
| CNN-LSTM | 80 | 19 |

Los deep tienen más hyperparams porque hay más decisiones: lookback, hidden, layers, dropout, filtros, kernel, learning rate, weight_decay, loss (CE/focal), label_smooth, focal_gamma, escalador, etc.

### Por qué 150 vs 80

- ML clásicos (LR, XGB): 150 trials en < 1 hora (rápido).
- Deep models: cada trial toma 7-12 s, más ruido → 80 trials es suficiente con `MedianPruner` (que abandona trials malos temprano).

### Por qué TPE y no random search o grid search

- **Grid**: exponencial en # hyperparams. Con 20 params × 3 valores = 3^20 trials. Inviable.
- **Random**: robusto pero ineficiente. Bergstra & Bengio (2012) mostraron que random beats grid, pero TPE beats random en la mayoría de problemas.
- **TPE**: aprende de trials pasados para muestrear zonas prometedoras.

## 9.3 Selección del "mejor" trial

**Objetivo:** F1-macro en **validación 2024**.

**Riesgo:** overfitting a validación. Con 150 trials, el mejor F1_val puede ser 0.02 más alto que el promedio, y ese exceso NO generaliza a test 2025.

**Mitigaciones:**
1. **Media de N semillas** para cada trial (reduce ruido).
2. **Reportar el best trial y también la variación entre trials cercanos**.
3. **Nunca tocar test** hasta que el best_trial esté congelado (R1 del PLAN_MAESTRO).

## ⚠️ Puntos débiles

- 80 trials para deep models es POCO comparado con el tamaño del espacio (17-20 params).
- Optuna puede quedarse en mínimos locales.
- Selección de best trial es susceptible a overfit a validación.

## 🎯 Preguntas típicas

**P: ¿Qué es Optuna y cómo funciona?**
R: Es una librería de optimización bayesiana de hyperparams. Usa TPE (Tree-structured Parzen Estimator) que modela la distribución de qué hyperparams dan buenos resultados. Sugiere el siguiente trial explorando zonas prometedoras. Más eficiente que grid o random search.

**P: ¿Por qué 150 trials para LR/XGB y 80 para deep?**
R: LR y XGB entrenan en 1-30 segundos, así que 150 trials caben en < 1 hora. Deep models toman 7-12 s por trial, con más varianza; 80 trials + MedianPruner (que aborta trials malos temprano) es suficiente.

**P: ¿No hay riesgo de overfitting a validación con 150 trials?**
R: Sí, es un riesgo real. Con muchos trials, el best F1_val puede ser fortuito. Mitigamos con (1) media de N semillas por trial, (2) evaluar el best trial sobre test solo una vez, (3) reportar intervalos de confianza bootstrap en el paper.

**P: ¿Qué hyperparams tuneó Optuna para el LR?**
R: penalty (l1/l2/elasticnet), C (inverso de regularización), class_weight, escalador (standard/robust/minmax) — 5 en total. Ganador: penalty=l2, C=0.000165, class_weight=balanced, robust.

**P: ¿Por qué el ganador es tan raro (C=0.000165)?**
R: Con Optuna explorando un rango amplio (log-uniforme entre 1e-5 y 100), encontró un óptimo con regularización EXTREMA. Es evidencia de que el problema requiere un modelo muy conservador para no memorizar ruido.

---

# Cap. 10 — Selección de features (probada y descartada)

Esta sección justifica por qué NO filtramos features estadísticamente antes del entrenamiento.

## 10.1 Los 4 métodos probados

### Pearson correlation

Mide la **correlación lineal** entre cada feature y el target.

```
r = cov(X, y) / (σ_X · σ_y)
```

Se filtran features con |r| < umbral.

**Cuándo funciona**: para modelos lineales, en teoría. En práctica, poco sensible a relaciones no lineales.

### VIF (Variance Inflation Factor)

Mide **multicolinealidad**. Si dos features son casi iguales (correlación >0.9), VIF > 10.

Se descartan features con VIF alto, quedándose con solo uno de cada grupo correlacionado.

**Cuándo funciona**: cuando el modelo es sensible a colinealidad (OLS puro sí, LR con regularización no tanto).

### Spearman rank correlation

Mide **correlación monotónica** (rank-based). Sensible a relaciones no lineales pero monótonas.

Se filtran features con |ρ| < umbral.

### SHAP (SHapley Additive exPlanations)

Método sofisticado que atribuye importancia a cada feature basado en teoría de juegos.

Para árboles (XGBoost), se calcula el SHAP value promedio absoluto por feature.

Se filtran features con SHAP bajo.

## 10.2 Resultados empíricos (Vía 0)

Tabla del paper §5 (Table 3):

| Modelo | Filtro | Δ F1 (all - filtered), 3 exps |
|---|---|:---:|
| LR | Pearson + VIF (4-8 feats) | +0.024 / +0.026 / +0.021 |
| XGBoost | SHAP top-N (23-25 feats) | +0.009 / +0.021 / +0.022 |
| LSTM | Spearman (3-25 feats) | +0.039 / +0.036 / -0.006 |
| CNN 1D | Spearman | +0.035 / -0.025 / +0.011 |
| CNN-LSTM | Spearman | -0.011 / +0.020 / -0.026 |

Positivo = usar todas las features es mejor que filtrar.

**11 de 15 casos: usar todas es mejor.**

## 10.3 Por qué NO ayuda filtrar

### Razón 1: la regularización interna hace mejor selección

Un LR con elasticnet **implícitamente** pone coeficientes en 0 para features inútiles. Un filtro externo (Pearson) elige antes de ver el modelo, con menos información.

### Razón 2: correlaciones débiles suman

Un feature con Pearson = 0.05 (débil) puede ser importante en combinación con otro. Los filtros univariados no ven combinaciones.

### Razón 3: los deep models detectan interacciones

LSTM/CNN pueden aprender que "RSI * VIX" es útil. Un filtro univariado descartaría uno o ambos.

## 10.4 Se usan como HERRAMIENTA EXPLORATORIA

Aunque no como pre-filtro, los tests estadísticos SÍ se usan para:
- Reportar qué features tienen más peso post-hoc.
- Justificar el diseño del feature set.
- Detectar redundancias graves.

## 🎯 Preguntas típicas

**P: ¿Por qué no hicieron selección de features antes de entrenar?**
R: La probamos. En 11 de 15 casos, usar las 61 features completas es mejor que filtrar con Pearson, VIF, Spearman o SHAP. La razón es que la regularización interna (elasticnet en LR, L2+pruning en XGBoost) hace selección implícita mejor que un filtro externo.

**P: Explique VIF.**
R: Variance Inflation Factor mide multicolinealidad. Para cada feature, ajusta una regresión donde esa feature es el target y los demás features son predictores; el VIF es 1/(1-R²). Si VIF > 10, la feature está muy correlacionada con las otras y aportar redundancia. Se puede descartar. Usamos VIF junto con Pearson para el filtrado LR-específico.

**P: ¿Por qué elegir Spearman para deep models y Pearson/VIF para LR?**
R: Pearson y VIF asumen relaciones lineales, apropiadas para LR. Spearman mide correlación monotónica (rank-based), captura relaciones no lineales que los deep models pueden explotar. SHAP es específico para árboles (XGBoost). Cada filtro se alineó con el modelo.

**P: Si el filtro no ayuda, ¿por qué mencionarlo en el paper?**
R: Para (1) documentar honestamente qué se probó, (2) justificar la decisión de usar todas las features, (3) refutar la crítica común "deberían haber pre-seleccionado". Es evidencia negativa útil.

---

# Cap. 11 — Ensembles (probados y descartados)

## 11.1 Multi-seed averaging (SÍ usado)

Cada modelo se entrena con N semillas diferentes (3 para deep, 5 para LR). Las predicciones se promedian:

- **LR/XGBoost**: soft-voting = promedio de probabilidades.
- **Deep**: hard-voting = majority vote.

**Por qué SÍ**: reduce la varianza sin sesgo. La diferencia entre 1 y 3 semillas puede ser ±0.02 F1.

## 11.2 Stacking (probado, descartado)

Un meta-modelo (segundo nivel) aprende a combinar las predicciones de los modelos base:

```
X_meta = [probs_LR, probs_XGB, probs_LSTM, probs_CNN, probs_CNN-LSTM]
y_meta = target

meta_model = LR(X_meta, y_meta)
```

**Resultado**: F1 ≈ 0.404 (igual a LR solo). No aporta.

**Razón**: si LR ya es el mejor y las otras son peores, apilar solo añade ruido.

## 11.3 Soft voting simple (probado, descartado)

Promedio de probabilidades de los 5 modelos:

```
probs_final = (probs_LR + probs_XGB + probs_LSTM + probs_CNN + probs_CNN-LSTM) / 5
```

**Resultado**: F1 ≈ 0.38 (peor que LR).

## 11.4 Blending optimizado por Optuna

Buscar pesos `w_i` que maximicen F1 (o Sharpe) en validación:

```
probs_final = w_LR · probs_LR + w_XGB · probs_XGB + ... + w_CNN-LSTM · probs_CNN-LSTM
sujeto a: Σ w_i = 1, w_i >= 0
```

**Vía 7 lo probó extensivamente:**

| Objetivo | Pesos elegidos | F1 test | Sharpe test |
|---|---|---:|---:|
| F1-macro | LR=0.03, XGB=0.03, LSTM=0.41, CNN=0.03, CNN-LSTM=0.49 | 0.373 | +0.042 |
| Sharpe | LR=0.11, XGB=0.45, LSTM=0.28, CNN=0.06, CNN-LSTM=0.10 | 0.358 | +0.152 |

**En ambos casos: peor que LR solo** (F1 0.404, Sharpe +0.895).

## 11.5 Por qué NO funcionan los ensembles aquí

- **LR es MUY superior**: incluso 90 % LR + 10 % XGB ya es peor que LR puro.
- **Optuna overfit a validación**: los pesos "óptimos" en 2024 no generalizan a 2025.
- **Los 5 modelos hacen predicciones correlacionadas**: si todos ven las mismas features, tienden a cometer los mismos errores.

## 🎯 Preguntas típicas

**P: ¿Qué es stacking y por qué no lo usaron?**
R: Stacking es un ensemble donde un meta-modelo aprende a combinar las predicciones de los modelos base. Lo probamos: un LR meta sobre las probs de los 4 modelos rinde igual que LR solo (~0.40 F1). No aporta porque LR ya es el mejor; apilar predicciones peores solo añade ruido.

**P: ¿Y soft voting simple?**
R: Promediar probabilidades de los 5 modelos da F1 ≈ 0.38, peor que LR solo. Los modelos débiles arrastran hacia abajo.

**P: ¿Blending con pesos óptimos?**
R: Optuna busca pesos que maximicen F1 (o Sharpe) en validación. Los pesos óptimos en 2024 NO generalizan a 2025 — los blends resultan sistemáticamente peor que LR solo. Vía 7 lo documenta con 3 variantes.

**P: ¿Pero no se supone que los ensembles siempre ayudan?**
R: Solo cuando los modelos base son (1) suficientemente diversos, (2) todos de calidad similar. Aquí LR es dominante y los deep models están correlacionados en sus errores. Si un modelo domina claramente, el ensemble no ayuda.

**P: ¿Usaron multi-seed averaging?**
R: Sí, siempre. Cada modelo se entrena con 3 (deep) o 5 (LR) semillas y las predicciones se promedian. Esto reduce varianza sin sesgo, y es distinto de "ensemble de modelos" — es "ensemble del mismo modelo con distintas inicializaciones".

---

# Cap. 12 — Alternativas descartadas

Otras arquitecturas probadas o consideradas y por qué NO se adoptaron.

## 12.1 LightGBM (probado)

Otro gradient boosting como XGBoost. Diferencia: usa histogramas y leaf-wise splits (más rápido).

**Resultado**: F1 similar a XGBoost. No aporta variedad ni ventaja.

## 12.2 CatBoost (probado)

Gradient boosting de Yandex. Fortalezas: maneja features categóricas de forma nativa.

**Resultado**: F1 similar a XGBoost, 3× más lento en Windows. Descartado por costo/beneficio.

## 12.3 GRU (probado)

Alternativa a LSTM más simple (2 compuertas en vez de 3).

**Resultado**: F1 similar a LSTM. No aporta.

## 12.4 Transformer (considerado, no viable)

Arquitecturas: Vanilla Transformer, Informer, PatchTST, TimeSeries Transformer.

**Por qué NO viable aquí:**
- Transformers requieren ~10K-100K muestras para no overfittear.
- Aquí tenemos 10,500 muestras global (o 1,500 por ticker).
- Sin pre-training en un dataset masivo, sobreajustan.

**Referencias**: Vaswani et al. (2017) "Attention is All You Need".

## 12.5 TabNet (probado)

Arquitectura DL diseñada específicamente para datos tabulares (Arik & Pfister 2020).

**Resultado**: Peor que XGBoost. Diseñado para tabular grande, no series financieras.

## 12.6 N-BEATS / N-HiTS (considerado, no viable)

Arquitecturas DL para forecasting de series temporales.

**Por qué NO viable:**
- Diseñadas para **regresión** de series, no clasificación multiclase.
- Requieren adaptaciones significativas.

## 12.7 Modelos considerados que NO se probaron

| Modelo | Por qué NO se probó |
|---|---|
| **Random Forest** | Muy similar a XGBoost, más lento, menos regularización |
| **SVM multiclase** | O(n²) en muestras, lento con 10K+ datos |
| **Naive Bayes** | Asunción de independencia entre features rota |
| **k-NN** | O(n) por predicción, muy lento; sensible a curse of dimensionality con 61 features |

## 🎯 Preguntas típicas

**P: ¿Por qué no usaron Transformer?**
R: Los Transformers requieren datasets grandes (10K-100K+ muestras) para no overfittear. Aquí tenemos 10,500 (global) o 1,500 (per-ticker). Sin pre-training en un dataset externo masivo (que no está disponible en Yahoo Finance), sobreajustan. Se documenta como trabajo futuro con Transfer Learning.

**P: ¿Por qué no LightGBM o CatBoost?**
R: LightGBM lo probamos: F1 muy similar a XGBoost, no aporta diversidad al ensemble. CatBoost también lo probamos: F1 similar, 3× más lento en nuestro setup Windows+CUDA. Descartados por costo/beneficio.

**P: ¿Y modelos clásicos como SVM o Random Forest?**
R: SVM tiene complejidad O(n²) en muestras — lento con 10K+ datos. Random Forest es esencialmente lo mismo que XGBoost pero sin boosting (peor generalmente). Naive Bayes rompe la asunción de independencia entre features correlacionadas.

**P: ¿Consideraron modelos de reinforcement learning?**
R: RL para trading requiere un entorno simulado con dinámicas de mercado (order book, latencia, slippage) y no simplemente clasificación. Salía del scope del TT (metodología comparativa de clasificadores). Trabajo futuro.

---

# Cap. 13 — Iteraciones v0 → v8

El TT no fue una sola corrida — fueron 9 iteraciones con distintos enfoques. Aquí el resumen.

| Ver. | Cambio principal | Resultado | Estado |
|---|---|---|:---:|
| v0 | Baseline inicial (grid search en 5 modelos) | Estableció pipeline base | Historia |
| v1 | Todos los modelos + splits originales | LR = 0.380, XGB = 0.386 | Historia |
| v2 | Threshold calibration | Sin mejora estable | Descartada |
| v3 | 94 features (yield curve, DXY, gold, oil...) | Sin mejora — overfitting | Descartada |
| **v4** | **Splits unificados: test=2025 en todos** | **LR = 0.404, XGB = 0.386** | **Paper** |
| v5 | Protocolo corregido + Optuna 150 trials + IC 95% bootstrap | LR = 0.404 con IC | Paper §6 |
| **v7** | Refinamiento post-Optuna: isotonic, SWA, blending, etc. | XGB + isotonic mejora (0.371, +0.60 Sharpe) | Adoptado |
| **v8** | Exploración del dataset: target ablation, interactions, cross-asset | **LR + interactions: F1 = 0.413** | Adoptado |

## 13.1 Por qué tantas iteraciones

- **v0-v2**: aprender el pipeline, corregir bugs, elegir métricas.
- **v3**: hipótesis "más features = mejor" — se refutó empíricamente.
- **v4**: corrección crítica del test unificado.
- **v5**: elevar el rigor a nivel académico (protocolo con Optuna real, IC).
- **v6**: walk-forward + statistical significance (bootstrap).
- **v7**: técnicas post-training que no requerían re-entrenar.
- **v8**: explorar el dataset (target, features de interacción, cross-asset).

## 13.2 Qué se aprendió de cada iteración

**v2 (threshold calibration)**: intentar ajustar el umbral de decisión post-training. Mejora marginal, no vale la complejidad.

**v3 (94 features)**: intentar mejorar dando más contexto. Overfitting confirmado.

**v4 (splits unificados)**: revelación de que las comparaciones anteriores eran injustas.

**v5 (protocolo)**: revelación de que el criterio de época era el problema real de los deep models (val_loss no era el mejor).

**v7 (isotonic para XGB)**: única técnica post-training que ayuda.

**v8 (interactions para LR)**: única mejora al modelo sin cambiar el problema.

## 🎯 Preguntas típicas

**P: ¿Por qué tantas versiones? ¿No se enfocaron desde el principio?**
R: Cada versión responde a un descubrimiento de la anterior. v0-v2 fueron aprender el problema. v3 refutó la hipótesis "más datos ayudan". v4 corrigió sesgos metodológicos. v5-v6 elevaron el rigor. v7-v8 exploraron mejoras marginales. Es investigación real, no ejecución lineal.

**P: ¿Cuál es la versión "final"?**
R: Para el paper enviado a MICAI: v4 + v5 (splits unificados + protocolo corregido). Para el modelo de producción del TT: v8 (LR + interactions). Son distintas porque el paper se enviö antes de las Vías 7 y 8.

**P: ¿Por qué v3 no funcionó?**
R: Agregar 33 features de contexto de mercado (bonos, VIX derivados, sectores) esperando mejora produjo neutralidad o degradación. Diagnóstico: los modelos se saturan en el signal-to-noise del target diario; más features solo añaden ruido. Es evidencia de que el techo del problema no es feature engineering.

---

# Cap. 14 — Ganador y por qué

## 14.1 Ganador final para producción

**LR con interactions**, específicamente:
- Regresión Logística multinomial
- Penalty L2, C = 0.000165
- RobustScaler
- 61 features base + 15 interactions (productos entre pares de las top-10 features)
- Class weight balanced, multi-seed averaging con 5 semillas

**Métricas** (test 2025 Exp B GLOBAL):
- F1-macro: **0.413**
- Sharpe: **+0.92**
- Win Rate: 0.53
- Max DD: -0.52

## 14.2 Por qué LR ganó (tres razones)

### Razón 1: Ratio señal/ruido bajo → prefiere modelos conservadores

Con retornos diarios donde el ruido domina la señal, un modelo con muchos parámetros memoriza ruido. LR con regularización EXTREMA (C=0.000165) produce coeficientes muy pequeños y no reacciona a fluctuaciones espurias.

### Razón 2: Los features ya capturan casi todo el signal lineal

Los 61 indicadores son transformaciones no lineales ricas de la historia (RSI es no lineal en precios; MACD es diferencia de medias exponenciales; ATR es rango; etc.). La combinación lineal de esas ricas transformaciones ya captura la mayoría de la señal disponible.

### Razón 3: Pocas muestras para modelos complejos

10,500 muestras (global) o 1,500 (por ticker) es pequeño para modelos con 10⁵-10⁶ parámetros. Los deep models entran en régimen de overfitting; LR con 186 parámetros es apropiado.

### Confirmación en la literatura

- Grinsztajn et al. (2022): "Why do tree-based models still outperform deep learning on tabular data?"
- Shwartz-Ziv & Armon (2022): "Tabular data: Deep learning is not all you need."
- Patel et al. (2015): resultados similares en el mercado indio con muestras comparables.

## 14.3 Cuándo cambiaría el ganador

- **Con datasets grandes** (>100K muestras): los deep models empezarían a ganar.
- **Con features crudos** (sin RSI/MACD calculados): CNN/LSTM tendrían ventaja al aprenderlos.
- **Con horizonte mayor** (5-10 días): el ratio señal/ruido mejora, quizás XGBoost ganaría.
- **Con datos externos** (sentiment, macro, opciones): los deep models podrían aprovechar mejor.

## 🎯 Preguntas típicas

**P: ¿Por qué el modelo más simple ganó al más sofisticado?**
R: Tres razones. (1) El ratio señal/ruido en retornos diarios es bajo, y modelos complejos con >100K parámetros memorizan ruido con 10,500 muestras. (2) Los 61 features ya son transformaciones no lineales ricas (RSI, MACD, ATR), la LR solo combina linealmente esas transformaciones ricas. (3) Es consistente con literatura sobre datos tabulares (Grinsztajn 2022).

**P: ¿Estarían de acuerdo con esta conclusión si tuvieran más datos?**
R: No necesariamente. Con >100K muestras y features crudos, los deep models superarían a LR (evidencia de Gu-Kelly-Xiu 2020 con 30K stocks × 60 años). Nuestra conclusión está scoped a este régimen: 7 tickers × ~1500 días con features engineered.

**P: ¿Qué pasaría con horizonte mayor de predicción?**
R: Vía 8 (target ablation) muestra que h=5-7 días es más aprendible (F1 sube a 0.43). Pero cambiar el horizonte cambia el problema definido ("señal diaria" → "señal semanal"). Se documenta como trabajo futuro con las mejoras acumuladas.

**P: ¿Hay un intervalo de confianza para esa F1 = 0.413?**
R: Sí, en el paper §6 usamos bootstrap block-resampling (95% CI). Para LR con protocolo estricto v5: [0.379, 0.428]. LR es significativamente mejor que todos los otros 4 modelos; las diferencias entre los otros 4 no son significativas.

---

# Cap. 15 — Banco de preguntas de defensa

## 15.1 Preguntas generales sobre motivación

**P1: ¿Cuál es la contribución de tu TT?**
R: Cuatro contribuciones: (1) un pipeline reproducible para clasificación de señales diarias con solo datos Yahoo Finance; (2) benchmark comparativo de 5 arquitecturas ML/DL bajo protocolo idéntico y con evaluación económica (no solo F1); (3) evidencia empírica de que la selección estadística de features no ayuda en este contexto; (4) descubrimiento de que la volatilidad del ticker importa más que la elección del modelo para el Sharpe cross-asset.

**P2: ¿Qué problema resuelves?**
R: Predicción diaria de señales de trading para 7 acciones tecnológicas. Específicamente clasificación en 3 clases (BUY/HOLD/SELL) con etiquetas basadas en percentiles rodantes del retorno logarítmico forward.

**P3: ¿Por qué este problema es relevante?**
R: (1) Trading algorítmico es una aplicación industrial de billones de USD. (2) La discusión "clásicos vs deep learning" en tabular data está viva (Grinsztajn 2022). (3) La mayoría de papers comparan solo 1-2 modelos; este compara 5 bajo protocolo estricto. (4) Los resultados económicos (no solo F1) importan para trasladar research a práctica.

**P4: ¿Qué diferencia tu trabajo del estado del arte?**
R: (1) Comparación de 5 modelos (vs 1-2 típicos). (2) Métricas económicas + F1 (vs solo accuracy o RMSE). (3) Protocolo estricto con Optuna simétrico y bootstrap IC (§6 del paper). (4) Descarte empírico de feature selection y ensembles. (5) Documentación exhaustiva de qué NO funciona.

## 15.2 Preguntas sobre datos

**P5: ¿Por qué solo Yahoo Finance?**
R: Reproducibilidad. Cualquier revisor puede correr el pipeline. Los proveedores pagados costarían $30-100 USD/mes sin cambiar la conclusión. La calidad OHLCV de Yahoo es adecuada para daily.

**P6: ¿No falta información importante como noticias, sentimiento, fundamentales?**
R: Sí, y se documenta explícitamente en Limitations. Trabajos futuros propuestos: FinBERT sobre news APIs (FinBERT), FRED para macro, ORATS para IV opciones. Cada uno cuesta esfuerzo o dinero adicional que salía del scope del TT.

**P7: ¿Por qué exactamente 7 tickers?**
R: Balance entre (a) suficientes datos por ticker (1500 días), (b) sector homogéneo para que pooling ayude, (c) alta liquidez para reducir ruido. Ampliar a 50+ está documentado como trabajo futuro.

**P8: ¿Cómo evitan el survivorship bias?**
R: No lo evitamos completamente — los 7 tickers son sobrevivientes. Es limitación explícita. Trabajo futuro: extender a componentes históricos del S&P 500 (López de Prado 2018).

**P9: ¿Qué es OHLCV?**
R: Open (apertura), High (máximo intradía), Low (mínimo), Close (cierre), Volume (volumen tradeado). Los 5 campos crudos por día que produce el mercado.

## 15.3 Preguntas sobre el target

**P10: ¿Por qué percentiles rodantes 30/70?**
R: Adaptativo a régimen (funciona en bull y bear); da distribución de clases 30/40/30 estable. Un threshold fijo (1 %) fallaría en distintos regímenes de volatilidad. Ver Cap. 3.

**P11: ¿Cómo evitan look-ahead bias?**
R: El percentil en día t se calcula con datos hasta t-1 (shift explícito de 1 día). Escaladores fit solo con train. Ver Cap. 3.5 y Cap. 5.5.

**P12: ¿Por qué log-return y no return simple?**
R: Aditividad para backtest, simetría de ganancias/pérdidas equivalentes, distribución lognormal de precios.

**P13: ¿Por qué 1 día y no 5 días?**
R: Es el horizonte más "puro" — información más fresca, decisiones frecuentes. Vía 8 explora horizontes mayores y confirma que 5-7 días son más aprendibles, pero cambia el problema.

## 15.4 Preguntas sobre features

**P14: ¿Cómo eligieron los 61 features?**
R: Cubriendo las 9 familias estándar de análisis técnico. No es un número mágico; es lo que sale de tocar todas las categorías (returns, momentum, MAs, volatilidad, osciladores, volumen, velas, estacionalidad, mercado).

**P15: ¿Explique RSI.**
R: Relative Strength Index. Ratio de ganancias promedio / pérdidas promedio en los últimos N días (típicamente 14). Se normaliza a [0, 100]. RSI > 70 = sobrecomprado (posible reversión bajista); RSI < 30 = sobrevendido (posible rebote).

**P16: ¿Explique MACD.**
R: Moving Average Convergence Divergence. `MACD = EMA12(precio) - EMA26(precio)`. Línea de señal = EMA9(MACD). Cruce MACD > Signal = señal alcista. Histograma = MACD - Signal.

**P17: ¿Qué son las medias móviles?**
R: Promedio de N últimos precios de cierre. MA10 = promedio de 10 días. MAs largos (MA200) muestran tendencia secular; cortos (MA10) muestran ruido a corto plazo. "Golden cross" (MA50 > MA200) = tendencia alcista establecida.

**P18: ¿Por qué sin/cos para día de la semana?**
R: Para preservar la periodicidad. Viernes (5) y lunes (1) están cerca en el ciclo semanal; sin/cos los codifica cerca en el espacio de features. One-hot los tratería como ortogonales.

## 15.5 Preguntas sobre regularización

**P19: Explique L1 y L2.**
R: Ver Cap. 6.2 y 6.3. Resumen: L2 penaliza suma de cuadrados, encoge todos coeficientes hacia 0 sin hacerlos 0. L1 penaliza suma de valores absolutos, hace algunos coeficientes exactamente 0 (selección implícita).

**P20: ¿Qué es elasticnet?**
R: Combinación lineal ponderada de L1 y L2. `R(β) = ρ·||β||₁ + (1-ρ)·½·||β||²₂` con ρ=l1_ratio. Combina sparsity de L1 con estabilidad de L2 en presencia de multicolinealidad.

**P21: ¿Por qué C = 0.000165 es tan chico?**
R: C es el inverso de la regularización. C chico = mucha regularización. Optuna exploró rangos logarítmicos amplios y este valor optimizó F1 en validación. Es evidencia de que el problema es intrínsecamente ruidoso — un modelo "casi flat" evita reaccionar a ruido.

**P22: ¿Qué es dropout y por qué reduce overfitting?**
R: Durante entrenamiento, apaga aleatoriamente una fracción p de neuronas en cada forward pass. Fuerza al modelo a no depender de neuronas específicas (previene co-adaptación). En test se usan todas. Actúa como regularización estocástica.

**P23: ¿Qué es early stopping?**
R: Parar el entrenamiento cuando la métrica de validación deja de mejorar (paciencia = 15 épocas en nuestro caso). Previene overfitting sin necesidad de calibrar # de épocas manualmente.

**P24: ¿Qué es weight decay?**
R: Es L2 aplicado a los pesos de la red durante el entrenamiento con AdamW. Regulariza igual que Ridge en LR.

## 15.6 Preguntas sobre modelos

**P25: Explique softmax.**
R: Función que convierte K scores en probabilidades: `p_k = exp(s_k) / Σⱼ exp(s_j)`. Salida suma a 1 y todos los valores son ≥ 0. Se usa en la salida de LR y deep models para clasificación multiclase.

**P26: Explique cross-entropy loss.**
R: `L = -Σ y_true · log(p_pred)`. Para clasificación multiclase con probabilidades softmax, es la log-verosimilitud negativa. Penaliza fuertemente predicciones confiadas incorrectas.

**P27: Explique gradient boosting.**
R: Ensemble secuencial de modelos débiles (árboles). Cada árbol nuevo se entrena para predecir el residuo (gradiente negativo de la loss) del ensemble actual. `F_M(x) = Σ η·h_m(x)`. XGBoost es una implementación optimizada con regularización explícita.

**P28: ¿Cómo funcionan las gates de un LSTM?**
R: 3 compuertas (forget, input, output), cada una sigmoide entre 0 y 1. Forget decide qué información del estado previo mantener. Input decide qué información nueva agregar. Output decide qué del estado interno exponer. El "cell state" es la memoria de largo plazo.

**P29: ¿Qué es batch normalization?**
R: Normaliza las activaciones dentro de un batch (media 0, varianza 1) durante el entrenamiento. Reduce sensibilidad a la inicialización, permite learning rates mayores, actúa como regularización leve.

**P30: ¿Qué es focal loss?**
R: Variante de cross-entropy: `FL(p) = -(1-p)^γ · log(p)` con γ ≥ 0. Reduce el peso de ejemplos fáciles (p cercano a 1) para enfocar al modelo en los difíciles. Con γ=0 es CE estándar. Optuna eligió γ ≈ 1.4-2.5 para los deep models.

## 15.7 Preguntas sobre métricas

**P31: ¿Por qué F1-macro y no accuracy?**
R: Accuracy es engañosa con distribución 30/40/30 — predecir siempre HOLD da 40 % accuracy sin señal. F1-macro promedia F1 por clase; si el modelo colapsa a HOLD, F1_BUY = F1_SELL = 0 y F1-macro es bajo. Detecta el colapso.

**P32: ¿Qué es Sharpe ratio?**
R: Retorno riesgo-ajustado: `Sharpe = mean(r) / std(r) · √252`. El √252 anualiza. Sharpe > 1 = bueno, > 2 = excelente, < 0 = perdedor.

**P33: ¿Qué es max drawdown?**
R: Peor caída porcentual desde el pico. `MaxDD = min((equity_t - peak_t)/peak_t)`. Medida de "peor momento" — importante porque en la práctica los inversores cierran estrategias con DD > 30-50 %.

**P34: ¿Qué es profit factor?**
R: `PF = Σ ganancias / |Σ pérdidas|`. PF > 1 = rentable. PF = 2 significa que ganas $2 por cada $1 perdido.

**P35: ¿Por qué no incluyen costos de transacción?**
R: Es una simplificación intencional para comparación pura entre modelos. Costos realistas (5-10 bp por trade) reducirían Sharpe en 0.3-0.5 pero afectarían a todos los modelos, manteniendo el ranking. Trabajo futuro.

## 15.8 Preguntas sobre metodología / experimentos

**P36: ¿Por qué 3 experimentos (A/B/C)?**
R: Para aislar la variable "cantidad de historia de train". A=10 años, B=6, C=4. Los 3 comparten test 2025 para comparación justa. Responde a la pregunta empírica "¿más historia ayuda o hace overfitting?"

**P37: ¿Por qué el mismo test year en los 3?**
R: Para que las diferencias entre experimentos sean solo por # años de train, no por el año de test. Es corrección crítica que hicimos en v4 respecto a v1-v3 (donde Exp A tenía 2 años de test).

**P38: ¿Cómo evitan overfitting a validación con Optuna?**
R: (1) Media de N semillas por trial (reduce ruido puntual). (2) Regla R1 del protocolo: nunca tocar test hasta que la config esté congelada. (3) Bootstrap IC en test (§6 paper) para reportar honestamente la incertidumbre.

**P39: ¿Por qué NO cross-validation?**
R: K-fold clásico rompe orden temporal en series financieras (leakage del futuro). Existen variantes correctas (walk-forward, purged k-fold de López de Prado) pero requieren 10× más compute. Se documenta como trabajo futuro. El paper usa bootstrap block-resampling que ataca el mismo problema sin recomputar.

**P40: Explique bootstrap.**
R: Método no paramétrico para estimar la distribución de un estadístico. Consiste en re-muestrear el dataset con reemplazo B veces (aquí B=1000). En cada re-muestra se calcula el estadístico (F1); la distribución de esas B copias da un intervalo de confianza (percentiles 2.5 y 97.5). Nosotros usamos block-bootstrap para preservar autocorrelación temporal.

## 15.9 Preguntas sobre decisiones específicas

**P41: ¿Por qué descartaron la selección de features?**
R: La probamos con Pearson, VIF, Spearman y SHAP. En 11 de 15 casos, usar las 61 features completas es mejor que filtrar. La regularización interna (elasticnet en LR) hace mejor selección implícita.

**P42: ¿Por qué descartaron el stacking?**
R: Un LR meta sobre los 4 modelos base da F1 igual a LR solo (~0.40). Cuando un modelo (LR) domina claramente, apilar peores solo añade ruido.

**P43: ¿Por qué descartaron LightGBM y CatBoost?**
R: F1 similar a XGBoost, no aportan diversidad. CatBoost además 3× más lento en Windows+CUDA.

**P44: ¿Por qué descartaron Transformer?**
R: Necesita 10K-100K muestras para no overfittear. Aquí tenemos 10,500 (global) o 1,500 (per-ticker). Sin pre-training en un dataset masivo (no disponible en Yahoo Finance), sobreajusta.

**P45: ¿Descartaron algo más?**
R: N-BEATS/N-HiTS (son para regresión de series, no clasificación multiclase). Random Forest (similar a XGBoost sin boosting). SVM (O(n²) en muestras, lento con 10K+ datos). Naive Bayes (asunción de independencia rota). k-NN (curse of dimensionality con 61 features).

## 15.10 Preguntas trampa / difíciles

**P46: ¿Es tu modelo mejor que "buy and hold"?**
R: Depende del ticker. Para TSLA (Vía 8), el modelo genera Sharpe +2.06 vs BH que sería similar pero con mayor drawdown. Para GOOGL, el modelo pierde vs BH. En promedio, la ventaja del modelo es capturar downside protection (SELL correctos en caídas). Sin costos, gana en Sharpe promedio; con costos realistas el margen se estrecha.

**P47: ¿Cómo sabes que no es overfitting a 2025?**
R: (1) Optuna se hizo en validación 2024, no test 2025. (2) La configuración se congeló antes de tocar test. (3) Bootstrap IC en test da rango honesto. (4) Vía 8 target ablation muestra consistencia — cuando cambiamos el horizonte, LR sigue ganando, sugiriendo que no es artefacto del año.

**P48: ¿Podrías usar esto en trading real hoy?**
R: Como sistema completo, NO — falta: (1) costos y slippage, (2) infra de ejecución, (3) risk management (stop-loss, position sizing), (4) monitoring en producción. Como capa de decisión sobre un sistema existente, SÍ — el modelo LR es rápido, interpretable y auditable.

**P49: Si LR gana, ¿por qué diablos entrenaron 5 modelos?**
R: Porque a priori no sabíamos. La contribución empírica es precisamente demostrar que LR gana en este régimen (10K samples, features engineered, target ruidoso). Si hubiéramos comparado solo LR con XGBoost habríamos perdido la evidencia contra deep models.

**P50: Si tuvieras 6 meses más, ¿qué harías?**
R: (1) Walk-forward validation con 5+ años consecutivos como test (rota el protocolo). (2) Agregar features macro de FRED (gratis). (3) Adaptar a horizonte multi-step (predecir 5 días juntos). (4) Position sizing dinámico (Kelly o vol-targeted). (5) Probar Transformer con pre-training en un dataset externo grande (transfer learning). (6) Sentimiento con FinBERT sobre RSS de noticias financieras.

**P51: ¿Cuál es la limitación más grave de tu trabajo?**
R: Un solo test year (2025). Aunque el paper argumenta que 2025 es representativo (§3, no anómalo en volatilidad ni retorno), no cubre todos los regímenes. Walk-forward sobre 5+ años consecutivos daría intervalos de confianza más honestos.

**P52: ¿Qué harías distinto si empezaras hoy?**
R: (1) Empezar con protocolo v5 (Optuna simétrico, IC bootstrap) desde el día uno. (2) Diseñar el target con Vía 8 ablation antes de comprometerse a h=1d/q=30/70. (3) Establecer costos de transacción como métrica primaria. (4) Considerar horizontes múltiples desde el inicio.

**P53: ¿Cómo justificarías esto ante un practitioner de Renaissance/Citadel?**
R: Con honestidad. Diría: "Este es un TT de metodología comparativa con datos públicos, no un sistema de trading para producción. La contribución es evidenciar cuándo LR gana a deep learning en este régimen. Para trading real necesitaríamos datos alt (order book, news), horizontes múltiples, cost model, risk management. Nada de eso está aquí."

---

# Cap. 16 — Trabajo futuro

## 16.1 Extensiones inmediatas (sin datos nuevos)

### 16.1.1 Walk-forward validation

Rotar el test year sobre 5-10 años consecutivos. Da intervalos de confianza más honestos. Coste: 10× compute actual.

### 16.1.2 Position sizing dinámico

Reemplazar posición binaria ±1 por sizing basado en:
- **Kelly criterion**: `f* = (bp - q)/b` con probabilidades del modelo.
- **Vol targeting**: escalar la posición inversamente con volatilidad reciente.

Mejora esperada: Sharpe +0.3-0.5.

### 16.1.3 Modelo de costos

Añadir 5-10 bp por trade y refit. Selección de modelo cambiaría hacia estrategias con menor turnover.

### 16.1.4 Ensemble por-ticker

En vez de un modelo global, entrenar 7 modelos LR + interactions específicos por ticker y comparar contra el global. Vía 8 mostró que interactions ayudan; extender a per-ticker.

## 16.2 Extensiones con datos gratuitos adicionales

### 16.2.1 Datos macro (FRED)

Descargar de FRED (Federal Reserve gratuita):
- Yield curve (2Y, 10Y, 30Y)
- Term spread (10Y - 2Y)
- Credit spread (HY - IG)
- Initial jobless claims
- CPI, PCE

Mejora esperada: F1 +0.01-0.03.

### 16.2.2 Sentimiento con FinBERT

Descargar RSS de noticias financieras, clasificar polaridad con FinBERT (BERT fine-tuned en financial text), agregar features `sentiment_5d_avg`, `sentiment_change`.

Mejora esperada: F1 +0.03-0.07 (especialmente para tickers con alta cobertura mediática como TSLA).

## 16.3 Extensiones con datos pagados

### 16.3.1 Datos intradía (~$10-30/mes)

Construir features de order-flow imbalance, Garman-Klass volatility, VWAP intra-day, etc.

### 16.3.2 Opciones IV surface (~$100/mes)

IV ATM 30d, put-call ratio, skew, term structure. Forward-looking.

### 16.3.3 Fundamentales (SimFin, Compustat)

Earnings surprise, guidance, revenue growth. Frecuencia trimestral pero relevante en fechas de reporte.

## 16.4 Extensiones metodológicas

### 16.4.1 Transformer con pre-training

Pre-entrenar en un dataset masivo (S&P 500 completo 20+ años), fine-tune en los 7 tickers. Transfer learning permitiría que Transformer no overfittee.

### 16.4.2 Bayesian Neural Networks

Modelo con uncertainty estimation. Solo tradear cuando la incertidumbre del modelo es baja. Mejoraría Sharpe dramáticamente al saltar días ruidosos.

### 16.4.3 Multi-task learning

Un solo modelo que prediga simultáneamente (a) señal BUY/HOLD/SELL, (b) magnitud del retorno, (c) volatilidad esperada. Regularización implícita entre tareas.

### 16.4.4 Reinforcement Learning

Cambio de paradigma: en vez de clasificar señales, un agente RL aprende una política de posición directamente. Requeriría entorno simulado del mercado.

## 16.5 Extensiones de scope

- **Más tickers**: extender a componentes históricos del S&P 500 (~500 stocks). Requiere manejo de survivorship bias.
- **Otros sectores**: comparar tech vs finance vs energy — ¿el modelo generaliza?
- **Otros mercados**: replicar en LATAM (BOVESPA, S&P/BMV IPC), Europa (FTSE 100), Asia (Nikkei 225).
- **Otros horizontes**: multi-step (predecir vector de 5 días), horizonte largo (5d, 20d, 60d).

---

## Cierre

Este documento cubre todo el trabajo hecho, la teoría detrás, las decisiones tomadas y las anticipa a preguntas de sinodales.

**Consejos para el día de la defensa:**

1. **Sé honesto sobre las limitaciones**. Un revisor experimentado detecta la falta de honestidad al instante.
2. **"No lo hicimos porque..." es una respuesta válida**. Enumera qué probaste y por qué descartaste, no inventes justificaciones post-hoc.
3. **Ten listas las 3-5 preguntas más difíciles**. Ver Cap. 15.10.
4. **Sabe distinguir paper (§ 6 Robustness = v5) vs TT (todo v0-v8)**. El paper es una extensión pública; el TT es el trabajo completo.
5. **Si no sabes algo, dilo**. "Esa es una excelente pregunta, no la habíamos considerado, pero se puede analizar así: ..." es 100 veces mejor que inventar.

Suerte.

---

*Documento generado 2026-08-30. Complementa a `INVESTIGACION_COMPLETA.md`, `METODOLOGIA_COMPLETA.md` y `docs/VIA7_REFINAMIENTO.md`, `docs/VIA8_DATASET.md`.*
