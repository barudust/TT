# Presentaciones

Fuentes de las presentaciones hechas para el TT. Cada carpeta es un deck en
formato de diapositivas HTML (1920×1080): `project/deck.json` lleva el orden y
las secciones, y `project/slides/*.html` una diapositiva por archivo.

| Carpeta | Para qué | Diapositivas | Versión publicada |
|---|---|---|---|
| `avances_tt2/` | Primera entrega de avances de TT2 (corta, sin compromisos) | 14 (11 + 3 de respaldo R1–R3) | https://claude.ai/artifact/WdoBBC4siKkUz66kgtdrqx |
| `sinodales/` | Presentación completa para sinodales: problema, etapas 1–6, resultados con gráficas, paper | 27 | https://claude.ai/artifact/PCx4mSuhipdMm9tMAEcY66 |

Los enlaces son privados de la cuenta que los publicó; se comparten desde el
propio artifact. Si se pierde el acceso, estas carpetas bastan para volver a
publicarlos.

## Pendiente en `sinodales/`

Todavía no incluye lo que salió de las observaciones de la sinodal (26 oct):

- Prueba ciega 2026 de los cinco modelos (LR primero en F1 0.346, casi empatado;
  las redes ganan en Sharpe ese año). Fuente: `RESULTADOS_OPTIMIZADOS/observaciones_sinodal/4_ciega2026.csv`.
- Multicolinealidad: 61 variables contra filtro VIF ≤ 10 (las 61 ganan en 11 de 15).
  Fuente: `RESULTADOS_OPTIMIZADOS/observaciones_sinodal/3_multicolinealidad_resumen.csv`.
- Criterio de elección declarado (empate LR–XGBoost → parsimonia, costos,
  interpretabilidad). Fuente: `ESTUDIO_TT/D_defensa/D9_OBSERVACIONES_SINODAL.md`.

## La presentación del MICAI

Va aparte, con el material del paper: `../PAPER_MICAI/`.
