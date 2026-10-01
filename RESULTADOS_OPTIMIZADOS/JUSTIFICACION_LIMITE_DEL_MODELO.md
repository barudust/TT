# Por qué el modelo llegó a su límite

**Justificación con evidencia de que, con datos de Yahoo Finance, los cinco
modelos del proyecto y una señal diaria, se alcanzó el mejor resultado
posible.**

> TT 2026-B164 · Documento para la tesis y la defensa · 2026-09-30
>
> Cada cifra sale de un archivo del repositorio (se indica cuál). El análisis
> nuevo de este documento está en
> [`docs/ANALISIS_HOLD_Y_GLOBAL.md`](docs/ANALISIS_HOLD_Y_GLOBAL.md); el
> inventario completo de lo que se probó, en
> [`INVESTIGACION_COMPLETA.md`](INVESTIGACION_COMPLETA.md).

---

## Resumen

1. **El problema tiene un techo bajo y ya lo tocamos.** Predecir la
   dirección del día siguiente solo con precios y volumen públicos es, por
   construcción, casi impredecible: esa información ya está en el precio.
   En seis años de prueba (walk-forward 2020–2025) el mejor modelo promedia
   F1-macro ≈ 0.35, donde el azar es 0.33, y **ningún modelo pasa de 0.394
   en ningún año**.
2. **Cinco arquitecturas muy distintas llegan a la misma banda.** Lineal,
   árboles, recurrente, convolucional e híbrida, cada una con búsqueda de
   hiperparámetros (Optuna), quedan entre 0.29 y 0.36 de F1 promedio. Si
   hubiera más información aprovechable en los datos, alguna de ellas la
   habría encontrado.
3. **Todas las palancas dentro del alcance se probaron** (≈ 30 técnicas en
   siete iteraciones). Las que "mejoran" lo hacen en 0.01–0.03 de F1,
   mientras que el mismo modelo varía 0.08 de un año a otro. Ninguna mejora
   es distinguible del ruido entre años.
4. **El exceso de MANTENER es consecuencia del techo, no un error.** Cuando
   el modelo no distingue si el precio subirá o bajará, reparte esa
   probabilidad entre COMPRAR y VENDER y MANTENER gana. Cambiar la etiqueta
   a 40/60 no lo corrige y empeora el modelo.
5. **El modelo global es mejor que un modelo por acción** (o empata), para
   los cinco modelos, en dos protocolos distintos.
6. **Lo único que sube claramente el desempeño es cambiar el problema**
   (horizonte de 5 días: F1 ≈ 0.43) **o salir del alcance** (otros datos).
   Ambas cosas quedan como trabajo futuro.

---

## 1. Qué problema se resolvió y con qué restricciones

| Aspecto | Definición del TT |
|---|---|
| Tarea | Clasificar cada día COMPRAR / MANTENER / VENDER para el día siguiente |
| Activos | AAPL, NVDA, TSLA, AMZN, MSFT, GOOGL, META |
| Datos | Solo Yahoo Finance: OHLCV diario + SPY + VIX (2014–2025) |
| Etiqueta | Percentiles 30/70 rodantes (252 días) del retorno a 1 día |
| Modelos | Exactamente cinco: Regresión Logística, XGBoost, LSTM, CNN 1D, CNN-LSTM |
| Evaluación | F1-macro (clasificación) + backtest de un día (Sharpe, drawdown, win rate) |

Cada restricción cierra una puerta: sin noticias, fundamentales, opciones ni
datos intradía; sin otras arquitecturas; y con el horizonte más ruidoso
posible (un día). La pregunta de este documento es: **dentro de esas
puertas, ¿quedó algo por hacer?** La respuesta es no, y las secciones 2–4
muestran por qué.

## 2. Qué tan predecible es el problema

### 2.1 Por qué se espera un techo bajo

- **Eficiencia débil del mercado.** Si el historial de precios y volumen
  permitiera predecir con claridad el día siguiente, esa ventaja se
  arbitraría y desaparecería. Las siete acciones del TT son de las más
  líquidas y analizadas del mundo; es el peor escenario para encontrar
  ineficiencias con indicadores técnicos públicos.
- **La literatura lo confirma.** Fischer y Krauss (2018), con LSTM sobre
  todo el S&P 500, obtienen una precisión direccional apenas arriba del
  50 % y reportan que la rentabilidad desaparece después de 2010. Gu, Kelly
  y Xiu (2020) solo ven ventaja de las redes neuronales con ~30 000
  acciones y 60 años de datos; aquí hay 7 acciones y ~6 años de
  entrenamiento.
- **Pocos datos para modelos grandes.** Exp B tiene ≈ 10 500 filas de
  entrenamiento en total (≈ 1 500 por acción); los modelos profundos tienen
  10⁵–10⁶ parámetros.

### 2.2 La medición directa: casi toda la señal es ruido

El kappa de Cohen mide cuánto se acierta **por encima del azar** (0 = azar,
1 = perfecto). Para el modelo de producción antes del ajuste de MANTENER
([`docs/ANALISIS_HOLD_Y_GLOBAL.md`](docs/ANALISIS_HOLD_Y_GLOBAL.md) §1, §6 y §8):

| Periodo | F1-macro | κ |
|---|---:|---:|
| Validación 2024 | 0.325 | 0.03 |
| Test 2025 | 0.413 | 0.14 |
| 2026 real, fuera de muestra (ene–sep, 1 302 días-acción) | 0.313 | 0.01 |
| 2026, modelo actual (peso de MANTENER × 0.90, §6.1) | 0.354 | 0.035 |

En dos de los tres años el modelo está prácticamente en el azar, y el año
bueno (2025) es el que se usó como test. Con 500 permutaciones aleatorias de
sus propias señales, en 2025 solo el 0.4 % le gana; en 2024, el 79 %.

### 2.3 Seis años de walk-forward: el techo es igual para todos

Además de los tres experimentos del paper, en v5 se corrió un walk-forward
(entrenar 5 años, validar 1, probar el siguiente) para 2020–2025
([`v5/log_wf_v5.txt`](v5/log_wf_v5.txt), consolidado en
[`analisis_hold/5_walk_forward_v5_resumen.csv`](analisis_hold/5_walk_forward_v5_resumen.csv)):

| Modelo | F1 medio | Rango por año | Sharpe medio |
|---|---:|---|---:|
| XGBoost | 0.356 | 0.330 – 0.387 | +0.22 |
| Regresión Logística | 0.350 | 0.314 – 0.394 | +0.22 |
| CNN-LSTM | 0.328 | 0.274 – 0.376 | −0.25 |
| LSTM | 0.314 | 0.264 – 0.366 | −0.48 |
| CNN 1D | 0.292 | 0.227 – 0.359 | −0.29 |

El mejor modelo cambia de año a año (XGBoost, LR, LSTM, LR, CNN-LSTM, LR).
Lo que se sostiene en los seis años es: **los dos clásicos quedan arriba de
los tres profundos, ninguno pasa de ≈ 0.39, y el promedio está a menos de
tres puntos del azar.** Esto es lo que significa "techo": no es que falte un
modelo mejor, es que la información no está en los datos.

## 3. Todo lo que se probó dentro del alcance

Resumen de siete iteraciones (detalle y archivos en
[`INVESTIGACION_COMPLETA.md`](INVESTIGACION_COMPLETA.md)):

| Dimensión | Qué se probó | Resultado |
|---|---|---|
| Arquitecturas | Los 5 del TT, globales y por acción, 3 ventanas de entrenamiento (120 corridas en v4, 120 en v5) + LightGBM | LR y XGBoost arriba; profundos abajo |
| Hiperparámetros | Optuna TPE: 150 trials LR y XGBoost, 80 cada profundo; multi-semilla | +0.033 F1 a LR (v5); el ranking no cambia |
| Protocolo | Torneo de 6 decisiones (criterio de época, ventanas alineadas, escalador, pesos de clase, pooling, reentrenamiento) | Solo 1 de 6 ayuda (al LSTM) |
| Diagnóstico profundo | ¿Aprenden los profundos? | En las configuraciones de v4 su pérdida de validación nunca baja de ln 3 (= azar) y el early stopping se queda en la época 1–2 ([`DIAGNOSTICO_MODELOS_PROFUNDOS.md`](docs/DIAGNOSTICO_MODELOS_PROFUNDOS.md)); v5 corrigió el protocolo y siguieron abajo |
| Más features | v3: 94 (curva de tasas, DXY, oro, petróleo, sectores); v5: +32 de contexto; v8: lags, multi-timeframe, cross-asset, interacciones | v3 y v5 sin mejora; en v8 solo interacciones (+0.023, solo en 2025, §7) |
| Selección de features | Pearson, VIF, Spearman, SHAP | Empeora en 11 de 15 casos |
| Ensambles | Stacking, soft voting, blending LR+XGB y de 5 modelos (por F1 y por Sharpe) | Ninguno supera a LR solo |
| Post-proceso | Calibración isotónica, Platt, umbral económico de HOLD, SWA, ponderación por recencia | Solo isotónica ayuda a XGBoost (+0.012) |
| Etiqueta | 6 horizontes × 5 pares de percentiles (28 configuraciones) | Con 1 día, 25/75 y 20/80 suben ~0.01 el F1 pero aumentan la proporción de MANTENER; 35/65 y 40/60 empeoran; con 5–7 días sube a ≈ 0.43 (otro problema) |
| Robustez | Bootstrap por bloques IC 95 %, walk-forward de 6 años, costos de 5 y 10 pb | LR significativamente arriba en 2025; empate con XGBoost en walk-forward; con costos LR gana por operar menos |

**El patrón:** cada palanca mueve el F1 entre −0.05 y +0.03. El mismo modelo
en distintos años se mueve 0.08 (LR: 0.314 → 0.394). Ninguna mejora dentro
del alcance es más grande que la variación natural entre años, así que no
hay forma honesta de decir que alguna "rompe" el techo.

## 4. Cuatro evidencias de que el límite es de los datos y no de los modelos

1. **Convergencia.** Cinco sesgos inductivos distintos (lineal, árboles,
   recurrente, convolucional, híbrido), con búsqueda de hiperparámetros,
   terminan en la misma franja 0.29–0.36. Si hubiera estructura no lineal o
   temporal aprovechable, los árboles o las redes la habrían explotado; en
   cambio, los modelos más flexibles quedan **abajo** del lineal, que es lo
   que ocurre cuando lo único que hay que aprender es poco y ruidoso.
2. **Empate en validación.** En validación 2024 (el año con el que se
   ajustaron los hiperparámetros) los cinco están entre 0.324 y 0.366
   ([`v5/resultados_finales.csv`](v5/resultados_finales.csv)); ahí LR es el
   más bajo. Las diferencias entre modelos son del tamaño del ruido.
3. **El propio modelo "sabe" que tiene poca información.** Con la
   regularización que eligió Optuna (C = 0.000165) los coeficientes son
   diminutos y las probabilidades quedan cerca de 1/3: confianza mediana de
   0.378, y en 28 % de los días la señal se decide por menos de 2 puntos
   porcentuales. Optuna llegó a esa regularización fuerte porque cualquier
   modelo más "atrevido" se ajustaba al ruido y perdía en validación.
4. **La única regularidad encontrada es inestable.** Lo que el modelo sí
   aprendió es que con volatilidad baja los movimientos son chicos (HOLD).
   En 2025 eso era cierto y el modelo funcionó; en 2026 dejó de cumplirse
   (HOLD real ≈ 35 % con VIX alto o bajo) y el F1 cayó a 0.31. Una relación
   que cambia de un año a otro no se puede "optimizar" más: cualquier ajuste
   fino a un año se pierde en el siguiente.

Y una evidencia a favor de que el límite es el **problema**: si se cambia el
horizonte a 5 días, el mismo LR sube a F1 ≈ 0.43 y Sharpe ≈ +1.15
([`docs/VIA8_DATASET.md`](docs/VIA8_DATASET.md)). Los modelos sí pueden
aprender cuando hay más señal; el día siguiente simplemente tiene muy poca.

## 5. Por qué el modelo recomienda MANTENER tan seguido

### 5.1 Los números

| Periodo | MANTENER real | Predicho (modelo anterior) | Predicho (modelo actual, §6.1) |
|---|---:|---:|---:|
| Test 2025 | 42 % | 57 % | — |
| 2026 fuera de muestra | 35 % | 60 % | 40 % |
| Últimos 30 días hábiles (ago–sep 2026) | 38 % | 95 % | 70 % |

### 5.2 La explicación ("voto dividido")

El modelo da tres probabilidades y elige la mayor. En **todos** los días en
que dijo MANTENER, la probabilidad de que el precio se mueva fuerte
(COMPRAR + VENDER) era mayor que la de MANTENER: en promedio 0.29 + 0.32 =
0.62 contra 0.38. El modelo espera movimiento, pero no sabe hacia dónde, así
que la probabilidad se divide entre COMPRAR y VENDER y ninguna le gana a
MANTENER por separado. MANTENER significa exactamente "no hay una dirección
clara", que es la definición que da la propia plataforma.

### 5.3 Por qué hay rachas de puro MANTENER

Las variables con más peso son de volatilidad del mercado (VIX respecto a su
media anual, volatilidad del S&P 500), que son las mismas para las siete
acciones. Cuando el VIX está debajo de su media anual, el modelo dice
MANTENER para casi todas: en 2025, 92 % de MANTENER en el quintil de VIX
más bajo y 0.6 % en el más alto. Desde agosto de 2026 el VIX está por debajo
de su media anual; por eso la plataforma muestra MANTENER en casi todo.

### 5.4 Por qué no es un defecto

- Los días en que dice MANTENER se mueven ~40 % menos (1.31 % contra 2.2 %).
- Quitarle la opción de MANTENER (forzar COMPRAR/VENDER) no mejora nada: en
  2025 el Sharpe queda igual (+0.89 contra +0.92) con peor win rate, profit
  factor y drawdown; en 2024 empeora (−0.71 contra −0.49).
- Con una señal tan débil, **no operar** cuando no hay dirección es la
  decisión racional. Un modelo que dijera COMPRAR o VENDER todos los días
  estaría fingiendo una certeza que no tiene.

## 6. ¿Y si se cambia la etiqueta a 40/60 ("60/40")?

40/60 dejaría MANTENER solo para el 20 % central de los retornos. Ya se había
probado en Vía 8 y se repitió con el modelo actual, en dos años:

| Etiqueta | MANTENER real | MANTENER predicho | κ 2025 | Sharpe 2025 | κ 2024 | Sharpe 2024 |
|---|---:|---:|---:|---:|---:|---:|
| 30/70 (actual) | 42 % | 57 % | 0.140 | +0.92 | 0.030 | −0.49 |
| 40/60 | 20 % | **53 %** | 0.077 | +0.58 | 0.024 | +0.13 |

- **No resuelve el problema:** aun con solo 20 % de MANTENER real, el modelo
  lo predice el 53 % de las veces, por la misma razón de la §5.2. Cambiar
  dónde se corta la etiqueta no le da al modelo información sobre la
  dirección.
- **Empeora el modelo:** κ baja 45 % en 2025 y 20 % en 2024; el Sharpe de
  2025 baja de +0.92 a +0.58. En 2024 el Sharpe sube, pero sigue muy debajo
  de comprar y mantener (+1.16) ese año.
- **Costaría mucho:** para los cinco modelos habría que repetir todo el
  protocolo v5 (≈ 6–8 h de GPU solo en Optuna, 120 corridas, reconsolidar
  tablas y reescribir capítulos), y el paper aceptado en MICAI usa 30/70.
  Con el mejor modelo empeorando, el resultado esperado es peor que el
  actual.

### 6.1 Lo que sí se hizo sin tocar la etiqueta: ajustar el peso de MANTENER

Se probaron cinco formas de reducir MANTENER sin cambiar la etiqueta,
eligiendo **solo con 2019–2024** (validación por origen rodante: entrenar
6 años, predecir el siguiente) y confirmando en 2025 y 2026
([`docs/ANALISIS_HOLD_Y_GLOBAL.md`](docs/ANALISIS_HOLD_Y_GLOBAL.md) §8):

- **Un factor fijo sobre la probabilidad de MANTENER no sirve:** el mejor
  factor resultó ≈ 1 (no tocar nada). El sesgo cambia de signo entre años
  (2022: 13 % predicho contra 32 % real; 2023: 74 % contra 48 %), así que un
  corrimiento fijo arregla unos años y descompone otros.
- **Reentrenar con el peso de clase de MANTENER × 0.90** fue el mejor en F1,
  κ y Sharpe a la vez en 2019–2024 y es el que quedó en producción:

| | F1 | κ | MANTENER pred. / real | Sharpe |
|---|---:|---:|---:|---:|
| 2019–2024, antes | 0.357 | 0.063 | 47 % / 40 % | +0.52 |
| 2019–2024, después | 0.365 | 0.068 | 36 % / 40 % | +0.54 |
| 2026, antes | 0.313 | 0.010 | 60 % / 35 % | +0.38 |
| 2026, después | 0.354 | 0.035 | 40 % / 35 % | +0.29 |

La proporción de MANTENER queda realista sin perder desempeño de forma
medible; no es una mejora estadísticamente significativa (mejora el F1 en 4
de 6 años, Wilcoxon p = 0.31). En meses muy tranquilos MANTENER sigue
predominando (agosto de 2026: 86 %), porque el modelo sigue sin conocer la
dirección: el ajuste mueve el umbral, no crea información.

## 7. ¿Modelo global o un modelo por acción?

**Sí se comparó, y ganó el global.** Cada uno de los cinco modelos se
entrenó en las dos modalidades, en los tres experimentos, dos veces: en v4
(el paper, 120 corridas) y en v5 con el protocolo corregido (otras 120).

Comparando sobre las mismas filas de cada acción (21 casos por modelo =
3 experimentos × 7 acciones, test 2025,
[`analisis_hold/4a_global_vs_porticker_por_modelo.csv`](analisis_hold/4a_global_vs_porticker_por_modelo.csv)):

| Modelo | F1 global | F1 por acción | Casos que gana el global | ¿Significativo? |
|---|---:|---:|---:|---|
| Regresión Logística | **0.394** | 0.375 | 18 de 21 | Sí (p = 0.002) |
| XGBoost | 0.359 | 0.364 | 10 de 21 | No (empate) |
| LSTM | 0.334 | 0.314 | 16 de 21 | Sí (p = 0.03) |
| CNN 1D | 0.293 | 0.212 | 19 de 21 | Sí (p < 0.001) |
| CNN-LSTM | 0.305 | 0.330 | 7 de 21 | No |

- El global es mejor en tres modelos, empata en XGBoost, y en ningún modelo
  el "por acción" es significativamente mejor.
- Para la Regresión Logística, además, el Sharpe medio del global duplica al
  del por acción (+0.88 contra +0.44).
- Con la configuración actual de producción (LR + interacciones): test 2025
  F1 0.413 (global) contra 0.398 (por acción), mismo Sharpe; en 2024
  empatan en F1.

**Por qué gana el global:** tiene siete veces más ejemplos (≈ 10 500 contra
≈ 1 500); la etiqueta es un percentil de cada acción, así que COMPRAR
significa lo mismo en las siete; las variables son razones y porcentajes
comparables entre acciones; y con tan poca señal, un modelo por acción
termina aprendiendo el ruido propio de esa acción. Además, en producción es
un solo modelo que mantener.

**Nota sobre el paper.** El paper (v4) dice que agrupar "es indiferente para
LR". Esa conclusión comparaba el F1 del global sobre todas las filas juntas
contra el promedio de siete F1 por acción, que no son la misma métrica. Con
la comparación directa de v5, el global también gana en LR. Las dos
versiones coinciden en lo importante: **no hay ningún caso en que convenga
un modelo por acción.**

## 8. Por qué la Regresión Logística sigue siendo el modelo a desplegar

En walk-forward LR y XGBoost empatan en F1 (0.350 contra 0.356) y en Sharpe
(+0.22 ambos). Lo que los separa:

- **En el experimento principal (test 2025, Exp B)** LR gana en F1 (0.404
  contra 0.359) y Sharpe (+0.89 contra +0.46), y el bootstrap por bloques lo
  separa significativamente de los otros cuatro en 2025 (paper, §6).
- **Opera menos.** Cambio medio de posición por día 0.38 contra 0.65 de XGBoost; con costos de
  10 puntos base por operación, LR conserva Sharpe +0.62 y XGBoost cae a
  +0.01 ([`v5/resultados_finales.csv`](v5/resultados_finales.csv)).
- **Es interpretable, estable y barato.** Coeficientes legibles, no cambia
  entre semillas (desviación 0.000), y predice en milisegundos.

## 9. Limitaciones que conviene decir antes de que las pregunten

- **Un solo año de test en el paper.** El walk-forward de v5 (§2.3) responde
  a esto: el techo se mantiene en seis años. Conviene citarlo.
- **Las interacciones de Vía 8 no están validadas.** Se eligieron mirando
  test 2025; en validación 2024 empatan con el LR sin interacciones (0.325
  contra 0.326) y en 2026 el modelo con interacciones da 0.313. Hay que
  tratarlas como equivalentes, no como mejora. Los archivos de métricas del
  modelo las etiquetan como "val 2024", pero son de test 2025.
- **Sin costos en las cifras principales.** Con 10 pb el orden LR > XGBoost
  se mantiene; los profundos, que ya tenían Sharpe negativo, empeoran.
- **La plataforma evalúa en vivo con el mismo criterio que la tesis**, y en
  2026 muestra lo que este documento dice: clasificación apenas arriba del
  azar (κ 0.035 con el modelo actual) y más MANTENER en épocas de volatilidad
  baja.

## 10. Qué haría falta para ir más allá (fuera del alcance)

Cada opción rompe una restricción del TT, por eso es trabajo futuro y no
algo que "faltó hacer":

| Opción | Restricción que rompe | Evidencia o estimación |
|---|---|---|
| Horizonte de 5–7 días | Cambia el problema | F1 ≈ 0.43, Sharpe ≈ +1.15 a +1.5 (Vía 8, medido) |
| Datos macro (FRED), opciones (volatilidad implícita), noticias (FinBERT), intradía | Solo Yahoo Finance | +0.01 a +0.07 F1 (estimado, [`ALTERNATIVAS_FUTURAS.md`](docs/ALTERNATIVAS_FUTURAS.md)) |
| Cientos de acciones en vez de 7 | Universo del TT | Es donde la literatura sí encuentra ventaja de las redes (Gu et al. 2020) |
| Tamaño de posición (Kelly, volatilidad objetivo) | Estrategia ±1/0 de la tesis | Cambia el Sharpe absoluto, no el F1 |
| Transformers, TabNet, otras arquitecturas | Los 5 modelos del TT | Sin evidencia de que ayuden con ~10 000 filas |

## 11. Respuestas cortas para la defensa

**¿Por qué no siguieron optimizando?**
Porque en seis años de prueba ningún modelo pasó de 0.39 de F1 y las mejores
técnicas mueven 0.01–0.03, menos que la diferencia entre un año y otro. Se
probaron las cinco arquitecturas con Optuna, más features, selección de
features, ensambles, calibración y cambios de protocolo. Seguir ajustando
sobre el mismo año de prueba solo habría sobreajustado a ese año.

**¿Por qué el modelo casi siempre dice MANTENER?**
Porque no distingue si el precio subirá o bajará: espera un movimiento, pero
esa probabilidad se divide entre COMPRAR y VENDER y MANTENER gana. Pasa más
cuando el VIX está por debajo de su media anual, como desde agosto de 2026.
Lo redujimos sin tocar la etiqueta: reentrenando con el peso de MANTENER ×
0.90, elegido con 2019–2024, en 2026 baja de 60 % a 40 % (real 35 %) y el F1
sube de 0.313 a 0.354. Un factor fijo sobre la probabilidad, en cambio, empeora
el modelo porque el sesgo no es constante entre años.

**¿Por qué no usaron 40/60 para que hubiera menos MANTENER?**
Lo probamos: el modelo siguió diciendo MANTENER el 53 % de los días aunque
solo el 20 % lo era, y el kappa y el Sharpe bajaron. El problema no es dónde
se corta la etiqueta, sino que la dirección casi no es predecible.

**¿Global o por acción?**
Global. Se comparó para los cinco modelos en dos protocolos; el global gana
o empata en todos, y en ningún modelo el por-acción es significativamente
mejor. Tiene siete veces más datos y la etiqueta es comparable entre
acciones.

**¿Entonces el modelo no sirve?**
El TT es una comparación metodológica, no un sistema de trading. Su
resultado es saber cuánto se puede extraer de datos públicos diarios con
estos modelos (poco, y de forma inestable), y que un modelo lineal bien
regularizado iguala o supera a redes profundas en este régimen, que es lo
que publica el paper.

**¿Qué harían para mejorarlo?**
Cambiar el horizonte a 5 días (ya medido: F1 ≈ 0.43) o añadir datos que no
estén en el precio (macro, opciones, noticias). Las dos cosas cambian el
alcance del TT.

---

## Anexo: cómo reproducir las cifras nuevas

```bash
python scripts_opt/analisis_hold_global.py      # ~20 s, sin red
python scripts_opt/evaluar_produccion_2026.py   # ~1 min, con red (Yahoo)
```

Resultados en `RESULTADOS_OPTIMIZADOS/analisis_hold/`. El walk-forward de v5
se consolidó desde `RESULTADOS_OPTIMIZADOS/v5/log_wf_v5.txt` en
`analisis_hold/5_walk_forward_v5_resumen.csv`.
