# C03 — Capítulo 3: Estado del arte (p. 27–35)

> Es el capítulo en mejor estado. Los cambios son la Tabla 1, el orden de las
> citas, una verificación y cinco trabajos que conviene agregar porque el
> paper los usa y ayudan a explicar el resultado.

## Resumen de puntos

| ID | Página | Sección | Tema | Prioridad |
|---|---|---|---|---|
| 3-01 | 27 | 3 | Falta punto final | FORMA |
| 3-02 | 29–31 | 3.3–3.4 | Orden de las citas y [21] sin citar | FORMA |
| 3-03 | 30 | 3.3 | Verificar la descripción de Sonkavde et al. | IMPORTANTE |
| 3-04 | 31–32 | 3.4 | Faltan trabajos clave del paper | IMPORTANTE |
| 3-05 | 33 | 3.5, Tabla 1 | Año, evaluación y filas nuevas | IMPORTANTE |
| 3-06 | 32–33 | 3.5 | Precios de suscripción sin fecha | FORMA |
| 3-07 | 34 | 3.6 | "mismos datos y características": cumplirlo en el cap. 4 | IMPORTANTE |
| 3-08 | 35 | 3.6 | Mencionar la plataforma y el paper | FORMA |

---

### 3-01 · p. 27 · Introducción del capítulo · FORMA
"…la brecha de investigación que da origen al presente trabajo terminal"
→ agregar el punto final.

### 3-02 · p. 29–31 · Orden de citas · FORMA
Con estilo IEEE las referencias se numeran por orden de aparición. Hoy
aparecen [15] → [17] → [16] (p. 29–30) y [22] → [20] → [23] (p. 31), y la
[21] (Goodfellow et al.) no se cita en el texto. Al regenerar la
bibliografía con el gestor de referencias de Word se renumera solo; citar
[21] en §2.5.1 (ver 2-17).

### 3-03 · p. 30 · §3.3, párrafo 4 · IMPORTANTE
**Dice:** "Sonkavde et al. (2023) [19] proponen y evalúan un modelo de
stacking que combina Random Forest, XGBoost y LSTM para la regresión de
precio de cierre en dos acciones del mercado indio…".
**Acción:** verificar contra el artículo. La referencia [19] es *"Forecasting
stock market prices using machine learning and deep learning models: A
systematic review, performance analysis and discussion of implications"*
(una revisión sistemática). Si el experimento con stacking está dentro de
esa revisión, decir "como parte de su revisión, evalúan…"; si no, corregir
la cita.

### 3-04 · p. 31–32 · §3.4 · IMPORTANTE
**Agregar** un párrafo con los trabajos que el paper usa para explicar por
qué gana un modelo lineal, y que hoy no están en el reporte:
- **Sezer, Gudelek y Ozbayoglu (2020)**, revisión de más de 140 trabajos:
  dominan LSTM y CNN y casi nunca se incluye una línea base lineal.
- **Fischer y Krauss (2018)**: LSTM sobre los componentes del S&P 500.
- **Patel et al. (2015)**: con datos diarios y muestras de tamaño parecido,
  modelos regularizados igualan a las redes.
- **Grinsztajn, Oyallon y Varoquaux (2022)**: en datos tabulares con
  variables construidas, los árboles y modelos lineales igualan o superan a
  las redes.
- **Gu, Kelly y Xiu (2020)**: las redes ganan con ~30 000 acciones y 60
  años de datos, condiciones muy distintas a este trabajo.
Referencias completas en `correcciones/C08` y en `paper_review/paper.tex`.
**Por qué:** dan contexto al resultado sin que parezca un fracaso de las
redes, y el capítulo 7 los necesita para la discusión.

### 3-05 · p. 33 · §3.5, Tabla 1 · IMPORTANTE

| Fila | Dice | Debe decir |
|---|---|---|
| Año de lanzamiento | 2025 | **2026** (C-36) |
| Modelos subyacentes documentados | LR · XGBoost · LSTM · CNN 1D · CNN-LSTM | "Cinco modelos comparados y documentados; en producción, Regresión Logística" |
| Evaluación económica formal | Sharpe · Drawdown · Profit Factor | "F1-macro y otras 7 métricas; Sharpe con y sin costos; intervalos de confianza; prueba en varios años" |
| Acceso | Aplicación web gratuita | "Aplicación web gratuita y pública; código abierto" |

**Filas nuevas sugeridas** (todas con "No" para las comerciales, que no las
publican): "Comparación pública de modelos" (Sí: pestaña «Modelos»),
"Nivel de seguridad de la señal explicado" (Sí: tres niveles calibrados),
"Material para usuarios sin conocimientos" (Sí: «Aprende» y «Ayuda»).

### 3-06 · p. 32–33 · §3.5 · FORMA
Los precios de TrendSpider (52–155 USD/mes) y Trade Ideas (118 y 228
USD/mes) son de 2024. Verificar y poner "consultado el [fecha]" en las
referencias [25] y [26].

### 3-07 · p. 34 · §3.6, párrafo 3 · IMPORTANTE
**Dice:** "El presente trabajo terminal cubre esta laguna al evaluar los
cinco modelos bajo el mismo protocolo experimental, con los mismos datos,
las mismas características de entrada y las mismas métricas de
clasificación".
**Acción:** la frase es correcta para el trabajo final, pero hoy la
contradice el capítulo 4 (§4.1 y §4.4: cada modelo con variables distintas).
Se resuelve corrigiendo el capítulo 4 (ver 4-05 y 4-24). Sugerencia:
terminar con "…y las mismas métricas de clasificación y económicas, sobre
las mismas filas de prueba".

### 3-08 · p. 35 · §3.6, último párrafo · FORMA
Agregar al final: "…y despliega el modelo resultante en una plataforma web
pública que muestra también la comparación entre los cinco modelos. La
comparación fue publicada en MICAI 2026 [ref.]". (La cita del propio paper
puede ir aquí o en 1.5.)
