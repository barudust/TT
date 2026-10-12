# B3 — Base de datos

> **Resumen.** SQLite con 4 tablas (`assets`, `ohlcv_daily`, `predictions`,
> `metrics`) definidas con SQLAlchemy. Guarda los precios diarios, cada
> señal del modelo con sus tres probabilidades y si acertó, y las métricas
> por ventana. Las tablas de datos base están en tercera forma normal; las
> de señales y métricas tienen columnas derivadas **a propósito** (son un
> registro de lo que el sistema calculó y mostró). Toda la base se puede
> reconstruir desde Yahoo Finance + el modelo, por eso en Render basta una
> base efímera. El esquema funciona igual en PostgreSQL.
>
> **Cambio respecto al TT1:** el TT1 diseñó PostgreSQL con 9 tablas y un ETL
> en un proceso aparte. Por qué cambió y qué se conservó: §4.
>
> Código: `api/database.py` (conexión), `api/models.py` (tablas),
> `api/db_ops.py` (inserción/actualización). Documento técnico:
> `docs/DATABASE.md`.

---

## 1. Modelo entidad-relación

```
┌──────────────┐ 1        N ┌──────────────────┐
│   assets     │───────────►│   ohlcv_daily    │   un precio por acción y día
│──────────────│            └──────────────────┘
│ id (PK)      │ 1        N ┌──────────────────┐
│ ticker (UQ)  │───────────►│   predictions    │   una señal por acción y día
│ name         │            └──────────────────┘
│ sector       │ 1        N ┌──────────────────┐
│ industry     │───────────►│     metrics      │   una fila por acción y ventana
└──────────────┘            └──────────────────┘
```

Una acción tiene muchos precios diarios, muchas predicciones y tres filas de
métricas (30, 60 y 90 días).

## 2. Las tablas

### `assets` — las acciones

| Columna | Tipo | Restricción | Significado |
|---|---|---|---|
| `id` | Integer | PK | Identificador interno |
| `ticker` | String(10) | Única, no nula | AAPL, MSFT… |
| `name` | String(100) | | Nombre de la empresa |
| `sector` | String(50) | | De Yahoo (`Ticker.info`) |
| `industry` | String(100) | | De Yahoo |

### `ohlcv_daily` — precios diarios

| Columna | Tipo | Restricción |
|---|---|---|
| `id` | Integer | PK |
| `asset_id` | Integer | FK → `assets.id`, no nula |
| `date` | Date | no nula |
| `open`, `high`, `low`, `close` | Numeric | |
| `volume` | BigInteger | |
| | | **Única (`asset_id`, `date`)** |

### `predictions` — una señal por acción y día

| Columna | Tipo | Significado |
|---|---|---|
| `id` | Integer PK | |
| `asset_id` | FK → `assets.id` | |
| `date` | Date | Día cuyo cierre generó la señal |
| `signal` | String(10) | `buy` / `hold` / `sell` |
| `prob_buy`, `prob_hold`, `prob_sell` | Numeric | Las tres probabilidades del modelo |
| `confidence` | Numeric | La probabilidad de la señal elegida |
| `actual_price` | Numeric | Cierre de ese día |
| `correct` | Integer (0/1, nulo) | Si la señal coincidió con lo que pasó al día siguiente; nulo mientras no existe ese cierre |
| `model_version` | String(50) | Qué modelo la generó |
| `created_at` | DateTime (UTC) | Cuándo se calculó |
| | | **Única (`asset_id`, `date`)** |

### `metrics` — métricas por ventana

| Columna | Significado |
|---|---|
| `id`, `asset_id` (FK), `window_days` (30/60/90), `model_version` | **Única (`asset_id`, `window_days`)** |
| `accuracy`, `f1_macro`, `f1_buy`, `f1_sell` | Clasificación |
| `cumulative_return`, `return_vs_bh`, `sharpe_ratio`, `max_drawdown`, `win_rate`, `profit_factor`, `number_of_trades`, `exposure`, `final_capital` | Estrategia |
| `signal_buy_pct`, `signal_hold_pct`, `signal_sell_pct` | Distribución de señales |
| `updated_at` | Última actualización (UTC) |

### Integridad

- **Llaves foráneas** de las tres tablas hacia `assets`.
- **Restricciones únicas** (`asset_id`, `date`) y (`asset_id`,
  `window_days`): imposibilitan duplicados y además crean índices para
  buscar por acción y fecha.
- **Borrado en cascada** desde `assets` (`cascade="all, delete-orphan"`):
  si se borra una acción, se borran sus precios, señales y métricas.
- **Upsert** (`db_ops.py`): si ya existe la fila (misma acción y fecha), se
  actualiza; si no, se inserta. Así recalcular no duplica nada.

### Tamaño aproximado

7 acciones × ~3 años descargados, menos los días de calentamiento de los
indicadores ≈ unos pocos miles de filas en `ohlcv_daily` y `predictions`,
21 en `metrics` y 7 en `assets`. Es una base pequeña.

---

## 3. ¿Está normalizada? (análisis forma por forma)

### 3.1 Primera forma normal (1FN): **sí**

- Todos los valores son atómicos (un número, una fecha, un texto).
- No hay grupos repetidos: las tres probabilidades son tres atributos
  distintos de una predicción (un conjunto fijo de tres clases), no una lista
  de tamaño variable.
- Cada tabla tiene llave primaria.

### 3.2 Segunda forma normal (2FN): **sí**

- La llave primaria de cada tabla es una sola columna (`id`), así que no
  puede haber dependencias parciales de esa llave.
- Las llaves candidatas naturales son compuestas: (`asset_id`, `date`) y
  (`asset_id`, `window_days`). Los atributos dependen de la **llave
  completa**: el cierre depende de la acción **y** del día; nada depende
  solo de la acción dentro de esas tablas (lo que depende solo de la acción,
  como el nombre o el sector, está en `assets`).

### 3.3 Tercera forma normal (3FN): **las tablas base sí; hay derivados intencionales**

| Tabla | ¿3FN? | Detalle |
|---|---|---|
| `ohlcv_daily` | **Sí** | Cada precio depende solo de (acción, día) |
| `assets` | Casi | `industry → sector` (una industria pertenece a un sector): dependencia transitiva `id → industry → sector`. Estrictamente, sector e industria irían en otra tabla |
| `predictions` | No del todo, a propósito | `confidence` = máximo de las tres probabilidades (derivada). `actual_price` repite el `close` de `ohlcv_daily` del mismo día. `correct` se deriva de la señal y del cierre del día siguiente. `model_version` es un texto repetido que podría ser una llave a una tabla de modelos |
| `metrics` | Es una tabla de agregados | Todo se calcula a partir de `predictions` y `ohlcv_daily`. Es información derivada guardada (una "vista materializada") |

### 3.4 ¿Por qué no se normalizó por completo?

La normalización evita **anomalías de actualización**: que al cambiar un
dato en un lugar quede desactualizado en otro. Aquí ese riesgo no existe
porque:

1. **Un solo escritor y recálculo total.** Solo la actualización diaria
   escribe, y en cada pasada recalcula y sobrescribe toda la ventana desde
   la fuente (Yahoo + modelo). Nunca se edita una fila a mano (los
   endpoints de escritura manual están desactivados). Los derivados no
   pueden quedar desincronizados entre actualizaciones.
2. **Es un registro de lo que se mostró.** `confidence`, `correct` y las
   métricas guardan exactamente lo que la plataforma calculó y mostró con
   cierta versión del modelo (`model_version`). Recalcularlas después con
   otro código podría dar otra cosa; guardarlas es lo que permite auditar.
3. **Lectura simple.** Consultar desempeño no requiere uniones ni recalcular
   agregados.
4. **Volumen mínimo.** Unos miles de filas: el espacio repetido es
   irrelevante.

Esta es una desnormalización consciente típica de tablas de hechos y de
agregados (como en un almacén de datos), no un descuido.

### 3.5 Si pidieran llevarla a 3FN estricta

1. Tabla `industries(id, name, sector)` y `assets.industry_id` (o
   `sectors` + `industries`).
2. Tabla `model_versions(id, version, trained_at, train_range, …)` y
   `predictions.model_version_id`, `metrics.model_version_id`.
3. Quitar `confidence` (= máx. de las probabilidades) y `actual_price` (=
   `ohlcv_daily.close`); obtenerlas con una consulta o una vista.
4. Convertir `metrics` y `correct` en **vistas** calculadas sobre
   `predictions` y `ohlcv_daily`.

El costo: consultas más complejas y perder la "foto" de lo que se mostró.

---

## 4. ¿Por qué SQLite y no PostgreSQL, como decía el TT1?

### 4.1 Qué proponía el TT1 (§4.3.1)

El reporte de TT1 diseñó una base **PostgreSQL** con **9 tablas en 3FN + 1
desnormalizada**:

| Tabla del TT1 | Contenido | ¿Qué pasó con ella? |
|---|---|---|
| `assets` | Activos (eje del esquema) | **Se mantiene** |
| `ohlcv_daily` | Precios diarios | **Se mantiene** |
| `features_daily` | 46 variables por acción y día | **Eliminada**: las 76 variables se recalculan en menos de un segundo desde el OHLCV; guardarlas obliga a mantenerlas sincronizadas con el código |
| `predictions` | Señal, 3 probabilidades, versión del modelo, `r_forward` | **Se mantiene** (con `confidence`, `actual_price` y `correct` en lugar de `r_forward`) |
| `daily_returns` | Retorno de la estrategia y buy & hold, capital acumulado, drawdown | **Absorbida** en `metrics` (ventanas 30/60/90) |
| `model_metrics_monthly` | F1 por mes, matriz de confusión en **JSONB** | **Sustituida** por `metrics` con ventanas móviles |
| `strategy_metrics_weekly` | Win rate y profit factor cada lunes | **Sustituida** por `metrics` |
| `strategy_metrics_monthly` | Sharpe, drawdown, Calmar por mes | **Sustituida** por `metrics` |
| `snapshots_90d` (desnormalizada) | Caché de 90 días para el panel | **Sustituida** por la caché en memoria de la API + `metrics` (ventana de 90) |

Con `ON DELETE RESTRICT` entre tablas, índices compuestos en
(`asset_id`, `date`) y un ETL que escribía directamente en PostgreSQL desde
un proceso aparte.

### 4.2 Las razones que daba el TT1 y por qué dejaron de aplicar

El TT1 justificó PostgreSQL sobre SQLite con tres argumentos (§4.1.1):

| Argumento del TT1 | Situación en el sistema final |
|---|---|
| **Transacciones con concurrencia:** el ETL y la API eran **procesos distintos** escribiendo y leyendo a la vez; SQLite bloquea al escribir | El ETL ahora corre **dentro del proceso de la API** (programador de tareas). Hay **un solo escritor**, protegido además por un candado (`threading.Lock`), y las lecturas salen de memoria. La limitación de SQLite no aplica. SQLite también es ACID (cada acción se guarda en una transacción con `commit`/`rollback`) |
| **JSONB** para guardar la matriz de confusión y la distribución de señales | No se guarda la matriz de confusión; la distribución de señales son 3 columnas numéricas. JSONB no hace falta |
| **Índices compuestos** por (`asset_id`, `date`) para consultas temporales | Las restricciones únicas (`asset_id`, `date`) y (`asset_id`, `window_days`) crean esos mismos índices en SQLite |

Y aparecieron razones nuevas:

1. **La base pasó a ser reconstruible.** Como el sistema recalcula toda la
   ventana desde Yahoo + el modelo en cada actualización, la base no guarda
   nada que no se pueda regenerar. No necesita respaldos ni un servidor
   dedicado.
2. **Despliegue sin costo.** El plan gratuito de Render no da disco
   persistente ni una base PostgreSQL permanente sin pagar; SQLite vive en
   el contenedor y se reconstruye al arrancar.
3. **Menos piezas que mantener.** Un servicio en vez de tres (ETL, base,
   API).

### 4.3 Lo que se conserva del diseño del TT1

- **Modelo relacional con `assets` como eje** y llaves foráneas.
- **Unicidad por acción y fecha.**
- **Una tabla de agregados desnormalizada a propósito** para responder
  rápido (antes `snapshots_90d`, ahora `metrics`): el TT1 ya justificaba
  esta excepción a la 3FN como "vista materializada".
- **Portabilidad:** el esquema usa tipos genéricos de SQLAlchemy y
  `docker-compose.yml` tiene un perfil con PostgreSQL 15. Volver a
  PostgreSQL es cambiar `DATABASE_URL`.

**Diferencia de detalle:** el TT1 usaba `ON DELETE RESTRICT` (no se puede
borrar un activo con historial); la implementación usa **borrado en
cascada**. Como la base se reconstruye y nunca se borra un activo en
operación, no tiene efecto práctico; si se quisiera proteger el historial,
bastaría cambiar a RESTRICT.

### 4.4 Cuándo sí convendría PostgreSQL

Si el ETL volviera a ser un proceso aparte, si hubiera varias instancias de
la API escribiendo, si se guardara información que no se puede regenerar
(por ejemplo, usuarios, carteras o el historial de señales de modelos
anteriores), o si se necesitaran consultas analíticas pesadas.

### 4.5 ¿Y MongoDB u otra NoSQL?

Los datos tienen estructura fija y relaciones claras (una acción tiene
muchos precios, señales y métricas) y se necesitan restricciones de
integridad. Es justo el caso del modelo relacional.

---

## 5. Cómo se usa la base en la práctica

- **Escritura:** en cada actualización, `persist_to_db()` hace *upsert* de
  la acción, sus precios, sus predicciones (fila por fila, por acción y
  fecha) y sus 3 filas de métricas, y confirma la transacción (`commit`).
  Si algo falla, se revierte (`rollback`) solo esa acción.
- **Lectura:** los endpoints `GET` responden desde la **caché en memoria**
  que se llena en el mismo paso, por velocidad. La base es el **registro
  persistente**: historial entre reinicios, auditoría (qué señal dio qué
  versión del modelo) y consultas SQL para análisis.
- **Sin tabla de variables:** las 76 variables se recalculan en memoria en
  menos de un segundo a partir del OHLCV; guardarlas sería redundante.

### En producción (Render)

El plan gratuito no tiene disco persistente: la base vive en el sistema de
archivos del contenedor y **se reconstruye en cada arranque**. Es aceptable
porque no guarda nada que no se pueda regenerar desde Yahoo + el `.pkl`. En
local con Docker se monta un volumen (`/data`) y sí persiste.

**Dilo así si preguntan:** "La base es un registro reconstruible, no la
fuente de verdad; la fuente de verdad son los datos de Yahoo y el modelo
versionado. Por eso una base efímera es suficiente en el plan gratuito, y
con un volumen o PostgreSQL sería persistente sin cambiar código."

---

## 6. Tecnologías

| Pieza | Qué es | Por qué |
|---|---|---|
| **SQLite** | Base relacional en un archivo | Ver §4 |
| **SQLAlchemy 2.0 (declarativo)** | ORM: las tablas son clases de Python | Independencia del motor; restricciones y relaciones declaradas en código |
| Sin Flask-SQLAlchemy / Alembic | — | Para este tamaño, sesiones manuales y `create_all` bastan; no hay migraciones porque la base se reconstruye |
| `python-dotenv` | Lee `DATABASE_URL` de `.env` | Configuración sin tocar código; sin contraseñas en el código |

---

## Preguntas de este tema

Están desarrolladas en [D6](../D_defensa/D6_PREGUNTAS_SISTEMA.md).
