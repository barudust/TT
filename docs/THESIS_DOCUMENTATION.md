# Guía para redactar el documento de tesis

Índice sugerido para el reporte del TT y, por cada capítulo, **de qué
documento del repositorio sacar el contenido y las cifras**. Las cifras
citadas aquí están verificadas al 2026-09-30.

| # | Capítulo | Fuente principal en el repo |
|---|---|---|
| 1 | Resumen | `RESULTADOS_OPTIMIZADOS/JUSTIFICACION_LIMITE_DEL_MODELO.md` (Resumen) |
| 2 | Introducción: motivación, objetivos, alcance (Yahoo Finance, 7 acciones, 5 modelos, señal diaria) | `GUIA_DEFENSA_TT.md` Cap. 1 · `JUSTIFICACION…` §1 |
| 3 | Marco teórico: series financieras, eficiencia de mercado, regresión logística y regularización, XGBoost, LSTM, CNN 1D, CNN-LSTM, métricas (F1-macro, kappa, Sharpe, drawdown) | `GUIA_DEFENSA_TT.md` Cap. 6–8 y Cap. 17 (P17.10–P17.18) |
| 4 | Estado del arte | Bibliografía de `paper_review/paper.tex` (Fischer y Krauss 2018; Gu, Kelly y Xiu 2020; Grinsztajn et al. 2022; Sezer et al. 2020; Patel et al. 2015) |
| 5 | Datos y etiqueta (61 indicadores, percentiles 30/70 rodantes, anti-fuga) | `GUIA_DEFENSA_TT.md` Cap. 2–4 · `INVESTIGACION_COMPLETA.md` §2 |
| 6 | Metodología experimental: splits A/B/C con test 2025, global y por ticker, Optuna, bootstrap, walk-forward | `GUIA_DEFENSA_TT.md` Cap. 5 y 9 · `RESULTADOS_V5.md` · `ANALISIS_HOLD_Y_GLOBAL.md` §7 |
| 7 | Resultados de los 5 modelos | `paper_review/paper.tex` §5–6 · `v5/resultados_finales.csv` |
| 8 | Robustez: walk-forward 2020–2025, permutaciones, IC bootstrap, costos de transacción | `ANALISIS_HOLD_Y_GLOBAL.md` §2.4 y §7 · `JUSTIFICACION…` §2–3, §8 |
| 9 | Global vs por ticker | `ANALISIS_HOLD_Y_GLOBAL.md` §4 · `JUSTIFICACION…` §7 |
| 10 | Lo que se probó y no funcionó (features, selección, ensambles, calibración, 40/60) | `INVESTIGACION_COMPLETA.md` §4–6 · `JUSTIFICACION…` §3, §6 |
| 11 | Exceso de MANTENER y ajuste del peso de clase | `ANALISIS_HOLD_Y_GLOBAL.md` §2 y §8 · `GUIA_DEFENSA_TT.md` P17.1–P17.8 |
| 12 | Sistema: arquitectura, API, frontend, base de datos, despliegue | `docs/API.md`, `docs/FRONTEND.md`, `docs/DATABASE.md`, `docs/DEPLOY_RENDER.md`, `docs/system_architecture_diagram.svg` (el `_propuesta_inicial.svg` sirve para contrastar propuesta y sistema final) |
| 13 | Evaluación en producción (2026 fuera de muestra) | `ANALISIS_HOLD_Y_GLOBAL.md` §6 y §8.3 · `scripts_opt/evaluar_produccion_2026.py` |
| 14 | Limitaciones y ética | `JUSTIFICACION…` §9 · aviso legal de la página "Acerca de" |
| 15 | Trabajo futuro | `JUSTIFICACION…` §10 · `GUIA_DEFENSA_TT.md` Cap. 16 |
| 16 | Conclusiones | `JUSTIFICACION…` Resumen y §11 |
| A | Anexos: instalación y ejecución, reproducibilidad, capturas | `README.md` · `scripts_opt/README.md` · `scripts_opt/requirements.txt` |

## Cifras clave (para no buscarlas)

| Qué | Valor | Fuente |
|---|---|---|
| F1-macro LR, test 2025, protocolo v5 | 0.404 (IC 95 % [0.379, 0.428]); Sharpe +0.89 | `v5/resultados_finales.csv`, paper §6 |
| Resto en test 2025 (v5) | XGBoost 0.359, LSTM 0.369, CNN 0.359, CNN-LSTM 0.372 | ídem |
| Walk-forward 2020–2025, F1 medio | XGBoost 0.356, LR 0.350, CNN-LSTM 0.328, LSTM 0.314, CNN 0.292; máximo de cualquier año 0.394 | `analisis_hold/5_walk_forward_v5_resumen.csv` |
| Costos 10 pb, Sharpe | LR +0.62, XGBoost +0.01 | `v5/resultados_finales.csv` |
| Global vs por ticker (LR, 21 casos) | Global gana 18/21, p = 0.002 | `analisis_hold/4a_global_vs_porticker_por_modelo.csv` |
| Modelo en producción | LR L2, 61 + 15 interacciones, pesos "balanced" con HOLD × 0.90 | `docs/MODEL_INTEGRATION.md` |
| Producción, 2026 fuera de muestra | F1 0.354, κ 0.035, HOLD 40 % (real 35 %) | `analisis_hold/8_confirmacion_2026.csv` |

## Recomendaciones de redacción
- Distinguir siempre **procedimiento evaluado** (protocolo con test 2025 y
  walk-forward) de **artefacto desplegado** (reentrenado con 2018–2025).
- No presentar las interacciones de la Vía 8 como mejora: se eligieron
  mirando 2025 y en validación empatan.
- Reportar κ junto a F1-macro: deja claro cuánto se acierta por encima del
  azar.
- No afirmar que CatBoost, GRU, TabNet o Transformers se probaron: no se
  corrieron (`GUIA_DEFENSA_TT.md` Cap. 12).
- Incluir diagramas del flujo de datos (Yahoo → features → modelo → API →
  frontend) y capturas de las cuatro páginas.
