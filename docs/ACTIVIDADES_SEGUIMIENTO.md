# Actividades para el profesor de seguimiento

Trabajo Terminal: predicción de señales BUY / HOLD / SELL en acciones con
aprendizaje automático y plataforma web de consulta.

Periodo reportado: 26 de agosto al 3 de octubre de 2026.

---

## Actividad 1. Cierre de la búsqueda de modelos y actualización del modelo de producción

**Fecha:** 25–26 de agosto de 2026

**Descripción:**
Se concluyó la etapa de optimización del modelo con dos vías finales:

- **Vía 7:** refinamiento posterior a la búsqueda de hiperparámetros con Optuna,
  que cerró la búsqueda sin encontrar una configuración mejor.
- **Vía 8:** exploración del dataset con cinco técnicas y sus combinaciones. La
  mejor fue agregar 15 términos de interacción entre variables.

Con ello, el modelo en producción pasó de una Regresión Logística elastic-net
con 61 variables a una Regresión Logística L2 con escalado robusto y 76
variables (61 base + 15 interacciones), reentrenada con los datos 2018–2025.
Se actualizaron el pipeline de variables de la API, las pruebas unitarias y se
verificó la predicción de punta a punta con datos reales descargados.
Además se integró la calibración de HOLD y los cambios de autores del paper
trabajados en otra rama del equipo.

**Evidencia:** commits `0185b44` (Vía 7), `229bb71` (Vía 8) y `817cc5a`;
`RESULTADOS_OPTIMIZADOS/INVESTIGACION_COMPLETA.md`; `api/ml/`.

---

## Actividad 2. Paper para MICAI 2026: revisión, versión final y material suplementario

**Fecha:** 26 de agosto al 3 de octubre de 2026

**Descripción:**
- Se atendieron los comentarios de los revisores #2 y #3 del congreso MICAI.
- Se redujo el artículo a 12 páginas (límite del formato LNCS de Springer) sin
  quitar contenido técnico.
- Se envió la versión *camera-ready* el 8 de septiembre.
- A petición de Springer se elaboró el material suplementario (7 páginas) que
  el artículo cita, verificado contra las Tablas 4–6 del paper. Se comprobó
  que las 24 corridas de Regresión Logística reportadas se reproducen exactas
  (`scripts_opt/replicar_lr_v4.py`).
- Se corrigió el apellido de un autor y se preparó el paquete final y el correo
  de respuesta a Springer.

**Evidencia:** `paper_review/` (paper, `supplementary/`, `compilar_paper.py`,
`correo_springer.txt`); `RESULTADOS_OPTIMIZADOS/v4/replica_lr_v4.csv`.

---

## Actividad 3. Análisis del exceso de HOLD, evaluación fuera de muestra y ajuste del modelo

**Fecha:** septiembre de 2026 (cierre el 30 de septiembre)

**Descripción:**
Se analizó por qué el modelo predecía HOLD en exceso (57 % predicho contra 42 %
real en 2025):

- En todos los casos predichos como HOLD, la suma P(BUY) + P(SELL) superaba a
  P(HOLD) ("voto dividido"), sobre todo con el VIX por debajo de su media anual.
- Cambiar la proporción a 40/60 no lo corregía y empeoraba κ y Sharpe.
- Se comparó el modelo global contra modelos por acción: el global gana
  (significativo en LR, LSTM y CNN; empate en XGBoost).
- Se evaluó el modelo con datos de 2026, fuera de la muestra de entrenamiento
  (F1 0.313).

Como corrección, se reentrenó el modelo reduciendo el peso de la clase HOLD a
0.90, valor elegido por validación de origen rodante 2019–2024. En 2026 la
proporción de HOLD bajó de 60 % a 40 % (real 35 %) y el F1 subió de 0.313 a
0.354. Se redactó un escrito que justifica los límites del modelo para la
defensa.

**Evidencia:** `scripts_opt/analisis_hold_global.py`,
`scripts_opt/ajuste_hold_rolling.py`, `scripts_opt/evaluar_produccion_2026.py`;
`RESULTADOS_OPTIMIZADOS/docs/ANALISIS_HOLD_Y_GLOBAL.md`;
`RESULTADOS_OPTIMIZADOS/JUSTIFICACION_LIMITE_DEL_MODELO.md`.

---

## Actividad 4. Corrección de la plataforma web, despliegue en Render y guía de defensa

**Fecha:** 30 de septiembre de 2026

**Descripción:**
- **Plataforma:** se corrigieron métricas que se mostraban mal: la columna
  "Correcta" comparaba contra el día anterior, los valores etiquetados como F1
  eran precisiones, Sharpe y drawdown se calculaban sobre el precio de la
  acción, las ventanas de 60/90 días no existían y el estado del mercado
  estaba fijo. Se agregaron los endpoints `GET /model` y `GET /market-status`,
  se desactivaron por defecto los endpoints de modificación manual y el
  service worker pasó a "network-first" para que los usuarios no se queden con
  la interfaz vieja. Pruebas de la API: 20/20.
- **Despliegue:** se verificó en Render que se sirve el modelo
  `LR-v8-interactions-holdw090`. Se agregó un reintento automático cada 2
  minutos para cuando la descarga de datos falla en el arranque, de modo que
  el catálogo de acciones se llena solo; `/health` reporta cuántas acciones
  están cargadas.
- **Repositorio:** se dejaron solo las ramas `main` (la que despliega Render)
  y `dev`.
- **Guía de defensa:** se escribió el documento de estudio del Trabajo
  Terminal, con un capítulo de preguntas probables de un sinodal experto en
  ML/DL y estadística, y se corrigieron afirmaciones de la documentación que
  no tenían respaldo en el código.

**Evidencia:** `api/`, `Frontend/`, `docs/API_FRONTEND_METRICS.md`,
`render.yaml`, `STATUS.md`, `RESULTADOS_OPTIMIZADOS/GUIA_DEFENSA_TT.md`.

---

## Pendientes para el cierre

1. Llevar al documento de tesis el walk-forward 2020–2025, el análisis y ajuste
   de HOLD, la comparación global vs por acción y la evaluación 2026.
2. Preparar la presentación de la defensa y ensayar con la guía.
3. Responder a Springer con el material suplementario y, al publicarse el DOI,
   regenerar la copia pública del paper.
