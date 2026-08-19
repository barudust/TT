# Estado del proyecto

Última actualización: 2026-07-16.

## Modelado (`scripts_opt/` → `RESULTADOS_OPTIMIZADOS/`)

**Completo.** Ganador declarado: Regresión Logística elasticnet, global,
Exp B. Comparado contra XGBoost, LightGBM, LSTM y CNN-LSTM en tres
particiones temporales (A/B/C), por-ticker y global. Bitácora completa en
`RESULTADOS_OPTIMIZADOS/docs/GUIA_PROGRESO.md`.

**Ojo con qué números citar** — hay dos evaluaciones con metodología
distinta y no son intercambiables:
- **v1** (`scripts_opt/opt_lr.py`, la que entrenó el `.pkl` que corre en
  producción): F1-macro=0.417, Sharpe=1.25 en Exp B. Es lo que reportan
  `GUIA_PROGRESO.md` y `docs/PAPER_FINAL.md` (ambos de mayo).
- **v4** ("splits unificados", mismo test=2025 en A/B/C — la corrida más
  reciente, 1 junio, "versión final para el paper" según su propio
  script): F1-macro=0.385 en Exp B, Sharpe=0.755. **No mencionada en
  GUIA_PROGRESO.md ni en PAPER_FINAL.md** — solo queda documentada en
  `paper/paper.tex` (el paper académico en inglés, también del 1 de
  junio, y el documento más riguroso/actualizado que hay). v4 nunca
  guardó modelos entrenables (solo CSVs de métricas), por eso el `.pkl`
  deployado sigue siendo el de v1 — no había otra opción real.
- **Conclusión que se sostiene en ambas**: LR gana en Sharpe y F1
  por-ticker de forma clara; en v4 XGBoost solo empata/gana F1-macro
  GLOBAL por un margen insignificante (0.0015) y con la mitad de Sharpe.
  El modelo elegido para producción sigue siendo el correcto.
- **Resuelto (14 ago)**: `paper/paper.tex` ahora está referenciado desde
  `paper/README.md` y desde el `README.md` raíz como "la versión más
  reciente/canónica" — ver sección de organización abajo.

Pendiente si se retoma el modelado: threshold calibration por clase,
stacking de los 4 modelos, walk-forward validation, costos de
transacción en el backtest (ver "Próximos pasos" en la bitácora). También
pendiente (a pedido del Revisor #2 de MICAI): darle a LSTM/CNN/CNN-LSTM una
búsqueda de hiperparámetros real con Optuna — hoy solo XGBoost la tiene, los
3 modelos profundos usan un grid fijo hecho a mano.

**Diagnóstico y plan nuevo (2026-08-14).** Antes de correr esa búsqueda se midió
qué está pasando realmente (`python scripts_opt/diag_deep.py`, 2.2 min) y el
resultado cambia las prioridades — detalle en
`RESULTADOS_OPTIMIZADOS/docs/DIAGNOSTICO_MODELOS_PROFUNDOS.md`:

- Un entrenamiento profundo cuesta **10 s**, no minutos: el cómputo nunca fue la
  restricción (caben 150 trials de Optuna por arquitectura en un par de horas).
- El early stopping por `val_loss` **restaura la época 1–2**: los modelos
  profundos del paper están entrenados ~1 época efectiva. Su `val_loss` nunca
  baja de ln(3) (= azar) en ninguna configuración probada, ni siquiera con un
  modelo 57× más chico → **no es un problema de hiperparámetros**.
- Tres asimetrías de protocolo frente a LR/XGBoost: el lookback se eligió con
  **F1 de test** (`consolidar_v4.py:35`, contradice `paper.tex:198`), LR/XGB
  reentrenan con train+val y los profundos no, y los profundos se evalúan sobre
  menos filas de test (1 316–1 596 vs 1 736) por cómo se construyen las ventanas.
- En **validación** los cinco modelos empatan dentro de 0.02 (LR 0.356,
  LSTM 0.357, XGBoost 0.374): el ranking del paper podría ser ruido de un único
  año de test, y hoy no hay ninguna prueba estadística que lo descarte.

Plan de trabajo vigente: `RESULTADOS_OPTIMIZADOS/docs/PLAN_MAESTRO_BUSQUEDA.md`
(siete vías con compuertas de decisión, ~6–8 h de GPU en total, solo con datos de
Yahoo Finance). `PLAN_OPTUNA_DEEP_MODELS.md` quedó marcado como superado.

## Plataforma web (`api/` + `Frontend/`)

**Fase 1 — conectar todo con datos/modelo reales: completa.**
API real (Yahoo Finance + 61 features + modelo ganador), persistencia en
SQLite, documentación reescrita para describir lo implementado.

**Fase 2 — scheduler, tests, overrides en BD, Docker: completa.**
Refresco automático diario (16:30 hora NY), suite de tests (verde),
overrides POST ahora persisten en BD, `Dockerfile`s + `docker-compose.yml`
(API+frontend). **Docker sin verificar en un build real** — el daemon no
estaba corriendo en el entorno donde se armó esto; correr
`docker compose up -d --build` una vez antes de confiar en ello. Android
descartado a propósito (queda como app web/PWA).

## Organización y unificación del repositorio (2026-07-15)

- Scripts sueltos movidos a `scripts_v1/`; docs de `RESULTADOS_OPTIMIZADOS/`
  organizados en `RESULTADOS_OPTIMIZADOS/docs/` (borradores de papers
  aparte); diagrama de arquitectura movido a `docs/`.
- **Limpieza (~676MB borrados, verificado que nada los referenciaba):**
  `tesis_ml_stocks/03_model_datasets` (484MB) y `04_models` (181MB) se
  recortaron a solo los CSV de resultados que `scripts_opt/comparar_baseline.py`
  y afines todavía leen; `tesis_ml_stocks/Validacion_A/B/C` (11MB) se
  eliminó por completo; `RESULTADOS_OPTIMIZADOS/v4_final/` se eliminó por
  ser un duplicado byte-a-byte de `reportes/v4_final/`. Todo lo demás
  (modelos_optimizados, logs, reportes, v3, v4, ensembles, stacking,
  etc.) se revisó y se conservó por tener valor documentado o estar
  activamente referenciado.
- **Repositorio unificado**: `Proyecto/` (que tenía su propio git con 17
  commits y remoto en GitHub `barudust/TT`) y todo lo demás
  (`scripts_opt/`, `RESULTADOS_OPTIMIZADOS/`, `scripts_v1/`,
  `tesis_ml_stocks/`, docs raíz) ahora viven en **un solo repositorio**,
  usando el historial real de `Proyecto/` como base (se descartó el
  historial del repo exterior de hoy mismo, que solo tenía 2 commits y
  ya había crecido a 669MB por haber commiteado el contenido que se borró
  después). `Proyecto/` pasó de ser la raíz del repo a ser una subcarpeta;
  git detectó los movimientos como renames.
- **Carpeta renombrada** de `Dataset_N` a `TT_Proyecto`.
- **Remoto de GitHub**: sigue apuntando a `barudust/TT` (heredado de
  `Proyecto/`), pero ese repo en GitHub hoy solo tiene el código web —
  nadie ha hecho push del contenido unificado (~435MB en `.git`). No se
  hizo push automáticamente. Ver la conversación para la evaluación de
  factibilidad de unificar en GitHub (nada supera el límite de 100MB por
  archivo; es factible con git normal, sin necesidad de Git LFS).

## Organización + preparación para Render (2026-07-16)

- **`scripts_opt/README.md` nuevo**: mismo formato vigente/obsoleto que ya
  existía para `scripts_v1/`. Confirma que `opt_lr.py` (config
  `LR-02-elasticnet-all`, exp B) generó el `.pkl` que corre en producción
  (verificado idéntico byte a byte), que `consolidar_120.py`/`reporte_final.py`
  son los consolidadores citados en el paper, y documenta qué de v2/v3/v4
  quedó como historial de iteración. `common_velas.py` (huérfano, sin
  importadores) y `comparar_baseline.py` (superado por `reporte_final.py`)
  quedaron señalados como candidatos a limpieza futura, sin borrar.
- **Higiene**: renombrados `scripts_v1/04-07_*.py` (traían un sufijo
  ` (1)` de descarga de navegador); el `package.json` del frontend traía el
  nombre de scaffold `@figma/my-make-file`, ahora `trading-signals-frontend`.
  Eliminado `RESULTADOS_OPTIMIZADOS/v4_final.zip` (backup manual del 1 de
  junio, duplicado/desactualizado respecto a `reportes/v4_final/` y
  `docs/` que ya viven en el repo).
- **Preparado para Render**: `render.yaml` en la raíz (Blueprint con
  `tt-api` Docker + `tt-frontend` static site, rama `dev`, autoDeploy en
  cada push). `api/wsgi.py` nuevo — necesario porque
  `initialize_data()`/`start_scheduler()` solo corrían dentro de
  `if __name__ == "__main__"` (a propósito, para que los tests puedan
  `import main` sin red real); gunicorn no ejecuta ese bloque, así que sin
  este entrypoint la API en producción nunca hubiera cargado datos.
  `api/Dockerfile` ahora corre gunicorn (1 worker — el scheduler no soporta
  varios) en vez del servidor de desarrollo de Flask, y respeta `$PORT` de
  Render. Detalle completo y limitaciones del plan free (spin-down,
  refresco automático poco confiable sin plan pago) en
  `docs/DEPLOY_RENDER.md`.
- **`dev` creada y sincronizada**: rama nueva, ya en GitHub y al día con
  `main`/`Baru` (fast-forward, sin conflictos — las tres apuntaban al mismo
  commit antes de este trabajo). El remoto de `origin` se cambió de HTTPS a
  SSH (`git@github-barudust:barudust/TT.git`) porque el push por HTTPS se
  quedaba esperando un login por navegador que no se podía completar; con
  SSH usa la llave `github-barudust` ya configurada.
- **Aplanado `Proyecto/` (mismo día, a pedido explícito)**: `Proyecto/`
  generaba la sensación de "API metida dentro de otra carpeta" y frontend
  suelto sin su propio espacio, así que se quitó el nivel intermedio:
  `Proyecto/api/` → `api/`, `Proyecto/docs/` → fusionado con `docs/` (que ya
  existía en la raíz), y todo el frontend (`src/`, `public/`, `package.json`,
  `vite.config.ts`, `Dockerfile`, `nginx.conf`, etc.) → `Frontend/`.
  `docker-compose.yml` y `.env.example` (el de nivel Docker Compose) subieron
  a la raíz junto con `render.yaml`. Se actualizaron todas las rutas que
  apuntaban a `Proyecto/` (`render.yaml`, `docker-compose.yml`,
  `.claude/launch.json`, este archivo, `README.md`,
  `scripts_v1/README.md`, `scripts_opt/README.md`) y se fusionaron
  `Proyecto/.gitignore` + `Proyecto/README.md` dentro de los archivos raíz
  equivalentes. Los `Dockerfile`s no necesitaron cambios internos (sus
  `COPY`/`ARG` son relativos al build context, que sigue siendo la misma
  carpeta, solo que ahora vive un nivel más arriba).
- **Blueprint desplegado y verificado en vivo**: `tt-api` (`tt-api-jc7n.onrender.com`)
  y `tt-frontend` (`tt-frontend-womf.onrender.com`) corriendo en Render.
  Se detectó un fallo real en el primer arranque: `initialize_data()`
  terminó sin poblar ningún ticker (`GET /stocks` → `[]`) por una falla
  transitoria de red/Yahoo Finance en el cold start del plan free — la API
  seguía "sana" (`/health` ok) porque ese endpoint no depende de los datos,
  pero el frontend no tenía nada que mostrar. `POST /admin/refresh` lo
  resolvió manualmente esa vez; ahora `initialize_data()` reintenta
  automáticamente (`FETCH_RETRY_ATTEMPTS`/`FETCH_RETRY_DELAY_SECONDS` en
  `api/main.py`, default 3 intentos / 5s) tanto el contexto de mercado como
  cada ticker antes de rendirse, y el `--timeout` de gunicorn subió de 120
  a 300s para no matar al worker mientras reintenta durante el arranque.
  Suite de tests (14) sigue en verde tras el cambio.

## Organización: carpeta `paper/` dedicada (2026-08-14)

- Todo lo del paper académico (repartido en tres sitios dentro de
  `RESULTADOS_OPTIMIZADOS/`) se movió a una carpeta `paper/` propia en la
  raíz: `RESULTADOS_OPTIMIZADOS/paper_latex/{paper.tex,figures/,README.md}`
  → `paper/{paper.tex,figures/,README.md}`;
  `RESULTADOS_OPTIMIZADOS/docs/PAPER_FINAL.md` → `paper/PAPER_FINAL.md`;
  `RESULTADOS_OPTIMIZADOS/docs/borradores/` → `paper/borradores/`. Todo
  vía `git mv`, historial preservado. `RESULTADOS_OPTIMIZADOS/` se queda
  solo con datos de experimentos (modelos, logs, reportes, bitácora
  `GUIA_PROGRESO.md`) — nada de prosa del paper. `paper.tex` sigue citando
  rutas como `RESULTADOS_OPTIMIZADOS/reportes/v4_final/*.csv` sin cambios,
  porque esa carpeta no se movió.
- Antes de este cambio, `git status` mostró la rama local 4 commits detrás
  de `origin/main` (los del aplanado de `Proyecto/` a `api/`+`Frontend/`+`docs/`
  y la preparación para Render, documentados arriba) — se hizo `git pull`
  primero y la reorganización de `paper/` se rehizo sobre esa base ya
  actualizada, no sobre la vieja estructura con `Proyecto/`.
- **Pendiente sin resolver**: `Proyecto/` quedó como carpeta huérfana en
  disco (no en git) con `.venv`, `node_modules`, `.pytest_cache`,
  `__pycache__`, `api/.env` y `api/trading_system.db` — nada de eso estaba
  trackeado, así que el aplanado no lo movió ni lo borró. Si sigues
  trabajando desde esta copia local, hace falta decidir si se copia el
  `.env` viejo a `api/.env` (el nuevo path) y se borra `Proyecto/` a mano,
  o si se regenera todo desde cero (`npm install` en `Frontend/`,
  `pip install` en `api/`).

## Huecos conocidos / no abordados

- No existe un `requirements.txt` para el pipeline de entrenamiento
  (`scripts_opt/`, `scripts_v1/`) — solo para `api/`. Reproducir
  el entrenamiento requiere instalar manualmente pandas, numpy,
  scikit-learn, xgboost, lightgbm, torch, optuna, pyarrow.
- Sin control de versiones previo de los datos (`tesis_ml_stocks/*.parquet`)
  más allá de este primer commit — son snapshots de Yahoo Finance del
  momento en que se corrieron los scripts.
- Decidir con tu compañero de equipo si el remoto compartido
  (`barudust/TT`) es donde quieren este repo unificado (más pesado ahora,
  ~435MB de historial) o si conviene separar app y datos de investigación
  en dos repos.
