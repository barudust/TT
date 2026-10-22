# C1 — El paper de MICAI 2026

> **Resumen.** El paper publica una parte del TT: la comparación de los 5
> modelos en las 120 corridas de la **Etapa 3** (§7) y su verificación con el
> protocolo final de la **Etapa 4** (§8: búsqueda simétrica con Optuna,
> ninguna decisión con la prueba e intervalos de confianza), más el
> experimento de preselección de variables de la **Etapa 2** (§6). Qué viene
> de cada etapa: [mapa de experimentos §6](../03_MAPA_DE_EXPERIMENTOS.md#6-qué-usa-el-paper-sección-por-sección). Fue aceptado en MICAI 2026 y la versión final se envió el
> 8 de septiembre. Es un **producto extra**: suma valor al TT y sirve como
> respaldo en la defensa (pasó revisión por pares), pero el TT es más amplio
> y siguió avanzando después.
>
> Archivos: `paper_review/paper.tex` (versión canónica),
> `paper_review/paper.pdf` (copia pública), `paper_review/supplementary/`
> (material suplementario), `paper_review/README.md`.

---

## 1. Datos del paper

| | |
|---|---|
| Título | *A Benchmark of Five Machine-Learning Architectures for Daily Trading-Signal Classification on US Tech Equities* |
| Autores | Jesús Baruc Polvo Cuatianquiz, Abdiel Reyes Vera, Emmanuel Juárez Carbajal, David Reyes Ramos, Maribel Aragón García |
| Congreso | MICAI 2026 (*Mexican International Conference on Artificial Intelligence*) |
| Publicación | Springer, *Lecture Notes in Artificial Intelligence* (LNAI), capítulo 171490174 |
| Formato | LNCS, una columna, máximo 12 páginas, inglés |
| Estado | Aceptado; *camera-ready* enviado el 8 de septiembre de 2026; material suplementario preparado el 2–3 de octubre |
| Pendiente | Responder a Springer con el suplementario y el paquete con el apellido corregido; al salir el DOI, regenerar la copia pública |

---

## 2. Qué dice (sección por sección)

| Sección | Contenido |
|---|---|
| 1. Introducción | Tres problemas frecuentes en la literatura: comparar solo 1–2 modelos, medir con accuracy o RMSE (que no se traducen en dinero) y filtrar variables sin comprobar que ayude. El paper ataca los tres |
| 2. Trabajo relacionado | Sezer et al. (revisión de 140+ trabajos: dominan LSTM y CNN y casi nunca hay una línea base lineal), Fischer y Krauss (LSTM en el S&P 500), Patel et al. (modelos regularizados igualan a redes en datos diarios), XGBoost y Optuna. El hueco: nadie compara LR, XGBoost y tres redes bajo un mismo protocolo con evaluación de clasificación y económica |
| 3. Datos y etiqueta | Las 7 acciones, 2013–2025, Yahoo; etiqueta 30/70 móvil; 61 variables en 9 familias; los 3 experimentos; **por qué 2025 es un año de prueba defendible** (retorno debajo de la mediana, volatilidad alta) |
| 4. Modelos | Configuración de los cinco en la Etapa 3 |
| 5. Evaluación | F1-macro como métrica principal; simulación económica; por qué no accuracy |
| 6. Selección de variables (Etapa 2) | Filtrar con Pearson/VIF/SHAP/Spearman empeora en 11 de 15 casos. **Ojo:** se corrió con las particiones de TT1 (A probaba 2024–2025) y la mejor configuración elegida con la prueba; la conclusión se confirma en la Etapa 3 |
| 7. Resultados (Etapa 3) | Modelos globales y por acción; de dónde viene la variación entre acciones; efecto de los años de entrenamiento; distribución de señales; detalle por acción |
| 8. Robustez (Etapa 4) | Protocolo sin decisiones con la prueba, búsqueda simétrica, intervalos bootstrap: **la LR queda significativamente arriba de los otros cuatro** |
| 9. Discusión | Por qué gana la LR; por qué la acción importa más que el modelo; cuándo usar redes |
| 10. Limitaciones | Un solo año de prueba; sin costos; 7 acciones; búsqueda simétrica en procedimiento pero no en dimensión |
| 11. Conclusiones | Un clasificador lineal bien regularizado es un punto de partida competitivo y barato para datos diarios sin fuentes alternativas |

### 2.1 Las cifras del paper

**§7 (Etapa 3), F1-macro global en 2025:**

| Modelo | Exp A | Exp B | Exp C | Promedio |
|---|---:|---:|---:|---:|
| **LR** | **0.411** | 0.385 | **0.401** | **0.399** |
| XGBoost | 0.396 | **0.386** | 0.373 | 0.385 |
| CNN-LSTM | 0.376 | 0.384 | 0.371 | 0.377 |
| LSTM | 0.389 | 0.370 | 0.370 | 0.376 |
| CNN 1D | 0.361 | 0.343 | 0.373 | 0.359 |

Exp B, economía: LR profit factor 1.21 y Sharpe **+0.76** (los más altos).

**§8 (Etapa 4), Exp B global:** LR 0.404 [0.379, 0.428], Sharpe +0.895; los
demás 0.359–0.372 con Sharpe negativo salvo XGBoost (+0.46).

**Otros hallazgos del paper:**

- La **acción explica 4.5 veces más** variación del Sharpe que el modelo
  (15.5 % contra 3.4 % de la suma de cuadrados; el experimento 7.0 %; el
  resto es interacción y ruido). AMZN sale bien con casi cualquier modelo;
  GOOGL mal con casi todos.
- Lo que más movió a las redes no fue un hiperparámetro sino **elegir la
  época por F1 de validación** (+0.059 a la LSTM).
- La pérdida de validación de las redes nunca baja de ln 3; achicar la LSTM
  de 592 000 a 10 000 parámetros no cambia nada.
- Reentrenar las redes con entrenamiento + validación las empeora.

---

## 3. El proceso de revisión

1. **Envío inicial** con los resultados de la Etapa 3.
2. **Comentarios de los revisores** (#2 y #3). Lo principal:
   - Las redes no tuvieron una búsqueda de hiperparámetros comparable a la
     de XGBoost.
   - El texto de las figuras era ilegible al imprimirse.
3. **Respuesta (agosto):**
   - Se hizo el diagnóstico de las redes y el protocolo de la Etapa 4 completo (esto
     agregó la **§8**).
   - Se transparentó en §7 que el lookback de las redes se eligió con la
     prueba (ventaja para ellas, así que el margen de la LR es un límite
     inferior).
   - Se regeneraron las figuras al tamaño impreso real
     (`scripts_opt/plots_paper.py`).
   - Se recortó a 12 páginas sin quitar contenido técnico; la tabla de
     variables y el mapa de calor del Sharpe pasaron al suplementario.
4. **Camera-ready** el 8 de septiembre.
5. **Springer pidió el material suplementario** que el paper cita en cinco
   lugares (§3.3, §5.1, §7.1, §7.3, §11). Se generó un PDF de 7 páginas
   verificado contra las tablas del paper; incluye versiones de bibliotecas
   y dos pruebas de reproducibilidad (las 18 corridas secuenciales globales
   y las 24 de LR se reproducen exactas).
6. Corrección del apellido "Cuatiaquiz" → **"Cuatianquiz"**.

---

## 3b. Relación con el reporte de TT1

El paper **no** usa los resultados del TT1: usa la corrida de la Etapa 3 (misma prueba
2025 en los tres experimentos, las 61 variables para todos los modelos) y la
Etapa 4. Por eso sus cifras difieren de las del TT1 (en TT1 XGBoost era primero
con 0.369 por acción; en el paper la LR es primera con 0.399 en global).

Sí hereda del TT1 parte de la redacción de los modelos (§4 del paper), y ahí
hay un detalle a conocer: el paper dice que **la CNN-LSTM recibe 5 canales
OHLCV normalizados por ventana**, como en el TT1, pero el código de la Etapa 3
(`train_all_v4.py`) le da solo las 61 variables. Si lo preguntan: "es una
frase heredada del diseño de TT1; en la corrida publicada las cinco
arquitecturas reciben exactamente las mismas 61 variables, que era
justamente la corrección que necesitábamos para comparar".

---

## 4. Qué cambió en el TT después del paper

| Tema | En el paper | En el TT ahora |
|---|---|---|
| Años de prueba | Solo 2025 (lo reconoce como la limitación principal) | **Prueba año por año 2020–2025** + **2026 fuera de muestra** |
| Costos de transacción | No incluidos (limitación) | Calculados con 5 y 10 pb (la LR gana con más margen) |
| Modelo LR | Elasticnet, C ∈ {0.01, 0.1, 1} (Etapa 3); L2, C = 0.000165 (Etapa 4) | En producción: L2, C = 0.000165, **+ 15 interacciones**, **peso de MANTENER × 0.90** |
| Refinamientos | — | **Etapa 5** (calibración, mezclas, SWA, recencia) |
| Dataset | 61 variables | **Etapa 5**: otros horizontes y percentiles, rezagos, interacciones, multi-escala, entre activos |
| Global contra por acción | Comparación con métricas distintas (F1 global sobre todas las filas contra promedio de F1 por acción) | Comparación **pareada sobre las mismas filas**: el global gana o empata en los 5 |
| Exceso de MANTENER | No se analiza | Explicado (voto dividido + régimen del VIX) y ajustado |
| Ventana de las redes | No se menciona | Detectado que termina en *t − 1*; efecto medido (≈ 0.007) ([A5 §7](../A_modelo/A5_REDES_NEURONALES.md#7-una-asimetría-que-hay-que-conocer-la-ventana-termina-un-día-antes)) |
| Plataforma | No forma parte del paper | Desplegada, con la misma metodología |

## 5. Qué se mantuvo

- El problema: señal diaria de 3 clases para las 7 acciones.
- La etiqueta 30/70 a un día con ventana de 252 días.
- Las 61 variables base.
- Los 5 modelos y los 3 experimentos.
- F1-macro como métrica principal y las métricas económicas.
- **La conclusión:** los clásicos bien regularizados igualan o superan a las
  redes en este régimen, y la LR es el mejor punto de partida.

## 6. ¿Hay contradicciones entre el paper y el TT?

No en la conclusión, pero hay matices que conviene conocer:

| Matiz | Cómo explicarlo |
|---|---|
| El paper describe la LSTM como **bidireccional** | Es correcto para la Etapa 3 (§7). La LSTM ganadora de Optuna en la Etapa 4 resultó **unidireccional** |
| El paper dice que la búsqueda en varios años es trabajo futuro | La prueba año por año de la Etapa 4 ya existía en el repositorio pero no se citó; en el TT ya está analizado |
| Las cifras del TT en 2026 son más bajas que las del paper | 2025 fue el mejor año del modelo; el paper lo dice como limitación ("un solo periodo no separa el efecto del modelo del régimen del año") |
| La "mejora" de las interacciones (+0.023) | No está en el paper; en el TT se aclara que solo existe en 2025 y que en validación empatan |

## 7. Cómo usar el paper en la defensa

- **Como respaldo:** la metodología y la conclusión principal pasaron
  revisión por pares en un congreso internacional indexado.
- **Como punto de partida:** "el paper publica la comparación; el TT además
  evalúa en seis años y en 2026, analiza el comportamiento del modelo y lo
  despliega en una plataforma".
- **No lo presentes como el TT completo**, ni defiendas cifras del paper
  que el TT ya matizó (por ejemplo, decir que la LR siempre gana: en el
  prueba año por año empata con XGBoost).

---

## Preguntas de este tema

Están desarrolladas en [D7](../D_defensa/D7_PREGUNTAS_PAPER.md).
