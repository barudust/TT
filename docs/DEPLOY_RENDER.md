# Despliegue en Render

`render.yaml` (raíz del repo) define dos servicios via [Blueprint](https://render.com/docs/blueprint-spec):

- **`tt-api`** — Docker (`api/Dockerfile`), gunicorn + 1 worker, expone `/health` para el health check.
- **`tt-frontend`** — static site (`npm ci && npm run build`, publica `Frontend/dist`).

Solo `api/` y `Frontend/` se despliegan. El resto del repo (`scripts_v1/`,
`scripts_opt/`, `tesis_ml_stocks/`, `RESULTADOS_OPTIMIZADOS/`) es el pipeline
de investigación que generó el modelo empaquetado en `api/ml/artifacts/`;
Render no lo necesita para servir la app.

## Primer despliegue

1. En el dashboard de Render: **New → Blueprint**, conectar el repo de GitHub
   (`barudust/TT` o el que corresponda) y la rama **`dev`** (es la que
   `render.yaml` tiene configurada en ambos servicios — cada push a `dev`
   dispara un deploy nuevo). Si más adelante cambias de rama, actualiza el
   campo `branch` en los dos servicios para que sigan coincidiendo.
2. Render crea `tt-api` y `tt-frontend`. Esperar a que `tt-api` termine su
   primer deploy y copiar su URL pública (`https://tt-api-XXXX.onrender.com`).
3. En el servicio `tt-frontend` → **Environment**, fijar `VITE_API_URL` con
   esa URL (quedó marcada `sync: false` en el blueprint a propósito: Render
   no puede conocerla de antemano porque depende del nombre que asigne).
   Redeploy manual de `tt-frontend` para que el build de Vite la hornee.
4. Verificar `GET https://tt-api-XXXX.onrender.com/health` → `{"status":"ok"}`
   y que el frontend cargue datos reales (Home muestra las 7 acciones).

Cada push posterior a la rama configurada dispara un deploy automático en
ambos servicios (`autoDeploy: true`).

## Limitaciones conocidas del plan free

- **La API se duerme tras ~15 min sin tráfico** (spin-down del plan free de
  Render). El primer request tras dormir tarda ~20-40s (reconstruye datos y
  señales desde cero, ver `initialize_data()` en `api/main.py`) — es
  esperable, no es un error.
- **Fallas transitorias de Yahoo Finance en el arranque en frío**: se
  observó al menos una vez que `initialize_data()` terminaba sin poblar
  ningún ticker (`GET /stocks` devolvía `[]`) tras un cold start, sin que
  la API cayera — el `/health` seguía respondiendo "ok" porque no depende
  de los datos. `initialize_data()` ahora reintenta (`FETCH_RETRY_ATTEMPTS`,
  default 3, con `FETCH_RETRY_DELAY_SECONDS` entre intentos, default 5) el
  contexto de mercado y cada ticker antes de darse por vencido, para
  autorrecuperarse de este tipo de falla sin intervención manual. Si aun así
  pasa, `POST /admin/refresh` fuerza un reintento inmediato.
- **El refresco automático diario** (`REFRESH_HOUR`/`REFRESH_MINUTE`, scheduler
  en `main.py`) solo corre si la instancia está despierta a esa hora. En plan
  free esto no está garantizado. Opciones si hace falta que sea confiable:
  - Plan pago (always-on), o
  - Un [Render Cron Job](https://render.com/docs/cronjobs) separado que
    haga `POST /admin/refresh` en el horario deseado (eso además despierta
    la instancia).
- **SQLite es efímero**: sin disco persistente en el plan free, la base se
  reconstruye en cada arranque/redeploy. Es el comportamiento esperado —
  `initialize_data()` recalcula y sobrescribe (upsert) toda la ventana de
  3 años con el modelo actual en cada arranque/refresco, así que no hay
  ningún dato en la BD que no sea reproducible desde Yahoo Finance + el
  `.pkl` (ver `docs/DATABASE.md`). Lo único que se pierde al reiniciar son
  los overrides manuales de `POST /stocks*`, que existen solo para
  pruebas/demos puntuales. No hace falta Postgres ni disco persistente
  para este proyecto tal como está diseñado.
- **`numInstances: 1` es obligatorio en `tt-api`**, no solo el default del
  plan free: el scheduler de refresco diario vive en memoria de un solo
  proceso (`start_scheduler()` en `main.py`); con 2+ instancias cada una
  correría su propio scheduler y downloads/refrescos se duplicarían. Si
  subes de plan, no actives autoscaling en este servicio.

## Alternativa: todo Docker

Si prefieres desplegar el frontend también como contenedor Docker (usando
`Frontend/Dockerfile` + `nginx.conf`, igual que `docker compose`) en vez de
static site, cambia el bloque `tt-frontend` de `render.yaml` a
`env: docker`, `dockerfilePath: ./Frontend/Dockerfile`,
`dockerContext: ./Frontend`, y pasa `VITE_API_URL` como `dockerBuildArgs`
en vez de `envVars` (el Dockerfile ya lo espera como `ARG`). El static site
es la opción por defecto aquí porque es gratis y no se duerme.
