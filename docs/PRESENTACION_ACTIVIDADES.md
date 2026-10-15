# Guía para presentar las 4 actividades

> Para cada actividad: **qué decir**, **qué archivos abrir** (con la línea) y
> **qué demostrar**. Unos 3–5 minutos por actividad.

**Antes de empezar**
- Abrir la API y el frontend 5 minutos antes (Render duerme el servicio y la
  primera carga tarda 20–40 s).
- Dejar abiertos en el editor los archivos de las tablas, cada uno en su línea.
- Tener capturas de respaldo por si Render o Yahoo fallan.

**URLs**
- API: `https://tt-api-jc7n.onrender.com`
- Frontend: `https://tt-frontend-womf.onrender.com`

**Orden sugerido:** plataforma en vivo (2 min) → Actividad 1 → Actividad 2 →
Actividades 3 y 4 juntas.

---

## Actividad 1. Ajuste de parámetros y reentrenamiento para mejorar el modelo y sus resultados

**Qué decir:** "Pasamos de hiperparámetros fijos a una búsqueda con Optuna
para los cinco modelos, la validamos en varios años y reentrenamos el modelo
de producción con el ajuste ganador."

| # | Archivo | Qué señalar |
|---|---|---|
| 1 | [scripts_opt/run_v5.py:467](../scripts_opt/run_v5.py) | `obj_lr` y `obj_xgb`: espacio de búsqueda (penalización, C, escalador…); el objetivo es el F1 de 2024, no el de la prueba |
| 2 | [scripts_opt/run_v5.py:240](../scripts_opt/run_v5.py) | `_muestrear`: lo que Optuna elige en las redes (capas, unidades, ventana, dropout, pérdida) |
| 3 | [RESULTADOS_OPTIMIZADOS/v5/ganadores_clasicos.json](../RESULTADOS_OPTIMIZADOS/v5/ganadores_clasicos.json) | Resultado de la búsqueda: L2, C = 0.000165, RobustScaler |
| 4 | [scripts_opt/ajuste_hold_rolling.py:65](../scripts_opt/ajuste_hold_rolling.py) | `PESOS_HOLD = (0.95, 0.90, 0.85, 0.80)`: pesos probados año por año (2019–2024) |
| 5 | [scripts_opt/entrenar_produccion.py:56](../scripts_opt/entrenar_produccion.py) | `LR_HP` y `PESO_HOLD = 0.90` (línea 68): reentrenamiento final con 2018–2025 |
| 6 | [api/ml/artifacts/lr_elasticnet_global_expB.metrics.json](../api/ml/artifacts/lr_elasticnet_global_expB.metrics.json) | Evidencia guardada junto al modelo: antes y después |

**Resultado a enseñar:** en 2026 (datos que el modelo nunca vio) el F1 sube
de **0.313 a 0.354** y MANTENER baja de **60 % a 40 %** (real 35 %).
Tabla visual: §8 de
[RESULTADOS_OPTIMIZADOS/docs/ANALISIS_HOLD_Y_GLOBAL.md](../RESULTADOS_OPTIMIZADOS/docs/ANALISIS_HOLD_Y_GLOBAL.md).

---

## Actividad 2. Desarrollo y configuración de la API para consultas externas

**Qué decir:** "API REST en Flask, de solo lectura, que se actualiza sola
después del cierre del mercado y responde JSON a cualquier cliente."

| # | Archivo | Qué señalar |
|---|---|---|
| 1 | [api/main.py:426](../api/main.py) | Los endpoints `@app.route` (`/health`, `/model`, `/stocks`, `/metrics`…) |
| 2 | [api/main.py:345](../api/main.py) | `_initialize_data`: descarga → variables → modelo → resultado real → métricas → base de datos |
| 3 | [api/main.py:728](../api/main.py) | `start_scheduler`: L–V 16:30 Nueva York y reintento cada 2 minutos |
| 4 | [api/ml/model.py](../api/ml/model.py) | `load_model` y `predict_row`: carga del `.pkl` y predicción |
| 5 | [api/Dockerfile](../api/Dockerfile) y [render.yaml](../render.yaml) | Configuración del despliegue (gunicorn, 1 worker, rama `main`) |
| 6 | [api/tests/](../api/tests/) | Las 24 pruebas automáticas |

**Demostración en vivo** (en el navegador):
- `https://tt-api-jc7n.onrender.com/health` → `stocksLoaded: 7`
- `https://tt-api-jc7n.onrender.com/model` → ficha del modelo leída del `.pkl`
- `https://tt-api-jc7n.onrender.com/stocks/AAPL/metrics?days=30`

Si piden pruebas: `cd api && pytest` → 23 en verde.

---

## Actividad 3. Programación de componentes visuales y navegación interactiva

**Qué decir:** "Aplicación de una sola página en React con TypeScript, con
componentes reutilizables y rutas."

| # | Archivo | Qué señalar |
|---|---|---|
| 1 | [Frontend/src/app/routes.ts](../Frontend/src/app/routes.ts) | Las 4 rutas: inicio, `stock/:symbol`, `performance`, `about` |
| 2 | [Frontend/src/app/Root.tsx:16](../Frontend/src/app/Root.tsx) | `navItems`: barra de navegación inferior y cambio de tema claro/oscuro |
| 3 | [Frontend/src/app/components/StockCard.tsx:16](../Frontend/src/app/components/StockCard.tsx) | Componente reutilizable: tarjeta que lleva al detalle con `Link` |
| 4 | [Frontend/src/app/pages/Home.tsx](../Frontend/src/app/pages/Home.tsx) | Consumo de la API (`fetch`), estados de carga y error, botón de actualizar |
| 5 | [Frontend/src/app/types.ts](../Frontend/src/app/types.ts) | Tipos de las respuestas de la API (TypeScript) |

**Demostración en vivo:** `https://tt-frontend-womf.onrender.com` → Hoy →
clic en una tarjeta → detalle → cambiar ventana 30/60/90 días → Resultados →
Ayuda (guía y glosario) → Acerca de → modo oscuro. Para mostrar que el
diseño es responsivo, reducir el ancho de la ventana del navegador.

---

## Actividad 4. Implementación de librerías para visualización de gráficas financieras

**Qué decir:** "Usamos Recharts, que se integra con React; cada gráfica
muestra datos reales de la API y referencias para interpretarlos (comprar y
mantener, línea del azar)."

| # | Archivo | Qué señalar |
|---|---|---|
| 1 | [Frontend/src/app/pages/StockDetail.tsx:176](../Frontend/src/app/pages/StockDetail.tsx) | `LineChart` del precio de cierre con un punto de color por señal (`CustomDot`), `Tooltip` y `ResponsiveContainer` |
| 2 | [Frontend/src/app/pages/Performance.tsx:165](../Frontend/src/app/pages/Performance.tsx) | `BarChart`: retorno de la estrategia contra comprar y mantener, línea en cero |
| 3 | [Frontend/src/app/pages/Performance.tsx:186](../Frontend/src/app/pages/Performance.tsx) | `BarChart` del F1 por acción con `ReferenceLine` en 33.3 % ("azar") |
| 4 | [Frontend/src/app/format.ts](../Frontend/src/app/format.ts) | Colores y formatos centralizados (porcentajes, fechas, color de cada señal) |
| 5 | [Frontend/package.json](../Frontend/package.json) | Dependencia `recharts` |

**Demostración en vivo:** pasar el mouse sobre la gráfica del detalle
(tooltips) y cambiar de 30 a 90 días para que se recalcule.
