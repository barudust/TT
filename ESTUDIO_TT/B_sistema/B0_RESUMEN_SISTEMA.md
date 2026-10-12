# B0 — Resumen de la sección "El sistema" (7 minutos)

> Lo esencial de B1 a B5.

---

## B1. Arquitectura

```
Investigación (offline, scripts_opt/) ──► modelo .pkl
Yahoo Finance ──► API Flask ──► SQLite
                     └──► JSON ──► App React (PWA) ──► navegador / celular
```

- **Dos mundos:** entrenar (pesado, una vez) y servir (ligero, diario). Solo
  pasan el `.pkl` y el código de las variables.
- **Mismo código de variables** en entrenamiento y API (si no, las métricas
  no valdrían).
- **Nada simulado:** todo sale de Yahoo o del modelo.
- **Vs TT1:** el TT1 tenía 6 capas con un ETL incremental aparte (cron) y
  PostgreSQL; ahora el ETL vive dentro de la API y recalcula todo cada día.

→ [B1 completo](B1_ARQUITECTURA.md)

## B2. API

- **Flask** + gunicorn. Rutas de lectura: `/health`, `/model`,
  `/market-status`, `/stocks`, `/stocks/:s`, `/history?days=`,
  `/metrics?days=`, `/info`. Escritura: `POST /admin/refresh`.
- **Actualización:** L–V 16:30 Nueva York (APScheduler), al arrancar y cada
  2 min si falta alguna acción. Recalcula ~3 años en segundos.
- **Flujo:** descargar → 76 variables → modelo → resultado real del día
  siguiente → métricas 30/60/90 → memoria + SQLite.
- **Sin mirar el futuro:** descarta la vela del día mientras el mercado está
  abierto; la última señal queda "pendiente".
- **Auditoría (30 sep):** se corrigieron métricas mal calculadas; ahora mide
  igual que la tesis. Los POST de carga manual están desactivados (403).
- **23 pruebas** automáticas.

→ [B2 completo](B2_API.md)

## B3. Base de datos

- **SQLite + SQLAlchemy**, 4 tablas: `assets`, `ohlcv_daily` (único por
  acción + fecha), `predictions` (señal, 3 probabilidades, acierto, versión
  del modelo), `metrics` (por acción y ventana 30/60/90).
- **Normalización:** 1FN y 2FN sí; 3FN en tablas base; columnas derivadas a
  propósito (confianza, acierto, métricas) como registro de lo mostrado. Sin
  riesgo de anomalías: un solo proceso recalcula todo.
- **Por qué no PostgreSQL (como decía el TT1):** sus razones dejaron de
  aplicar (ya no hay dos procesos escribiendo; no se guarda JSONB) y la base
  es reconstruible. Volver a PostgreSQL = cambiar `DATABASE_URL`.

→ [B3 completo](B3_BASE_DE_DATOS.md)

## B4. Frontend

- **React 18 + TypeScript + Vite + Tailwind + Recharts**, **PWA** instalable.
- **4 páginas:** señales del día, detalle por acción, rendimiento global,
  acerca de (ficha del modelo leída de la API).
- Muestra las 3 probabilidades (azar 33 %), el resultado de cada señal y el
  F1 contra el azar; aviso legal.
- **Vs TT1:** no se hicieron la curva de capital, la matriz de confusión ni
  la consulta cada hora.

→ [B4 completo](B4_FRONTEND.md)

## B5. Despliegue

- **Render:** API en Docker (1 worker por el programador de tareas) +
  frontend como sitio estático; despliegue automático desde `main`.
- **Problemas reales resueltos:** arranque en frío (20–40 s), Yahoo fallando
  al arrancar (reintentos), PWA con interfaz vieja (network-first).
- **Vs TT1:** antes solo corría en local.

→ [B5 completo](B5_DESPLIEGUE.md)
