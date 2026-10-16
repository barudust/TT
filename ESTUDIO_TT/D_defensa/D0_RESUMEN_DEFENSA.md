# D0 — Resumen de la sección "La defensa" (10 minutos)

> Las respuestas más probables, en una o dos líneas. Si te repreguntan, el
> enlace lleva a la respuesta completa.

---

## D1. Del TT1 a TT2 (lo primero que van a preguntar)

| En TT1 | Ahora | Por qué |
|---|---|---|
| Cada modelo con sus variables | Las 61 para todos | El TT1 dijo que así no se podía comparar; filtrar era peor 11/15 |
| Por acción como principal | Global | Gana o empata en los 5 |
| Exp A probaba 2024–2025 | 2025 | Para comparar A, B y C |
| Redes fijas, cuadrícula | Optuna para los 5 | Un entrenamiento tarda 7–12 s |
| Ganaba XGBoost | Gana la LR (empata en 6 años) | Con las 61 variables la LR subió 0.355 → 0.392 |
| PostgreSQL, ETL aparte | SQLite, ETL dentro de la API | Un solo escritor; base reconstruible |
| App "en desarrollo" | Desplegada | |

**Lo que no cambió:** problema, etiqueta, acciones, 5 modelos, CRISP-DM y la
conclusión (los clásicos igualan o superan a las redes).

→ [D1 completo](D1_TT1_VS_TT2.md)

## D2. Generales

- **Aporte:** 5 modelos con el mismo protocolo, evaluación de clasificación y
  económica, explicación medida de por qué las redes no ganan, sistema en
  producción.
- **¿F1 0.40 es bueno?** Azar 0.33; predecir la dirección diaria es casi
  imposible (mercado eficiente); que sea distinguible del azar ya es
  resultado.
- **Objetivos:** los cuatro cumplidos (pipeline, cinco modelos, comparación,
  app). La hipótesis de que el DL ganaría no se confirmó: es un resultado.
- **Metodología:** CRISP-DM + SCRUM.
- **Pendiente tuyo:** quién hizo qué (G13).

→ [D2 completo](D2_PREGUNTAS_GENERALES.md)

## D3. Datos

- **¿Por qué percentiles móviles?** Un umbral fijo cambia de significado con
  la volatilidad.
- **¿Por qué 30/70?** Clases balanceadas; 40/60 empeora (kappa −45 %).
- **¿Fuga de información?** Umbrales con `shift(1)`, escalador solo con
  entrenamiento, separación por tiempo.
- **¿Por qué 61 variables?** Cubren 9 familias; más no ayuda, menos es peor.

→ [D3 completo](D3_PREGUNTAS_DATOS.md)

## D4. Modelos

- **¿Por qué ganó la LR?** Poca señal y pocos datos → modelo rígido y muy
  regularizado (C = 0.000165); las variables ya son no lineales.
- **¿Cuántas capas?** LSTM 2 × 118; CNN 2 bloques; CNN-LSTM 2 bloques + 1
  LSTM. Las eligió Optuna (podía 1–3 / 1–4).
- **¿No las ajustaron bien?** v5 buscó 17–20 hiperparámetros; su pérdida de
  validación no baja del azar con ninguna configuración.
- **¿GRU, Transformer?** No se corrieron (solo LightGBM además de los 5).

→ [D4 completo](D4_PREGUNTAS_MODELOS.md)

## D5. Estadística

- **¿No es suerte?** IC bootstrap, permutación (0.4 % en 2025), walk-forward,
  2026.
- **¿Por qué no k-fold?** Mezcla futuro con pasado; usamos walk-forward.
- **¿Sharpe +0.9 significativo?** No solo: error estándar ≈ 1 en un año.
- **¿Por qué tanto MANTENER?** Voto dividido: sabe cuándo, no hacia dónde.
- **¿Data snooping?** Decisiones en validación; las interacciones se
  declaran no validadas.

→ [D5 completo](D5_PREGUNTAS_ESTADISTICA.md)

## D6. Sistema

- **Arquitectura:** cliente-servidor REST; ETL programado dentro de la API.
- **¿Por qué Flask?** API chica de lectura; Django sobraba.
- **¿Normalizada?** 1FN, 2FN; 3FN en tablas base con derivados a propósito.
- **¿Por qué SQLite si el TT1 decía PostgreSQL?** Un solo escritor, sin JSONB,
  base reconstruible; compatible con PostgreSQL.
- **¿Por qué 1 worker?** El programador corre en el proceso.
- **¿Pruebas?** 24 automáticas.

→ [D6 completo](D6_PREGUNTAS_SISTEMA.md)

## D7. Paper

- MICAI 2026; publica v4 + v5. En el paper la LR gana en 2025; en el TT,
  con 6 años, empata con XGBoost: no se contradicen (el paper declara el año
  único como su limitación).

→ [D7 completo](D7_PREGUNTAS_PAPER.md)

## D8. Trampa

- **"Apenas mejor que una moneda":** un resultado negativo bien medido es un
  resultado.
- **"Eligieron 2025 a conveniencia":** se fijó antes de ver resultados;
  reportamos años peores.
- **"TT1 y TT2 se contradicen":** TT2 corrigió lo que el TT1 señaló; la
  conclusión se mantuvo.
- **"¿Lo usarían con su dinero?":** No.

→ [D8 completo](D8_PREGUNTAS_TRAMPA.md)

---

## Las 5 cifras para tener en la cabeza

**0.404** (LR 2025) · **0.35** (media en 6 años) · **0.394** (máximo de
cualquier modelo en cualquier año) · **0.354** (2026 en vivo) · **ln 3**
(las redes no bajan de ahí).
