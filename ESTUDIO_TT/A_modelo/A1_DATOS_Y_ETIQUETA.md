# A1 — Datos y etiqueta

> **Resumen.** Datos diarios gratuitos de Yahoo Finance para 7 acciones
> tecnológicas (2013-12-31 a 2025-12-29, 3 017 días por acción, 21 119 filas
> en total), más el S&P 500 (SPY) y el VIX como contexto. La respuesta
> correcta de cada día se define con percentiles móviles: COMPRAR si el
> retorno de mañana está en el 30 % más alto del último año, VENDER si está
> en el 30 % más bajo, MANTENER en otro caso. Así la etiqueta se adapta a la
> volatilidad de cada época y no usa información futura.
>
> Código: `scripts_v1/01_build_raw_dataset.py` (construcción),
> `api/ml/target.py` (la misma etiqueta en vivo).

---

## 1. Fuente: Yahoo Finance

Todos los datos se descargan con la biblioteca `yfinance` de Python, con
precios **ajustados** por *splits* y dividendos (`auto_adjust=True`).

### ¿Por qué solo Yahoo Finance?

| Razón | Explicación |
|---|---|
| Reproducibilidad | Cualquiera puede descargar exactamente los mismos datos y correr el pipeline sin pagar licencias |
| Alcance | El TT es de metodología comparativa con datos públicos, no de acceso a datos privilegiados |
| Calidad suficiente | Para datos **diarios** de acciones grandes, Yahoo es confiable; sus problemas conocidos están en datos intradía y en acciones pequeñas |
| Evidencia de que no es la limitante | Se probó agregar 32–33 variables más de Yahoo (bonos, dólar, oro, petróleo, sectores, VVIX, crédito) en v3 y v5, y no mejoró |

### ¿Qué no se usó y por qué?

| Fuente | Por qué no |
|---|---|
| Noticias / sentimiento | Requiere procesamiento de lenguaje natural (otro TT). Queda como trabajo futuro |
| Datos intradía (minuto a minuto) | Yahoo solo da los últimos días; 12 años requieren un proveedor de pago |
| Fundamentales (ganancias, márgenes) | Son trimestrales; no encajan con una señal diaria |
| Opciones (volatilidad implícita por acción) | No hay histórico gratuito |
| Macroeconomía (FRED) | Es gratis, pero quedó fuera del alcance definido; trabajo futuro |

---

## 2. Las 7 acciones

| Ticker | Empresa | Perfil |
|---|---|---|
| AAPL | Apple | Estable, la mayor capitalización |
| MSFT | Microsoft | Estable |
| GOOGL | Alphabet | Estable, a veces lateral |
| AMZN | Amazon | Intermedio |
| META | Meta | Intermedio, con episodios muy volátiles |
| NVDA | NVIDIA | Muy volátil (auge de la IA) |
| TSLA | Tesla | Muy volátil |

Son las 7 tecnológicas más grandes de EE. UU. a finales de 2024 (las
llamadas *Magnificent 7*), ~30 % del valor del S&P 500.

### ¿Por qué estas 7?

1. **Liquidez:** se negocian millones de acciones al día, así que los
   precios no tienen huecos ni saltos por falta de operaciones.
2. **Historia completa:** las 7 tienen datos diarios en todo el periodo.
3. **Variedad de volatilidad dentro de un sector:** permite ver si el modelo
   funciona igual en acciones estables y en volátiles.
4. **Sector homogéneo:** hace razonable entrenar **un solo modelo global**
   con las 7, que multiplica los datos por 7.

### Limitaciones que hay que reconocer

- **Sesgo de supervivencia:** son empresas que crecieron; si una hubiera
  quebrado no estaría aquí.
- **Un solo sector y un solo país:** no sabemos si las conclusiones valen
  para otros sectores o mercados.

---

## 3. El periodo: 2013-12-31 a 2025-12-29

- Se descargan datos desde 2013-01-01 para que los indicadores largos (la
  media de 200 días, la ventana de 252 días del VIX) estén completos.
- Quedan **3 017 días por acción** y **21 119 filas** (día-acción) en total.
- Cubre varios regímenes: mercado alcista largo (2014–2019), el desplome
  del COVID (2020), la recuperación (2021), el año bajista (2022) y el
  auge de la IA (2023–2025).
- **2025** es el último año completo y se usa como prueba. El paper muestra
  que no es un año "fácil": retorno promedio +24 % (por debajo de la mediana
  2014–2024, que es +46 %) y volatilidad alta (39 %, la 3.ª más alta).
- **2026** (enero–septiembre) se usa solo para evaluar el modelo final en
  vivo, nunca para decidir nada.

---

### Cambio respecto al TT1

En el reporte de TT1 el **experimento A** usaba entrenamiento 2014–2021,
validación 2022–2023 y **prueba 2024–2025** (Tablas 3 y 8 del TT1), así que
no compartía la prueba con B y C (el texto del TT1, §3.5.1, dice que sí; la
tabla dice que no). Desde v4 el experimento A es 2014–2023 / 2024 / 2025.
Ver [A3 §2](A3_PROTOCOLO_Y_METRICAS.md#2-los-tres-experimentos-a-b-c).

---

## 4. Contexto de mercado: SPY y VIX

| Serie | Qué es | Para qué |
|---|---|---|
| **SPY** | Fondo que replica el S&P 500 | Saber si "todo el mercado" sube o baja |
| **VIX** | Volatilidad esperada del S&P 500 a 30 días ("índice del miedo") | Saber si el mercado está tranquilo o nervioso |

**Por qué se agregan:** las 7 acciones no se mueven solas. Si el S&P 500
cae, casi todas caen; si el VIX se dispara, hay pánico generalizado. Sin
esta información el modelo no distingue "AAPL cayó por una noticia de Apple"
de "AAPL cayó porque cayó todo".

**Cómo se unen:** por fecha; si falta un día del mercado se rellena con el
último valor conocido (`ffill`), nunca con uno futuro.

**Dato importante para la defensa:** las variables con más peso en el
modelo final son justamente las del VIX y la volatilidad del S&P 500. Eso
explica por qué el modelo dice MANTENER "en bloque" para las 7 acciones en
meses tranquilos (ver [A7](A7_RESULTADOS_Y_LIMITES.md)).

---

## 5. La etiqueta (la parte más importante)

### 5.1 Definición

```
r_fwd(t) = ln( C_{t+1} / C_t )                 retorno del día siguiente

q30(t) = percentil 30 de r_fwd en los 252 días ANTERIORES a t
q70(t) = percentil 70 de r_fwd en los 252 días ANTERIORES a t

etiqueta(t) = COMPRAR (2)  si r_fwd(t) ≥ q70(t)
            = VENDER  (0)  si r_fwd(t) ≤ q30(t)
            = MANTENER (1) en otro caso
```

En código (`calcular_target` de `01_build_raw_dataset.py` y
`api/ml/target.py`):

```python
r_fwd = np.log(close.shift(-1) / close)
umbral_buy  = r_fwd.shift(1).rolling(252, min_periods=126).quantile(0.70)
umbral_sell = r_fwd.shift(1).rolling(252, min_periods=126).quantile(0.30)
```

El `shift(1)` es lo que garantiza que el umbral del día *t* no incluya el
retorno de *t*.

### 5.2 En palabras

- **COMPRAR:** mañana la acción sube tanto como en el 30 % de los mejores
  días de su último año.
- **VENDER:** mañana baja tanto como en el 30 % de sus peores días del año.
- **MANTENER:** cualquier otra cosa (movimiento normal).

### 5.3 ¿Por qué percentiles móviles y no un umbral fijo?

| Alternativa | Problema |
|---|---|
| Umbral fijo (por ejemplo ±1 %) | En 2017 (calma) casi todo sería MANTENER; en 2020 (COVID) casi todo sería COMPRAR o VENDER. La etiqueta cambiaría de significado entre años |
| Umbral en desviaciones estándar (±α·σ) | Hay que elegir α a mano, y supone retornos normales (las colas reales son más pesadas) |
| Triple barrera (López de Prado) | Cierra cada ejemplo en un día distinto (cuando toca una barrera) y requiere calibrar dos parámetros más. Para una comparación limpia entre modelos se prefirió un horizonte fijo de 1 día |
| **Percentiles móviles 30/70** | Se adapta sola al régimen, no tiene parámetros arbitrarios más allá de 30/70, da clases balanceadas y se interpreta fácil |

### 5.4 ¿Por qué 30/70?

- Da ~30 % COMPRAR, ~40 % MANTENER, ~30 % VENDER: clases suficientemente
  grandes para aprender y una clase de "no operar" clara.
- Es la elección usual en la literatura de clasificación de señales.
- **Se probaron otros cortes (Vía 8 y análisis de septiembre):**

| Percentiles | F1 test 2025 | Kappa 2025 | MANTENER real | MANTENER predicho |
|---|---:|---:|---:|---:|
| 20/80 | 0.424 | 0.163 | 61 % | 60 % |
| 25/75 | 0.424 | 0.160 | 51 % | 57 % |
| **30/70 (elegido)** | **0.413** | **0.140** | **42 %** | **57 %** |
| 35/65 | 0.384 | 0.107 | 32 % | 54 % |
| 40/60 | 0.347 | 0.077 | 20 % | 53 % |

Cuidado al leer: el F1 **no** se puede comparar entre cortes distintos
(cambia lo que vale el azar). Por eso se usa también **kappa**, que sí es
comparable. Lo importante: con 40/60 el modelo sigue diciendo MANTENER el
53 % de los días aunque solo el 20 % lo sea, y el kappa cae 45 %. Cortes más
extremos (20/80) suben un poco el kappa, pero hacen que MANTENER sea el
61 % de los días: el modelo operaría muy poco. 30/70 es el equilibrio.

### 5.5 ¿Por qué 252 días?

Es aproximadamente un año de mercado (NYSE opera ~252 días al año). Una
ventana más corta da percentiles inestables; una más larga tarda en
adaptarse a un cambio de régimen.

### 5.6 ¿Por qué retorno logarítmico?

1. Se puede sumar: el retorno de varios días es la suma de los diarios.
2. Es simétrico: subir y bajar la misma proporción da valores opuestos.
3. Su distribución es más parecida a una normal que la del retorno simple.

### 5.7 ¿Por qué 1 día?

- Es la definición directa de "señal diaria", que es el producto que se
  quería construir.
- Da el máximo número de ejemplos.
- Es el caso más difícil (más ruido), y por eso el más exigente para
  comparar modelos.
- **Se probaron horizontes de 2, 3, 5, 7 y 10 días** (Vía 8). Con 5–7 días
  el F1 sube a ~0.43, pero eso **cambia el problema** (ya no es una señal
  diaria) y contradice lo publicado. Queda como trabajo futuro.

### 5.8 Proporción real de clases por año

La proporción no es exactamente 30/40/30 cada año, porque el umbral sale
del año **anterior**: si el año nuevo es más agitado que el anterior, hay
más COMPRAR/VENDER.

| Año | VENDER | MANTENER | COMPRAR |
|---|---:|---:|---:|
| 2018 | 35.8 % | 30.8 % | 33.4 % |
| 2019 | 24.8 % | 45.9 % | 29.3 % |
| 2020 | 33.9 % | 31.8 % | 34.3 % |
| 2021 | 27.9 % | 44.7 % | 27.4 % |
| 2022 | 36.5 % | 32.0 % | 31.4 % |
| 2023 | 23.2 % | 48.2 % | 28.6 % |
| 2024 | 30.0 % | 39.5 % | 30.4 % |
| 2025 | 29.6 % | 42.2 % | 28.3 % |
| Todo 2014–2025 | 30 % | 40 % | 30 % |

Este detalle importa para entender por qué un ajuste fijo del umbral de
MANTENER no funciona: el sesgo cambia de año a año.

### 5.9 Debilidades de la etiqueta (dilas tú antes de que te las digan)

1. **Un día es muy ruidoso.** La mayor parte del movimiento diario es azar.
2. **No distingue magnitud.** Un COMPRAR que sube 0.8 % vale lo mismo que
   uno que sube 5 %.
3. **Memoria del último año.** Después de un mes de crisis, los umbrales se
   ensanchan y hay menos COMPRAR/VENDER en las semanas siguientes.
4. **El último día del año** usa el cierre del primer día del año siguiente
   para su etiqueta (es un solo día por corte; ver [A3](A3_PROTOCOLO_Y_METRICAS.md)).

---

## 6. Cómo queda cada fila del dataset

Una fila = un día de una acción:

| Columnas | Contenido |
|---|---|
| Índice | Fecha |
| 61 variables | Calculadas con información hasta el cierre de ese día ([A2](A2_VARIABLES.md)) |
| `target` | 0 VENDER, 1 MANTENER, 2 COMPRAR |
| `r_forward` | `ln(C_{t+1}/C_t)`, para la simulación económica |

Se guardan en `tesis_ml_stocks/01_raw_datasets/{TICKER}_raw.parquet`. Las
variables solo miran hacia atrás; la etiqueta y `r_forward` miran un día
hacia adelante, y **nunca** se usan como entrada del modelo.

---

## 7. La misma etiqueta en la plataforma

`api/ml/target.py` reproduce la etiqueta en vivo para evaluar cada señal
contra lo que pasó al día siguiente. Diferencia: en el dataset de
entrenamiento, un día sin suficiente historia se marca MANTENER; en la
plataforma se deja como "pendiente" (no se inventa). Hay una prueba
automática que verifica que ambas coinciden al 100 % cuando la ventana de
252 días está completa.

---

## Preguntas de este tema

Están desarrolladas en [D3](../D_defensa/D3_PREGUNTAS_DATOS.md).
