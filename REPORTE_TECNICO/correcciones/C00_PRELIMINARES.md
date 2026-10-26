# C00 — Portada, resumen, abstract e índices (p. 0–7)

## Resumen de puntos

| ID | Página | Sección | Tema | Prioridad |
|---|---|---|---|---|
| 0-01 | Portada | — | "POLITÉCTICO" | CRÍTICO |
| 0-02 | Portada | — | "Computo" sin acento | IMPORTANTE |
| 0-03 | Portada | — | Apellido "Cuatiaquiz" | IMPORTANTE |
| 0-04 | Portada | — | Título registrado contra el resultado | IMPORTANTE |
| 0-05 | 1 | Resumen | "basada en modelos de aprendizaje profundo" | CRÍTICO |
| 0-06 | 1 | Resumen | "seleccionar la arquitectura de aprendizaje profundo más adecuada" | CRÍTICO |
| 0-07 | 1 | Resumen | 54 características | CRÍTICO |
| 0-08 | 1 | Resumen | Clases balanceadas / "ninguna residual" | IMPORTANTE |
| 0-09 | 1 | Resumen | Falta el protocolo final y las validaciones | CRÍTICO |
| 0-10 | 1 | Resumen | Métricas desactualizadas | IMPORTANTE |
| 0-11 | 1 | Resumen | **No dice el resultado** | CRÍTICO |
| 0-12 | 1 | Resumen | Plataforma y paper | IMPORTANTE |
| 0-13 | 1 | Resumen | "Palabras clave: Palabras clave:" | FORMA |
| 0-14 | 2 | Abstract | Mismos problemas que el resumen | CRÍTICO |
| 0-15 | 3–4 | Contenido | Títulos que cambian | IMPORTANTE |
| 0-16 | 5 | Índice de figuras | Seis figuras obsoletas, ninguna de resultados | IMPORTANTE |
| 0-17 | 6 | Índice de tablas | Títulos y tablas que desaparecen | FORMA |
| 0-18 | 7 | — | Página en blanco | FORMA |
| 0-19 | — | — | Falta lista de siglas | FORMA |

---

### 0-01 · Portada · CRÍTICO
**Dice:** "INSTITUTO POLITÉCTICO NACIONAL".
**Debe decir:** "INSTITUTO POLITÉCNICO NACIONAL".
**Por qué:** error ortográfico en la primera línea del documento.

### 0-02 · Portada · IMPORTANTE
**Dice:** "Escuela Superior de Computo".
**Debe decir:** "Escuela Superior de Cómputo".

### 0-03 · Portada · IMPORTANTE
**Dice:** "Jesús Baruc Polvo Cuatiaquiz".
**Acción:** verificar el apellido. En el artículo de MICAI se corrigió
"Cuatiaquiz" → **"Cuatianquiz"** el 2 de octubre (ver
`paper_review/README.md`). Usar la forma correcta en portada, paper,
referencias y plataforma («Acerca de»).

### 0-04 · Portada y resumen · IMPORTANTE
**Dice (título registrado):** "Diseño e implementación de un modelo de
aprendizaje profundo para el análisis y toma de decisión en el mercado
bursátil".
**Acción:** **no cambiar el título** (está registrado), pero el resumen, la
introducción y las conclusiones deben explicar en una frase por qué el
modelo desplegado es una Regresión Logística: el TT diseñó, implementó y
optimizó tres arquitecturas de aprendizaje profundo y las comparó contra
modelos de referencia, como pide el objetivo general; la comparación
mostró que, con datos diarios públicos y señal a un día, las redes no
superan a los clásicos, y el sistema despliega el mejor modelo según un
criterio declarado. Borrador: `textos/T01_resumen_abstract_intro.md` §3.
**Por qué:** es la primera pregunta previsible de un sinodal.

### 0-05 · p. 1 · Resumen, párrafo 1 · CRÍTICO
**Dice:** "una herramienta de análisis y toma de decisión… basada en modelos
de aprendizaje profundo".
**Debe decir:** "…basada en modelos de aprendizaje automático: se
compararon tres arquitecturas de aprendizaje profundo (LSTM, CNN 1D y
CNN-LSTM) con dos modelos clásicos (Regresión Logística y XGBoost)".
**Por qué:** la plataforma usa la LR (`api/ml/model.py`).

### 0-06 · p. 1 · Resumen, párrafo 3 · CRÍTICO
**Dice:** "Para seleccionar la arquitectura de aprendizaje profundo más
adecuada se realiza una comparativa entre cinco modelos: Regresión Logística
y XGBoost como referencias…".
**Debe decir:** "Para determinar si el aprendizaje profundo aporta una
ventaja sobre modelos más simples, se comparan cinco modelos bajo un mismo
protocolo…".

### 0-07 · p. 1 · Resumen, párrafo 3 · CRÍTICO
**Dice:** "54 características técnicas organizadas en nueve categorías".
**Debe decir:** "61 características técnicas organizadas en nueve familias"
(y, si se quiere, "a las que el modelo de la plataforma agrega 15
interacciones").
**Fuente:** Tabla 4 del propio documento; `ESTUDIO_TT/A_modelo/A2`. Ver C-01.

### 0-08 · p. 1 · Resumen, párrafo 2 · IMPORTANTE
**Dice:** "Ninguna se trata como clase residual; el esquema de etiquetado
por percentil rodante garantiza que las tres clases estén aproximadamente
balanceadas en el conjunto de entrenamiento".
**Debe decir:** "El etiquetado por percentil rodante produce una
distribución cercana a 30/40/30 (vender/mantener/comprar) en cualquier
régimen de mercado; el entrenamiento compensa la diferencia con pesos por
clase".
**Por qué:** "garantiza" es demasiado fuerte (la proporción varía por año:
2023 tuvo 48 % de mantener, ver A1 §5.8) y en producción el peso de
mantener se ajustó (× 0.90).

### 0-09 · p. 1 · Resumen, párrafo 4 · CRÍTICO
**Dice:** "Los experimentos se diseñan bajo tres esquemas de partición
temporal que cubren distintos regímenes de mercado entre 2014 y 2025".
**Falta:** que los tres comparten el año de prueba 2025; que los
hiperparámetros de los cinco modelos se buscaron con Optuna sin usar la
prueba; los intervalos de confianza; la prueba año por año 2020–2025 y la
prueba ciega 2026.

### 0-10 · p. 1 · Resumen, párrafo 4 · IMPORTANTE
**Dice:** "…principalmente F1-Score macro, con métricas económicas como el
Win Rate, el retorno acumulado simulado y el Sharpe Ratio".
**Debe decir:** "F1-macro como métrica principal, junto con kappa,
exactitud balanceada, AUC y pérdida logarítmica, y una simulación económica
(índice de Sharpe con y sin costos de transacción)".

### 0-11 · p. 1 · Resumen · CRÍTICO
**Falta el resultado.** Agregar: la LR obtuvo el mayor F1-macro en el año de
prueba (0.404, IC 95 % [0.379, 0.428], Exp B) y fue significativamente
mejor que los otros cuatro en los tres experimentos, con el mejor Sharpe
(+0.89; +0.62 con costos de 10 pb); en seis años de prueba año por año
empata con XGBoost y ambos superan a las redes; con datos de 2026 no usados
en ninguna decisión la LR siguió primera en clasificación.
**Fuente:** `03_CIFRAS_VIGENTES.md` §6–7.

### 0-12 · p. 1 · Resumen, último párrafo · IMPORTANTE
**Dice:** "Los resultados se presentan a través de una aplicación web…".
**Agregar:** que la aplicación está desplegada y actualiza la recomendación
cada día hábil, que muestra el modelo elegido y la comparación de los cinco,
y que la comparación se publicó en MICAI 2026 (Springer LNAI).

### 0-13 · p. 1 · Palabras clave · FORMA
**Dice:** "Palabras clave: Palabras clave: Aprendizaje profundo…".
**Debe decir:** "Palabras clave: aprendizaje profundo, regresión
logística, señales de trading, clasificación multiclase, series de tiempo
financieras".

### 0-14 · p. 2 · Abstract · CRÍTICO
Aplicar 0-05 a 0-13. Además:
- "This paper presents" → "This work presents" (es un reporte, no un paper).
- "54 technical features" → "61 technical features".
- Keywords: agregar "logistic regression".
Borrador completo en `textos/T01_resumen_abstract_intro.md` §2.

### 0-15 · p. 3–4 · Contenido · IMPORTANTE
- "1.2.2 Objetivo Específico" → "1.2.2 Objetivos específicos".
- "7. Análisis parcial de resultados" → "7. Conclusiones" (C-19).
- Regenerar con la estructura que se adopte (`01_ESTRUCTURA_PROPUESTA.md`).
- Agregar anexos (paper, reproducibilidad).

### 0-16 · p. 5 · Índice de figuras · IMPORTANTE
Las seis figuras son del capítulo 5 y todas quedan obsoletas (la Fig. 6
menciona PostgreSQL). El documento no tiene ninguna figura de metodología ni
de resultados. Nueva lista en `01_ESTRUCTURA_PROPUESTA.md` §3 y
`diagramas/README.md`.

### 0-17 · p. 6 · Índice de tablas · FORMA
- Tabla 2: "Activos seleccionados para su evaluación con los modelos de
  Deep Learning" → "Acciones del caso de estudio".
- Tablas 5–7 ("Selección de características Caso A/B/C") y Tabla 8
  (duplicada) desaparecen.
- Tablas 15–30 se reemplazan por las de `tablas/TABLAS_NUEVAS.md`.

### 0-18 · p. 7 · FORMA
Página en blanco después del índice de tablas: eliminar (o justificarla si
el formato de ESCOM la pide antes del capítulo 1).

### 0-19 · Nuevo · FORMA
Agregar una **lista de siglas** después de los índices: LR, XGBoost, LSTM,
CNN, F1, AUC, VIF, SHAP, OHLCV, SPY, VIX, ETF, EMH, API, REST, SPA, ORM,
pb (puntos base), IC (intervalo de confianza). El documento usa muchas sin
definirlas en un solo lugar.
