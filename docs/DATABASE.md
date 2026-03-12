# Almacenamiento de Datos

## Objetivo
Persistir señales, históricos y métricas para ventanas 30/60/90 días sin necesidad de usuarios.

## Opción Local: SQLite
- Ventajas: ligero, sin servidor, suficiente para el tamaño del proyecto.
- Despliegue: archivo `.db` versionable (con cuidado).

### Esquema Propuesto
- `stocks`:
  - `symbol` (PK), `name`, `sector`, `industry`
- `prices`:
  - `id` (PK), `symbol` (FK), `date`, `open`, `high`, `low`, `close`, `volume`
- `signals`:
  - `id` (PK), `symbol` (FK), `date`, `signal` ("buy","sell","hold"), `confidence` (real), `correct` (bool), `actual_price`
- `metrics`:
  - `id` (PK), `symbol` (FK), `window_days` (30|60|90), `accuracy`, `buy_precision`, `sell_precision`, `hold_precision`, `f1_score`, `cumulative_return`, `sharpe_ratio`, `win_rate`, `profit_factor`, `max_drawdown`, `number_of_trades`, `exposure`, `final_capital`, `updated_at`

Claves:
- Índices por (`symbol`,`date`) en `prices` y `signals`.
- Control de ventanas en `metrics` mediante `window_days`.

### Integración
- Insertar precios diarios al cargar Yahoo Finance.
- Al ejecutar el modelo, insertar una fila en `signals` con la señal del día y su confianza.
- Recalcular métricas y sobrescribir la fila correspondiente en `metrics`.

## Opción Nube (Azure)
- Azure SQL Database (PostgreSQL flexible/managed o SQL Server) según preferencia.
- Alternativas: Azure Database for PostgreSQL o MySQL.
- Migración desde SQLite:
  - Exportación a CSV por tabla.
  - Importación con herramientas nativas del motor.
  - Ajustar tipos (booleanos, fechas) y claves.

## Consideraciones
- Consistencia temporal: usar UTC y normalizar fechas.
- Integridad: claves foráneas y cascadas al limpiar.
- Rendimiento: índices adecuados, partición por fecha si el volumen crece.
- Seguridad: restringir conexiones de escritura en producción; separar credenciales.

