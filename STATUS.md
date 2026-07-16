# Estado del proyecto

Última actualización: 2026-07-15.

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
  `RESULTADOS_OPTIMIZADOS/paper_latex/paper.tex` (el paper académico en
  inglés, también del 1 de junio, y el documento más riguroso/actualizado
  que hay). v4 nunca guardó modelos entrenables (solo CSVs de métricas),
  por eso el `.pkl` deployado sigue siendo el de v1 — no había otra
  opción real.
- **Conclusión que se sostiene en ambas**: LR gana en Sharpe y F1
  por-ticker de forma clara; en v4 XGBoost solo empata/gana F1-macro
  GLOBAL por un margen insignificante (0.0015) y con la mitad de Sharpe.
  El modelo elegido para producción sigue siendo el correcto.
- **Pendiente**: `paper_latex/paper.tex` no está referenciado desde
  `docs/README.md` como "la versión más reciente" — vale la pena
  revisarlo si se va a citar un número específico en la defensa.

Pendiente si se retoma el modelado: threshold calibration por clase,
stacking de los 4 modelos, walk-forward validation, costos de
transacción en el backtest (ver "Próximos pasos" en la bitácora).

## Plataforma web (`Proyecto/`)

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

## Huecos conocidos / no abordados

- No existe un `requirements.txt` para el pipeline de entrenamiento
  (`scripts_opt/`, `scripts_v1/`) — solo para `Proyecto/api/`. Reproducir
  el entrenamiento requiere instalar manualmente pandas, numpy,
  scikit-learn, xgboost, lightgbm, torch, optuna, pyarrow.
- Sin control de versiones previo de los datos (`tesis_ml_stocks/*.parquet`)
  más allá de este primer commit — son snapshots de Yahoo Finance del
  momento en que se corrieron los scripts.
- Decidir con tu compañero de equipo si el remoto compartido
  (`barudust/TT`) es donde quieren este repo unificado (más pesado ahora,
  ~435MB de historial) o si conviene separar app y datos de investigación
  en dos repos.
