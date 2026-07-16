# Documentos de RESULTADOS_OPTIMIZADOS

- **`../paper_latex/paper.tex`** — el paper académico en inglés, LaTeX.
  Es el documento **más reciente y riguroso** (1 de junio, mismo día que
  `../v4/` y `../v4_final/`): usa la evaluación "splits unificados" (v4),
  que ninguno de los documentos de abajo menciona. Si vas a citar un
  número específico para la defensa, empieza aquí, no en `PAPER_FINAL.md`.
- **`GUIA_PROGRESO.md`** — bitácora interna completa: hipótesis,
  configuraciones probadas, resultados por experimento. Muy detallada,
  pero se quedó en la sesión de mayo — no cubre v3/v4/v4_final (junio).
- **`PAPER_FINAL.md`** — versión en español del paper (22 de mayo), con
  los números de la evaluación v1 (F1-macro=0.417, Sharpe=1.25 en Exp B).
  Distintos de los que reporta `paper.tex` (v4: F1-macro=0.385,
  Sharpe=0.755) — ver `../../STATUS.md` para por qué ambos son válidos y
  la conclusión no cambia.
- **`ANALISIS_FEATURE_SELECTION.md`** — por qué se usan las 61 features
  completas en vez de un subconjunto filtrado.
- **`ALTERNATIVAS_FUTURAS.md`** — ideas no exploradas (datos macro FRED,
  sentimiento FinBERT, IV de opciones, walk-forward validation).
- **`borradores/`** — versiones anteriores de `PAPER_FINAL.md`
  (`PAPER.md`, `PAPER_TESIS.md`), conservadas como historial de
  iteración, no como referencia vigente.

Ver también `../reportes/` (CSVs/JSON con las comparativas numéricas que
respaldan estos documentos, incluye `v1_vs_v3/` y `v4_final/`).
