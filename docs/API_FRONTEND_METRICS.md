# API → Frontend: Métricas esperadas

El frontend de la pestaña `Rendimiento` espera recibir un array de objetos (por acción) con las siguientes claves. En la API, enviar estas claves (nombres sugeridos) para cada activo.

- `symbol` : string — Ticker / símbolo del activo
- `name` : string — Nombre legible del activo
- `cumulative_return_90d` : number — Retorno acumulado en los últimos 90 días (porcentaje, p. ej. 12.5)
- `return_vs_bh_90d` : number — Retorno vs Buy&Hold en 90 días (porcentaje)
- `sharpe_90d` : number — Sharpe ratio calculado en 90 días
- `max_drawdown_90d` : number — Máxima caída (%) en 90 días (positivo — el frontend muestra con signo "-")
- `win_rate_90d` : number — Win rate (%) en 90 días
- `profit_factor_90d` : number — Profit factor en 90 días
- `f1_macro_last_month` : number — F1 macro del último mes (0..1)
- `f1_buy_last_month` : number — F1 para señales BUY del último mes (0..1)
- `f1_sell_last_month` : number — F1 para señales SELL del último mes (0..1)
- `signal_buy_pct_90d` : number — % de señales BUY en los últimos 90 días (0..100)
- `signal_hold_pct_90d` : number — % de señales HOLD en los últimos 90 días (0..100)
- `signal_sell_pct_90d` : number — % de señales SELL en los últimos 90 días (0..100)

Notas:
- Los nombres de las claves en el frontend están mapeados a campos tipo `cumulativeReturn`, `return_vs_bh`, `sharpeRatio`, `maxDrawdown`, `winRate`, `profitFactor`, `f1_macro`, `f1_buy`, `f1_sell`, `signal_buy_pct`, `signal_hold_pct`, `signal_sell_pct`.
- Si la API usa nombres distintos, actualizar el mapping en `src/app/pages/Performance.tsx` en la función que procesa la respuesta.
- Enviar valores numéricos (floats). Para porcentajes, puede enviarse en formato 12.5 (no 0.125), el frontend asumirá la unidad mostrada.

Ejemplo de objeto por acción:

```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "cumulative_return_90d": 8.4,
  "return_vs_bh_90d": 1.2,
  "sharpe_90d": 1.05,
  "max_drawdown_90d": 5.3,
  "win_rate_90d": 62.1,
  "profit_factor_90d": 1.45,
  "f1_macro_last_month": 0.78,
  "f1_buy_last_month": 0.82,
  "f1_sell_last_month": 0.74,
  "signal_buy_pct_90d": 25.0,
  "signal_hold_pct_90d": 50.0,
  "signal_sell_pct_90d": 25.0
}
```
