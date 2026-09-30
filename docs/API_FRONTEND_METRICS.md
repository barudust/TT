# Métricas que la API entrega al frontend

`GET /stocks/:symbol/metrics?days=N` y `GET /metrics?days=N` (N ∈ 30, 60,
90) devuelven, por acción, las métricas de la ventana de los últimos N días
hábiles. Se calculan en `generate_metrics()` (`api/main.py`) con la
metodología de la tesis; el frontend solo las formatea.

## Cómo se evalúa cada día

La señal del día *t* se calcula con el cierre de *t* y apuesta por el
movimiento del cierre de *t* al cierre de *t+1*:

- **Etiqueta real** (`actualSignal`): la misma del entrenamiento
  (`api/ml/target.py`). Con `r = ln(C_{t+1}/C_t)`: BUY si `r` ≥ percentil 70
  de los 252 retornos previos del mismo activo, SELL si `r` ≤ percentil 30,
  HOLD en otro caso.
- **Estrategia**: BUY = posición larga (`+r`), SELL = posición corta (`−r`),
  HOLD = sin posición (0), abierta al cierre de *t* y cerrada al cierre de
  *t+1*, sin costos de transacción.
- El último día de la ventana todavía no tiene cierre siguiente: cuenta en
  la distribución de señales pero no en las métricas (`pendingPredictions`).

## Campos

| Campo | Unidad | Definición |
|---|---|---|
| `windowDays` | días | N solicitado |
| `periodStart`, `periodEnd` | fecha | primer y último día de la ventana |
| `totalPredictions` | n | señales emitidas en la ventana |
| `evaluatedPredictions` | n | señales con resultado conocido |
| `pendingPredictions` | n | señales aún sin cierre siguiente |
| `correctPredictions` | n | `prediction == actualSignal` |
| `accuracy` | 0–1 | `correctPredictions / evaluatedPredictions` |
| `f1_buy`, `f1_hold`, `f1_sell` | 0–1 | F1 de cada clase (scikit-learn) |
| `f1_macro` | 0–1 | promedio de los tres F1 (azar ≈ 0.33) |
| `cumulativeReturn` | % | `exp(Σ estrategia) − 1` |
| `bh_return` | % | comprar y mantener en los mismos días: `exp(Σ r) − 1` |
| `return_vs_bh` | puntos % | `cumulativeReturn − bh_return` |
| `sharpeRatio` | — | `√252 · media / desv. est.` de la estrategia diaria; `null` si hubo menos de 5 días con posición (no interpretable) |
| `bh_sharpe` | — | lo mismo para comprar y mantener |
| `maxDrawdown` | % (positivo) | mayor caída desde un máximo de la curva de capital de la estrategia |
| `winRate` | % | días con posición y ganancia / días con posición; `null` sin operaciones |
| `profitFactor` | — | Σ ganancias / Σ pérdidas en días con posición; `null` con menos de 5 días con posición o sin pérdidas |
| `numberOfTrades` | n | días con posición (cada señal BUY/SELL es una operación de 1 día) |
| `exposure` | % | días con posición / días evaluados |
| `finalCapital` | $ | 1000 × (1 + `cumulativeReturn`/100) |
| `avgConfidence` | 0–1 | confianza media de las señales emitidas |
| `signal_buy_pct`, `signal_hold_pct`, `signal_sell_pct` | % | distribución de señales emitidas |

Si ninguna señal de la ventana tiene resultado conocido, solo se envían los
campos de conteo, fechas, confianza y distribución.

## Historia

Hasta septiembre de 2026 estas métricas se calculaban distinto y no
correspondían a la tesis: la "señal correcta" se comparaba con el movimiento
del día *anterior* (±1 %), `f1_buy`/`f1_sell` eran en realidad precisiones,
el Sharpe y el drawdown se calculaban sobre el precio de la acción (no sobre
la estrategia) y la ventana siempre era de 30 días aunque la interfaz dijera
90. Ver `RESULTADOS_OPTIMIZADOS/docs/ANALISIS_HOLD_Y_GLOBAL.md` §5.
