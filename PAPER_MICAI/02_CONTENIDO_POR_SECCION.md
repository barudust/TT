# 02 — Contenido del artículo, sección por sección

> Resumen fiel de lo que dice el texto publicado (`../paper_review/paper.tex`).
> Las cifras exactas de las tablas están en `03_TABLAS_Y_CIFRAS.md`. Entre
> corchetes, la etapa del TT de la que sale cada sección (ver `04_PAPER_VS_TT.md`).

---

## Resumen (abstract)

Compara cinco clasificadores supervisados —regresión logística multinomial
(LR), XGBoost, LSTM bidireccional, CNN 1D y CNN-LSTM— para predecir señales
diarias BUY/HOLD/SELL de siete acciones tecnológicas grandes de EE. UU. La
etiqueta es el percentil rodante 30/70 del retorno logarítmico a un día en
una ventana de 252 días. Usa 61 indicadores de datos diarios OHLCV más SPY y
VIX, todo gratis de Yahoo Finance. Tres particiones comparten el año de
prueba (2025) y difieren solo en años de entrenamiento (10, 6 y 4); cada
modelo se entrena global y por acción: 120 corridas. **La LR con elasticnet
obtiene el mayor F1-macro promedio (0.399) y el mejor Sharpe del experimento
principal (+0.76)**; repetir todo con un protocolo más estricto (búsqueda
simétrica con Optuna e intervalos bootstrap del 95 %) **deja a la LR
significativamente arriba de los cuatro**. Filtrar variables con pruebas
estadísticas empeora en 11 de 15 casos, y **la volatilidad de la acción, no
el tipo de modelo, domina la variación entre acciones**.

## 1. Introduction [—]

Tres problemas recurrentes en la literatura: (i) se comparan uno o dos
modelos, (ii) se reporta accuracy o RMSE, que no se traducen en desempeño de
trading, (iii) se filtran variables sin comprobar que ayude. El artículo
ataca los tres. **Contribuciones:** (i) pipeline reproducible con datos
gratuitos y particiones alineadas; (ii) comparación de cinco modelos en 120
corridas, como clasificación y como economía; (iii) evaluación de la
preselección estadística de variables; (iv) evidencia de que la volatilidad
de la acción explica más que el modelo; (v) repetición con un protocolo más
estricto, búsqueda simétrica e intervalos de confianza.

## 2. Related Work [—]

Sezer et al. (más de 140 trabajos: dominan LSTM y CNN, rara vez hay línea
base lineal); Fischer y Krauss (LSTM en el S&P 500, con dudas posteriores de
*look-ahead*); Patel et al. (modelos regularizados igualan a redes con datos
diarios); XGBoost y Optuna. **Hueco:** no hay una comparación de LR, XGBoost
y tres redes bajo un mismo protocolo con evaluación de clasificación y
económica.

## 3. Data and Target [Etapa 3]

- **3.1 Activos y fuente:** AAPL, NVDA, TSLA, AMZN, MSFT, GOOGL, META (las
  siete más grandes a fines de 2024); OHLCV diario del 2013-12-31 al
  2025-12-29 con `yfinance`, ajustado; SPY y VIX como contexto. Sin datos de
  pago.
- **3.2 Etiqueta:** `r_fwd(t) = ln(C_{t+1}/C_t)`; percentiles 30 y 70 en
  252 días con datos anteriores a *t*; BUY si `r_fwd ≥ q70(t−1)`, SELL si
  `≤ q30(t−1)`, HOLD si no. Distribución cercana a 30/40/30 en cualquier
  régimen; el desplazamiento de un día evita *look-ahead*.
- **3.3 Variables (61):** nueve familias (tabla completa en el
  suplementario).
- **3.4 Particiones:** Tabla 1 (A 2014–2023, B 2018–2023, C 2020–2023; todas
  validan en 2024 y prueban en 2025). **¿2025 es representativo?** Retorno
  medio +24.2 % (mediana 2014–2024: +46.3 %, 9.º de 12), volatilidad 39.1 %
  (3.ª más alta), caída máxima media −33.0 %, VIX medio 19.0; proporción
  29.6/42.2/28.3. Dentro del rango histórico, pero debajo de la mediana en
  retorno y arriba en volatilidad: no es el mercado alcista fácil que
  favorecería a un clasificador sesgado a comprar.

## 4. Models [Etapa 3, texto heredado de TT1]

- **LR:** multinomial con elasticnet (SAGA), C ∈ {0.01, 0.1, 1}, l1-ratio
  0.5, pesos balanceados, cinco semillas por voto.
- **XGBoost:** `multi:softprob`, `hist` en GPU, Optuna (TPE) 20–40 intentos,
  pesos balanceados, tres semillas promediadas.
- **LSTM bidireccional:** 2 capas de 128, dropout 0.3, LayerNorm; lookback
  20 y 60.
- **CNN 1D:** tres bloques Conv1D (64-128-192, kernel 3, BN, ReLU, dropout),
  promedio + máximo global, dos capas densas.
- **CNN-LSTM:** CNN (64-128) → LSTM (128, dos capas) → lineal. *El texto dice
  que los últimos cinco canales llevan OHLCV normalizado por ventana; ver
  `04_PAPER_VS_TT.md` §3.*
- **Entrenamiento:** escaladores dentro de cada partición (Standard para LR,
  MinMax para redes); redes hasta 80 épocas, AdamW, recorte 1.0,
  ReduceLROnPlateau, paro temprano con paciencia 15 sobre la pérdida de
  validación —"criterio que la §8 muestra que es el que limita"—; tres
  semillas (cinco para LR).

## 5. Evaluation [Etapa 3]

- **5.1 Clasificación:** F1-macro como métrica principal (pesa igual las tres
  clases). F1 por clase en el suplementario.
- **5.2 Backtest:** BUY +1, HOLD 0, SELL −1; `r_strat = posición · r_fwd`;
  win rate y profit factor sobre días con posición; caída máxima; Sharpe
  anualizado con `r_f = 0`. **Sin costos a propósito** (comparación de primer
  orden).
- **5.3 Sobre accuracy:** no se reporta; predecir solo HOLD da ≈ 0.40.

## 6. Statistical feature pre-selection: should we use it? [Etapa 2]

Filtros por prueba estadística (Pearson + VIF para LR, SHAP para árboles,
Spearman para no lineales) contra usar las 61. **Tabla 2:** usar todas es
mejor en 11 de 15 casos; la ventaja es mayor en la LR (su regularización
selecciona mejor que un filtro externo); para XGBoost SHAP es competitivo;
para las redes depende del experimento. **Decisión:** todo lo demás usa las
61 para todos los modelos. Los filtros sirven para explorar, no para
preprocesar.

## 7. Results [Etapa 3]

- **Introducción:** 120 corridas. Para las redes se entrenaron lookback 20 y
  60 y **se reporta el mejor medido en la prueba**: ventaja de "oráculo" para
  las redes, así que la brecha es un **límite inferior** del margen de la LR.
  La §8 repite todo sin esa ventaja.
- **7.1 Modelos globales (Tabla 3):** LR primera en promedio (0.399), gana A
  y C; XGBoost segundo, supera a la LR por 0.002 en B; redes 0.34–0.39.
  **Economía en B (Tabla 4):** LR con el mayor profit factor (1.21) y Sharpe
  (+0.76); XGBoost iguala en F1 pero es más cercano al azar en dinero;
  CNN-LSTM controla mejor la caída (−0.40); la CNN es la más débil.
- **7.2 Por acción (Tabla 5):** la LR es la más consistente (gana los tres);
  las redes caen más porque cada acción tiene ~1 500 muestras.
- **7.3 De dónde viene la variación entre acciones:** bandas horizontales en
  el mapa de calor del Sharpe (AMZN bien con casi todos, GOOGL mal con casi
  todos). Descomposición de la suma de cuadrados de los 105 Sharpe por
  acción: **acción 15.5 %, modelo 3.4 %**, experimento 7.0 %, interacción y
  ruido 74.1 % → la acción explica ≈ 4.5 veces más. GOOGL es la única con
  media negativa (−0.15); NVDA la única con mediana negativa (−0.16).
- **7.4 Longitud del entrenamiento:** la LR va mejor con 10 años (0.411) pero
  no es monótono (C 0.401 > B 0.385); las redes casi planas. La diferencia
  entre ventanas (0.026 en la LR) es del orden del ruido; no se lee una
  tendencia.
- **7.5 Distribución de señales (Figura 1):** proporción real 30/40/30
  (2014–2025) y 29.6/42.2/28.3 en 2025. La CNN colapsa hacia BUY (49 %) y casi
  abandona SELL (6 %); LSTM y XGBoost siguen la proporción base; la LR es
  conservadora en BUY (18 %) y alta en SELL (38 %), lo que le da el mejor
  Sharpe en un año con retorno debajo de la mediana.
- **7.6 Detalle por acción (XGBoost por acción, B):** TSLA el mejor (F1 0.44,
  Sharpe +2.06, +201 %), GOOGL el peor (F1 0.34, Sharpe −0.88); el rango entre
  acciones es mucho mayor que entre modelos.

## 8. Robustness: symmetric search and confidence intervals [Etapa 4]

- **Motivación:** dos asimetrías podían explicar el orden: XGBoost se ajustó
  con Optuna y las redes con una cuadrícula chica, y la ventana de las redes
  se eligió con la prueba.
- **Protocolo:** modo *dev* (entrena 2018–2022, época con 2023, todas las
  decisiones con 2024) y modo *final* (entrena 2018–2023, época con 2024,
  2025 se evalúa una vez). Ventanas sobre la serie continua: **las cinco se
  evalúan en las mismas 1 736 filas** (antes las redes veían 1 596 con
  lookback 20 y 1 316 con 60). El código nuevo reproduce 18 de 18 celdas.
- **Presupuesto:** mismo muestreador TPE y mismo año de decisión; redes con
  17–20 hiperparámetros (80 intentos; 54/53/74 terminados), XGBoost 9, LR 5;
  un entrenamiento de red tarda 7–12 s.
- **Resultado (Tabla 6):** la búsqueda **no cierra la brecha**: la LR sigue
  primera (0.404 [0.379, 0.428]) y su margen crece; es significativamente
  mejor que los cuatro (diferencias pareadas +0.045 sobre XGBoost, +0.035
  sobre LSTM, +0.031 sobre CNN-LSTM, +0.045 sobre CNN 1D); entre los otros
  cuatro ninguna diferencia es significativa. En promedio de las tres
  particiones, LR +0.005 respecto a §7, XGBoost −0.025, CNN −0.054, CNN-LSTM
  −0.059. Las tres redes caen a profit factor < 1 y Sharpe negativo; la LR
  llega a +0.895 con profit factor 1.27.
- **Qué movió a las redes:** elegir la época por F1 de validación en lugar de
  la pérdida (+0.059 a la LSTM); la pérdida de validación nunca baja de
  ln 3 = 1.0986; reducir la LSTM de 592 k a 10 k parámetros no cambia nada;
  reentrenar con validación las empeora (−0.024 a −0.047).

## 9. Discussion [—]

- **¿Por qué gana la LR?** ~1 500 muestras por acción (10 500 globales) y 61
  entradas: redes de 10⁵–10⁶ parámetros sobreajustan; los indicadores ya
  capturan casi todo el contenido lineal; la penalización selecciona y
  estabiliza. Coincide con Grinsztajn et al. (datos tabulares); Gu, Kelly y
  Xiu ganan con redes en ~30 000 acciones y 60 años; Fischer y Krauss en todo
  el S&P 500; Patel et al. llegan a la misma conclusión con muestras
  parecidas. El régimen donde el aprendizaje profundo no paga: historias
  diarias cortas, etiqueta de un día casi ruido, variables que ya son
  agregados de varios días.
- **¿Por qué tanta variación entre acciones?** Acciones con tendencia o alta
  volatilidad (AMZN, TSLA, NVDA) premian a cualquier clasificador razonable;
  las laterales (GOOGL) no. Conviene preseleccionar acciones antes que elegir
  un modelo más complejo.
- **Agrupar acciones y cuándo usar redes:** el modelo global ayuda a XGBoost
  en los tres experimentos y a las redes en 7 de 9; para la LR da igual. La
  ventaja de LSTM y CNN-LSTM en caída máxima en §7 desaparece en §8. Las redes
  son atractivas con historias más largas o entradas más ricas.

## 10. Limitations [—]

Sin costos ni deslizamiento (con costos el orden entre modelos con
Sharpe < 0.5 se inclinaría hacia el que opera menos); siete acciones de un
sector; posición binaria; una sola partición por experimento. **Limitación
principal: las tres particiones prueban en 2025**; repetir el protocolo en
varios años de prueba es la extensión más valiosa. La búsqueda es simétrica
en procedimiento, no en dimensión; la conclusión se limita a esta
representación.

## 11. Conclusions [—]

Una LR multinomial con elasticnet sobre 61 indicadores gratuitos supera a tres
redes y a un XGBoost ajustado en F1-macro promedio en las tres particiones e
iguala o supera en economía; su margen sobrevive a la búsqueda simétrica, a un
protocolo sin decisiones con la prueba y a los intervalos bootstrap. La
preselección estadística no ayuda (11 de 15). La volatilidad de la acción
explica la mayor parte de la variación del Sharpe. Para datos diarios de
acciones grandes sin datos alternativos, un clasificador lineal bien
regularizado es un punto de partida competitivo y barato.

## Material suplementario (7 páginas)

| Sección | Contenido | La cita el artículo en |
|---|---|---|
| S1 | Las 61 variables por familia | §3.3 |
| S2 | F1-macro y F1 por clase de las 120 corridas | §5.1 |
| S3 | Métricas económicas de los Experimentos A y C | §7.1 |
| S4 | Mapa de calor del Sharpe por modelo y acción | §7.3 |
| S5 | Código, manifiesto de datos (SHA-256), semillas y versiones (PyTorch 2.12 con CUDA 12.8, scikit-learn 1.7.2, XGBoost 3.2.0, Optuna 4.8; Python 3.13.5) | §11 |
