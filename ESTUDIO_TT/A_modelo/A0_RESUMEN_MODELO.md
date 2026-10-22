# A0 — Resumen de la sección "El modelo" (10 minutos)

> Lo esencial de A1 a A7 para cuando no hay tiempo. Cada bloque termina con
> el enlace al documento completo.

---

## A1. Datos y etiqueta

- **Fuente:** Yahoo Finance (gratis y reproducible). Precios diarios OHLCV
  ajustados por *splits* y dividendos.
- **Acciones:** AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA (Magnificent 7):
  muy líquidas, historia completa y volatilidades distintas.
- **Contexto:** S&P 500 (SPY) y VIX, porque las acciones se mueven con el
  mercado.
- **Periodo:** 2013-12-31 a 2025-12-29 → 3 017 días por acción, 21 119 filas.
  2026 solo para evaluar en vivo.
- **Etiqueta:** `r = ln(C_{t+1}/C_t)`. COMPRAR si `r` ≥ percentil 70 de los
  252 días anteriores; VENDER si ≤ percentil 30; si no, MANTENER (~30/40/30).
- **Por qué así:** se adapta a la volatilidad de cada época; sin información
  futura (`shift(1)`); 40/60 y otros cortes son peores; 5 días sube el F1
  pero cambia el problema.
- **Cambio vs TT1:** el experimento A probaba en 2024–2025; ahora en 2025.

→ [A1 completo](A1_DATOS_Y_ETIQUETA.md)

## A2. Variables

- **61 variables** en 9 familias: retornos (5), momentum (4), medias móviles
  (9), volatilidad (8), osciladores (9), volumen (8), velas (7), calendario
  (5), mercado (6). Casi todas son razones o porcentajes, comparables entre
  acciones.
- **Producción:** + 15 interacciones (productos de pares) = **76**. Mejoraron
  2025 pero empatan en validación: se presentan como equivalentes.
- **Las más importantes:** VIX normalizado, volumen, VIX, volatilidad del
  S&P 500 → lo predecible es la magnitud del movimiento, no la dirección.
- **Cambio vs TT1:** antes cada modelo tenía su filtro (LR 3–8 variables,
  XGBoost 23–25, redes 3–25); filtrar fue peor en 11 de 15 casos, así que
  todos usan las 61. El "54" del texto del TT1 era un error de conteo.
- **Escalado:** RobustScaler (mediana y rango intercuartílico), ajustado solo
  con entrenamiento.

→ [A2 completo](A2_VARIABLES.md)

## A3. Protocolo y métricas

- **Separación por tiempo**, nunca al azar.
- **3 experimentos**, prueba 2025: A = 10 años, **B = 6 (2018–2023, principal)**,
  C = 4. Validación 2024.
- **Etapa 4 anidado:** decidir con 2024 (modo dev), evaluar 2025 una sola vez.
  Los cinco modelos sobre las mismas 1 736 filas.
- **Optuna:** LR y XGBoost 150 intentos; redes 80 con 17–20 hiperparámetros.
- **Métricas:** F1-macro (principal; azar 0.33), kappa, Sharpe, drawdown, win
  rate, profit factor; costos de 5 y 10 pb.
- **Contra la suerte:** bootstrap por bloques (2 000 × 20 días), permutación,
  prueba año por año 2020–2025, 2026 en vivo.

→ [A3 completo](A3_PROTOCOLO_Y_METRICAS.md)

## A4. Regresión Logística y XGBoost

- **LR (ganadora):** multinomial (softmax de 3 clases), **L2, C = 0.000165**
  (regularización muy fuerte → probabilidades cerca de 1/3), RobustScaler,
  pesos balanceados con MANTENER × 0.90, 231 parámetros.
- **Por qué gana:** poca señal + pocos datos → conviene un modelo rígido; las
  variables ya hacen el trabajo no lineal.
- **XGBoost:** 485 árboles, profundidad 9. Empata con la LR en 6 años
  (0.356 vs 0.350), pero cambia más de posición: con costos de 10 pb su
  Sharpe cae a +0.01 (LR +0.62).
- **Vs TT1:** en TT1 ganaba XGBoost porque la LR solo tenía 3–8 variables;
  con las 61 la LR por acción subió de 0.355 a 0.392.

→ [A4 completo](A4_MODELOS_CLASICOS.md)

## A5. Redes neuronales

| Red | Diseño ganador (Etapa 4, Optuna) | Parámetros |
|---|---|---:|
| LSTM | 2 capas × 118, atención, ventana 10 días | 198 480 |
| CNN 1D | 2 bloques (50 → 100 filtros, kernel 7), promedio global, densa 101 | 67 007 |
| CNN-LSTM | 2 bloques (77 → 154, kernel 7) + 1 LSTM de 136, ventana 20 | 276 109 |

- Las tres usan *focal loss*, AdamW y paro temprano; 5 semillas promediadas.
- **Por qué no ganan:** su pérdida de validación nunca baja del azar (ln 3);
  una LSTM 57 veces más chica rinde igual; las variables ya resumen los días
  que ellas leerían.
- **En TT1** tenían arquitectura fija (LSTM 2 × 128; la CNN 1D era la
  CNN-LSTM sin LSTM, como ablación).
- **A conocer:** su ventana termina un día antes que la LR (cuesta ≈ 0.007 de
  F1; no cambia la conclusión).

→ [A5 completo](A5_REDES_NEURONALES.md)

## A6. Evolución

| Versión | Qué fue |
|---|---|
| Etapa 1 = TT1 | Variables por modelo, por acción, redes fijas → XGBoost primero |
| Etapa 2 | Umbrales por clase y 94 variables: no sirven |
| **Etapa 3** | Misma prueba y mismas 61 variables para todos → **paper** |
| **Etapa 4** | Protocolo estricto, Optuna, intervalos, prueba año por año → LR significativa |
| Etapa 5 | Búsqueda de mejoras: solo las 15 interacciones, que luego empatan; cambiar la etiqueta queda fuera del planteamiento |
| Etapa 6 | Modelo de la plataforma: ajuste de mantener; 2026: F1 0.354 |
| Septiembre | Exceso de MANTENER y ajuste × 0.90 |

Equivalencias con los nombres viejos (v1 … v8): [mapa de experimentos](../03_MAPA_DE_EXPERIMENTOS.md).

→ [A6 completo](A6_ETAPAS_DEL_PROYECTO.md)

## A7. Resultados y límites

- **2025:** LR 0.404 [0.379, 0.428], Sharpe +0.89; los demás 0.359–0.372.
- **Prueba año por año:** XGBoost 0.356, LR 0.350, redes 0.29–0.33; ningún modelo
  pasa de 0.394 en ningún año.
- **2026 (producción):** F1 0.354, kappa 0.035.
- **Exceso de MANTENER:** "voto dividido" (sabe que habrá movimiento, no
  hacia dónde) + VIX bajo. Ajuste × 0.90: MANTENER 60 % → 40 % (real 35 %).
- **Global vs por acción:** gana o empata el global (LR 18 de 21, p = 0.002).
- **Lectura honesta:** hay señal, débil e inestable; 2025 fue el mejor año.

→ [A7 completo](A7_RESULTADOS_Y_LIMITES.md)
