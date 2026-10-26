# C01 — Capítulo 1: Introducción (p. 8–10)

## Resumen de puntos

| ID | Página | Sección | Tema | Prioridad |
|---|---|---|---|---|
| 1-01 | 8 | 1 | Mayúscula después de coma | FORMA |
| 1-02 | 8 | 1 | Falta el hallazgo y la plataforma | IMPORTANTE |
| 1-03 | 8 | 1 | Organización del documento | FORMA |
| 1-04 | 9 | 1.1 | Motivación solo a favor del aprendizaje profundo | IMPORTANTE |
| 1-05 | 9 | 1.1 | "optimicen la precisión" | FORMA |
| 1-06 | 9 | 1.2 | "que se intentarán cumplir" | FORMA |
| 1-07 | 9–10 | 1.2 | Objetivos: no cambiar, pero mapearlos | IMPORTANTE |
| 1-08 | 10 | 1.3 | Periodo de datos sin 2026 | IMPORTANTE |
| 1-09 | 10 | 1.3 | "de forma estricta a cinco modelos" | IMPORTANTE |
| 1-10 | 10 | 1.3 | Falta qué queda fuera del planteamiento | IMPORTANTE |
| 1-11 | Nuevo | 1.5 | Productos del trabajo | IMPORTANTE |

---

### 1-01 · p. 8 · §1, párrafo 2 · FORMA
**Dice:** "…en el campo de la inteligencia artificial, Sobre todo en las
áreas…".
**Debe decir:** "…, sobre todo en las áreas…".

### 1-02 · p. 8 · §1, párrafo 4 · IMPORTANTE
**Dice:** el planteamiento de la comparativa termina en "…salidas
directamente interpretables como decisiones de inversión".
**Agregar** (2–3 líneas): qué se encontró (en esta tarea los modelos
clásicos igualan o superan a las redes; la LR es la mejor en la prueba
principal) y que el resultado se integra en una plataforma web desplegada.
Una introducción de TT2 puede adelantar el hallazgo.

### 1-03 · p. 8 · §1, último párrafo · FORMA
Actualizar la descripción de capítulos según la estructura final y
mencionar los anexos (artículo MICAI, reproducibilidad). El capítulo 7 es
"Conclusiones", no "Análisis parcial" (C-19).

### 1-04 · p. 9 · §1.1 · IMPORTANTE
**Dice:** "La necesidad de superar estas limitaciones justifica la
implementación de modelos de Aprendizaje Profundo… Por consiguiente, este
trabajo terminal va enfocado a la implementación y entrenamiento de
modelos que optimicen…".
**Acción:** conservar, pero equilibrar con una frase como: "Sin embargo,
las revisiones de la literatura señalan que estos trabajos rara vez incluyen
una línea base lineal bien ajustada (Sezer et al., 2020), por lo que no es
claro si la complejidad adicional se traduce en mejores señales. Este
trabajo implementa las tres arquitecturas y las contrasta, bajo un mismo
protocolo, con dos modelos clásicos de referencia."
**Por qué:** la motivación actual presupone que el aprendizaje profundo es
la solución; el resultado dice lo contrario y la motivación debe dejar
abierta la pregunta. Agregar la referencia de Sezer et al. (está en el paper).
Además: "al tomar linealidad y estacionariedad" → "al asumir linealidad y
estacionariedad".

### 1-05 · p. 9 · §1.1, último párrafo · FORMA
**Dice:** "modelos que optimicen la precisión en estimar la dirección".
**Debe decir:** "modelos que mejoren el desempeño al estimar la
dirección". *Precisión* es una métrica específica (2.6.1) y no es la
principal.

### 1-06 · p. 9 · §1.2 · FORMA
**Dice:** "los objetivos específicos que se intentarán cumplir".
**Debe decir:** "los objetivos que se plantearon" (el documento final
reporta lo que se hizo).

### 1-07 · p. 9–10 · §1.2.1 y §1.2.2 · IMPORTANTE
**Acción:** **no modificar** el objetivo general ni los cuatro específicos
(están en el protocolo registrado). Solo:
- Título "Objetivo Específico" → "Objetivos específicos".
- Asegurar que el capítulo 7 responda cada uno con evidencia (ver
  `correcciones/C07`): el objetivo 3 pide "Accuracy, Precision, Recall,
  F1-score, etc."; se reportan esas y además kappa, AUC, exactitud
  balanceada y pérdida logarítmica. El objetivo 4 ("visualizar los mejores
  modelos") se cumple con la plataforma, que además muestra la comparación
  de los cinco en la pestaña «Modelos».

### 1-08 · p. 10 · §1.3, párrafo 2 · IMPORTANTE
**Dice:** "La recopilación de datos históricos inicia el 1 de enero de 2013…
empleando efectivamente el periodo del 1 de enero de 2014 al 31 de diciembre
de 2025 para el modelado y evaluación".
**Agregar:** "Los datos de 2026 (enero a octubre) se usan únicamente como
validación ciega, sin intervenir en ninguna decisión, y la plataforma
descarga los datos de cada día hábil".

### 1-09 · p. 10 · §1.3, párrafo 2 · IMPORTANTE
**Dice:** "este trabajo terminal se limita de forma estricta a la evaluación
de cinco modelos".
**Acción:** conservar, pero agregar: "Como exploración complementaria se
probaron LightGBM, ensambles (stacking, voto suave y mezclas ponderadas) y
calibración de probabilidades; ninguno superó a la Regresión Logística y no
forman parte de la comparación principal" (Etapas 2 y 5).
**Por qué:** el capítulo 6 los reporta; el alcance no puede decir que solo
hubo cinco modelos sin mencionarlos.

### 1-10 · p. 10 · §1.3 · IMPORTANTE
**Agregar** un párrafo de lo que queda **fuera del planteamiento**: la
señal es diaria (horizonte de un día), la etiqueta es 30/70 y los datos son
precios gratuitos; cambiar cualquiera de las tres (otros horizontes, otros
percentiles, noticias, datos intradía, ejecución real de órdenes) es otro
problema y se deja como trabajo futuro. El sistema es demostrativo y no
constituye asesoría financiera.
**Fuente:** `ESTUDIO_TT/03_MAPA_DE_EXPERIMENTOS.md` §5.
**Por qué:** protege contra "¿por qué no probaron 5 días si daba más?".

### 1-11 · Nuevo · §1.5 Productos del trabajo · IMPORTANTE
Agregar una sección corta con: (1) la plataforma web desplegada (URL),
(2) el artículo aceptado en MICAI 2026 (Springer LNAI), (3) el repositorio
con el código, datos y resultados de todas las etapas. Borrador en
`textos/T01_resumen_abstract_intro.md` §4.
