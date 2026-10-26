# 04 — El artículo frente al TT

> Qué parte del TT publica el artículo, qué hizo el TT después y los
> detalles finos que conviene saber antes de presentar o citar el artículo.
> Nombres de etapas: `../ESTUDIO_TT/03_MAPA_DE_EXPERIMENTOS.md`.

---

## 1. De qué etapa sale cada sección

| Sección del artículo | Contenido | Etapa del TT |
|---|---|---|
| §3 Datos y etiqueta | 7 acciones, 61 variables, etiqueta 30/70, A/B/C con prueba 2025 | Etapa 3 |
| §4 Modelos | Configuraciones de los cinco | Etapa 3 (texto heredado de TT1 en parte; ver §3 abajo) |
| §5 Evaluación | F1-macro, backtest sin costos, por qué no accuracy | Etapa 3 |
| §6 Preselección de variables | 11 de 15 a favor de usar todas | **Etapa 2** |
| §7 Resultados | 120 corridas, global y por acción, variación por acción | Etapa 3 |
| §8 Robustez | Protocolo dev/final, Optuna para los cinco, intervalos de B | **Etapa 4 (resultado principal del TT)** |
| §9–§11 | Discusión, limitaciones, conclusiones | — |

**No está en el artículo:** la Etapa 1 (TT1), la Etapa 2 salvo §6, los
intervalos de A y C, los costos de transacción, la prueba año por año, la
permutación, la Etapa 5, la Etapa 6, la prueba ciega 2026, las ocho métricas
y la plataforma.

## 2. Qué hizo el TT después (y que el artículo declara como limitación o trabajo futuro)

| El artículo dice | El TT ya tiene |
|---|---|
| "The main limitation is that all three splits test on 2025… rolling the protocol over several test years remains the most valuable extension" | **Prueba año por año 2020–2025:** LR 0.360 y XGBoost 0.356 empatan (diferencia +0.003, no significativa) y superan a las tres redes con significancia; ningún modelo pasa de 0.394 en ningún año |
| "We do not include transaction costs" | **Costos de 5 y 10 pb:** LR +0.89 → +0.62; XGBoost +0.46 → +0.01 (rotación 0.38 contra 0.65). Exactamente lo que el artículo anticipa: el orden se inclina hacia el que opera menos |
| Intervalos solo para B | Intervalos de A y C: la LR es significativamente mejor que los cuatro en los tres |
| Un solo periodo | **Prueba ciega 2026** (enero–22 de octubre, datos que nadie usó): LR primera en F1 (0.346), sin diferencia significativa salvo contra la CNN 1D; en Sharpe dos redes salen mejor ese periodo |
| F1 y economía | Las **ocho métricas** para los cinco sobre las mismas filas: la LR es la mejor en todas en A, B y C |
| Global vs por acción con métricas distintas (F1 sobre todas las filas contra promedio de F1 por acción) | Comparación **pareada sobre los mismos días**: el global gana o empata en los cinco; LR 18 de 21 pares, p = 0.002 |
| — | Exceso de HOLD explicado ("voto dividido" y régimen del VIX) y corregido (peso × 0.90) |
| — | Plataforma desplegada con la LR + 15 interacciones |
| §6 con filtros de la Etapa 2 | Multicolinealidad con el protocolo final: filtro VIF ≤ 10 (45 variables) → las 61 ganan en 11 de 15; el filtro perjudica a las redes |

**Cómo decirlo en el congreso:** "Since submission we extended the
evaluation to six test years and to unseen 2026 data; the qualitative
conclusion holds: the regularized classical models match or beat the deep
architectures. Between LR and XGBoost the six-year difference is not
significant." (Ver `07_PREGUNTAS_MICAI.md`.)

## 3. Detalles finos del texto publicado (conocerlos, no repetirlos)

| # | Detalle | Qué pasó realmente | Cómo responder si sale |
|---|---|---|---|
| 1 | §4 dice que la CNN-LSTM recibe cinco canales OHLCV normalizados por ventana | Frase heredada del diseño de TT1; el código de la Etapa 3 (`train_all_v4.py`) da a las cinco arquitecturas solo las mismas 61 variables | "That sentence describes an earlier design; in the reported runs all five models receive exactly the same 61 features" |
| 2 | §4 describe la LSTM como bidireccional | Cierto para §7 (Etapa 3). En §8 Optuna eligió una LSTM **unidireccional** de 2 × 118 con atención | "Section 7 uses a bidirectional LSTM; the Section 8 search selected a unidirectional one with attention; both rank below LR" |
| 3 | §7: ventana de las redes elegida con la prueba | Error de protocolo de la primera corrida; el artículo lo declara y la §8 lo corrige | "We disclose it; it favours the deep models, so Section 7 is a lower bound on LR's margin" |
| 4 | §6 viene de la Etapa 2 (particiones de TT1 en A) | Confirmado después con el protocolo final y otro filtro (VIF ≤ 10): 11 de 15 de nuevo | "The same 11-of-15 result reappears under the corrected protocol with a VIF filter fitted on training data only" |
| 5 | La LR de §7 es elasticnet; la de §8 es L2 con C = 0.000165 | Optuna podía elegir L1, L2 o elasticnet y eligió L2 | "With such strong regularization the L1 part adds nothing" |
| 6 | Tabla 4: negritas en el win rate de CNN-LSTM (0.505) aunque la CNN 1D tiene 0.510 | Detalle de formato | No mencionarlo; si lo señalan, reconocerlo |
| 7 | La ventana de las redes termina en *t − 1* (no ve el día *t*) | Detectado en octubre; medido con la LR: cuesta ≈ 0.007 de F1 | "We measured it: removing day t from LR costs about 0.007 macro-F1, far below the gap" |
| 8 | §9: el global ayuda a XGBoost en los tres experimentos y a las redes en 7 de 9 | Comparación con métricas no pareadas; la pareada del TT da el mismo sentido | — |

## 4. Coherencia entre el artículo y el reporte técnico

- El **resultado principal del reporte** (Etapa 4, LR 0.404 en B) es la
  **§8 del artículo**: coinciden.
- Las cifras de la Etapa 3 del reporte (LR 0.399 promedio) son la **Tabla 3**:
  coinciden.
- El reporte agrega A y C con intervalos, costos, seis años y 2026; no
  contradice al artículo, lo extiende.
- **Lo que el reporte no debe hacer:** presentar como propias del artículo
  cifras que no están en él (costos, 2026, año por año), ni repetir los
  detalles 1 y 2 de la tabla anterior como si fueran el diseño final.
