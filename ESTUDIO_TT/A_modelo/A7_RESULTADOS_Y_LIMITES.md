# A7 — Resultados y límites

> **Resumen.** En la prueba principal (2025, protocolo de la Etapa 4) la LR gana con
> significancia: F1 0.404, Sharpe +0.89. En seis años de prueba año por año la LR
> y XGBoost empatan apenas arriba del azar (~0.35) y las redes quedan abajo.
> En 2026, fuera de muestra, el modelo en producción da F1 0.354. La señal
> existe pero es débil e inestable entre años; la conclusión que se sostiene
> en todas las pruebas es comparativa: en este régimen, un modelo lineal bien
> regularizado iguala o supera a las redes profundas.

---

## 1. La tabla que hay que saberse

| Qué | Cifra | Fuente |
|---|---|---|
| LR, 2025, Etapa 4, Exp B global | **F1 0.404**, IC 95 % [0.379, 0.428], **Sharpe +0.89** | `RESULTADOS_OPTIMIZADOS/v5/resultados_finales.csv` |
| Los otros cuatro, 2025, Etapa 4 | CNN-LSTM 0.372, LSTM 0.369, XGBoost 0.359, CNN 0.359 | ídem |
| LR, promedio de A/B/C, Etapa 3 (paper §7) | F1 0.399, Sharpe B +0.76 | `v4/resultados_v4.csv` |
| Prueba año por año 2020–2025, F1 medio | XGBoost 0.356, LR 0.350, CNN-LSTM 0.328, LSTM 0.314, CNN 0.292 | `analisis_hold/5_walk_forward_v5_resumen.csv` |
| Máximo de cualquier modelo en cualquier año de la prueba año por año | 0.394 (LR, 2025) | ídem |
| Con costos de 10 pb (2025) | LR Sharpe +0.62; XGBoost +0.01 | `v5/resultados_finales.csv` |
| Global contra por acción (LR, 21 pares) | Global gana 18/21, p = 0.002 | `analisis_hold/4a_global_vs_porticker_por_modelo.csv` |
| Producción en 2026 (ene–sep) | **F1 0.354, κ 0.035, Sharpe +0.29**, MANTENER 40 % (real 35 %) | `analisis_hold/8_confirmacion_2026.csv` |
| Modelo anterior en 2026 | F1 0.313, κ 0.010, MANTENER 60 % | ídem |
| Azar / siempre MANTENER | F1 ≈ 0.33 / ≈ 0.20 | |

### Otras métricas del mismo ranking (Etapa 4, Exp B global, 2025)

Calculadas el 2026-10-12 con las probabilidades guardadas en
`RESULTADOS_OPTIMIZADOS/v5/preds/`. La LR es la mejor en todas:

| Modelo | F1-macro | AUC-ROC (macro, uno contra todos) | Balanced accuracy | Kappa |
|---|---:|---:|---:|---:|
| **LR** | **0.404** | **0.593** | **0.407** | **0.120** |
| CNN-LSTM | 0.372 | 0.573 | 0.373 | 0.068 |
| LSTM | 0.369 | 0.551 | 0.373 | 0.065 |
| CNN 1D | 0.359 | 0.568 | 0.369 | 0.060 |
| XGBoost | 0.359 | 0.539 | 0.364 | 0.046 |

*AUC-ROC*: probabilidad de que el modelo dé más probabilidad de una clase a
un ejemplo de esa clase que a uno de otra (0.5 = azar). *Balanced
accuracy*: promedio del recall de las tres clases (0.33 = azar).

---

## 2. Cómo leer el resultado de 2025

### 2.1 Clasificación

Matriz de confusión del LR + interacciones en 2025 (filas = realidad):

| | dijo VENDER | dijo MANTENER | dijo COMPRAR |
|---|---:|---:|---:|
| **era VENDER** | 172 | 262 | 79 |
| **era MANTENER** | 154 | 493 | 79 |
| **era COMPRAR** | 140 | 231 | 119 |

- Acierta bien MANTENER (493 de 726).
- Cuando dice COMPRAR o VENDER acierta más que el azar, pero se confunde
  mucho entre las dos direcciones (140 COMPRAR que dijo VENDER).
- Exactitud 45 %, kappa 0.14: **acuerdo leve sobre el azar**.

### 2.2 Dinero (sin costos)

- La LR de la Etapa 4 (sin interacciones) en 2025: Sharpe +0.89, win rate 52 %, profit factor 1.27, máximo
  drawdown −45 %.
- Gran parte de la ganancia viene de **no operar** en días de poco
  movimiento: los días MANTENER tienen movimientos ~40 % menores (|r| medio
  1.31 % contra 2.2–2.3 %).
- Con LR + interacciones, forzar COMPRAR/VENDER todos los días (sin MANTENER) da Sharpe parecido en
  2025 (+0.89 contra +0.92) pero un drawdown peor (−61 % contra −52 %), y en
  2024 pierde más.

### 2.3 Por qué 2025 se ve mejor que el resto

2025 fue el **mejor año** del modelo en la prueba año por año. En 2025 se cumplía
la regla "VIX bajo → movimientos pequeños" que el modelo aprendió (MANTENER
real 55 % con VIX bajo contra 28 % con VIX alto). En 2026 esa regla dejó de
cumplirse (MANTENER real ≈ 35 % en todos los niveles del VIX).

**El año de prueba no se eligió a conveniencia:** se fijó en la Etapa 3 como el
último año completo, antes de conocer los resultados, para que los tres
experimentos lo compartieran. Por eso se reportan también la prueba año por año y
2026.

---

## 3. Prueba año por año 2020–2025 (la evidencia más amplia)

| Año de prueba | LR | XGBoost | LSTM | CNN | CNN-LSTM | Mejor |
|---|---:|---:|---:|---:|---:|---|
| 2020 | 0.343 | **0.387** | 0.292 | 0.279 | 0.320 | XGBoost |
| 2021 | **0.388** | 0.358 | 0.264 | 0.257 | 0.274 | LR |
| 2022 | 0.314 | 0.347 | **0.366** | 0.314 | 0.351 | LSTM |
| 2023 | **0.335** | 0.330 | 0.312 | 0.316 | 0.319 | LR |
| 2024 | 0.325 | 0.356 | 0.363 | 0.359 | **0.376** | CNN-LSTM |
| 2025 | **0.394** | 0.359 | 0.284 | 0.227 | — | LR |
| **Media** | 0.350 | **0.356** | 0.314 | 0.292 | 0.328 | |
| Sharpe medio | **+0.22** | **+0.22** | −0.48 | −0.29 | −0.25 | |

(CNN-LSTM de 2025 no quedó en el registro de la prueba año por año.)

**Qué dice:**

1. El ranking cambia de año a año: cada modelo "gana" algún año.
2. En promedio, LR y XGBoost empatan y son los únicos con Sharpe medio
   positivo.
3. Las tres redes quedan abajo en promedio y con Sharpe negativo.
4. **Ningún modelo pasa de 0.394 en ningún año.** Eso es el techo práctico
   con estos datos.

---

### 3.1 La misma prueba con ajustes fijos de antemano (más limpia)

Los ajustes de la tabla anterior se eligieron con 2024, así que para los
pliegues 2020–2023 son información posterior. Con los ajustes fijos de la
Etapa 3 (que no vieron ningún pliegue) la comparación es limpia
(`v5/walkforward_v4.csv`):

| Modelo | F1 promedio | Lugar promedio | Años ganados | Sharpe 10 pb |
|---|---:|---:|---:|---:|
| **LR** | **0.360** | **1.83** | **3** | **+0.09** |
| XGBoost | 0.356 | 2.67 | 1 | −0.10 |
| CNN 1D | 0.338 | 3.00 | 2 | −0.02 |
| LSTM | 0.331 | 3.67 | 0 | −0.50 |
| CNN-LSTM | 0.326 | 3.83 | 0 | −0.63 |

Juntando los seis años: LR − XGBoost +0.003 (no significativa); LR − cada
red +0.017 a +0.026 (significativas).

### 3.2 Prueba ciega 2026 de los cinco

Ajustes congelados de la Etapa 4, entrenamiento 2020–2024, validación 2025,
prueba del 2 de enero al 22 de octubre de 2026: LR 0.346, XGBoost 0.343,
LSTM 0.331, CNN-LSTM 0.318, CNN 1D 0.304 de F1. Solo la diferencia contra la
CNN 1D es significativa. En Sharpe, la CNN 1D (+0.88) y la LSTM (+0.72)
superan a la LR (+0.38). Detalle y lectura en
[D9](../D_defensa/D9_OBSERVACIONES_SINODAL.md).

## 4. El exceso de MANTENER y su ajuste

### 4.1 El síntoma

| Periodo | MANTENER real | MANTENER predicho (modelo "balanced") |
|---|---:|---:|
| Validación 2024 | 39.5 % | 64.4 % |
| Prueba 2025 | 42.0 % | 57.0 % |
| 2026 (ene–sep) | 34.7 % | 59.5 % |
| 17 ago – 28 sep 2026 | 38.1 % | 94.8 % |

### 4.2 La causa: voto dividido

En el **100 %** de los días que el modelo dice MANTENER, se cumple
`P(COMPRAR) + P(VENDER) > P(MANTENER)`. Un día típico: VENDER 0.32,
MANTENER 0.38, COMPRAR 0.30. El modelo cree que lo más probable es un
movimiento fuerte (0.62), pero no sabe hacia dónde; esa probabilidad se
reparte y ninguna dirección supera a MANTENER.

**Por qué pasa:** la *magnitud* del movimiento es algo predecible (la
volatilidad se agrupa en el tiempo; es lo que modelan ARCH/GARCH), pero la
*dirección* casi no (eficiencia débil del mercado). El modelo aprende bien
"habrá movimiento / no habrá", y mal "sube / baja".

**Por qué en bloque:** las variables con más peso son del VIX y del S&P 500,
iguales para las 7 acciones. Con VIX bajo su media, el modelo dice MANTENER
a casi todo (92 % en el quintil más bajo del VIX en 2025).

**No es desbalance de clases:** ya se entrena con pesos "balanced", que le
bajan el peso a MANTENER. Y con la etiqueta 40/60 (MANTENER real 20 %) el
modelo sigue diciendo MANTENER el 53 % de los días.

### 4.3 Qué se probó para corregirlo (sin cambiar la etiqueta)

Elegido **solo con 2019–2024** por origen rodante; 2025 y 2026 solo
confirman:

| Alternativa | F1 2019–24 | κ | Sharpe | MANTENER predicho |
|---|---:|---:|---:|---:|
| "Balanced" (modelo anterior) | 0.357 | 0.063 | +0.52 | 47 % |
| Multiplicar P(MANTENER) × 0.90 al decidir | 0.334 | 0.050 | +0.37 | 23 % |
| Proporción móvil causal (252 días) | 0.367 | 0.070 | +0.51 | 41 % |
| Reentrenar con peso MANTENER × 0.95 | 0.360 | 0.062 | +0.53 | 42 % |
| **Reentrenar con peso MANTENER × 0.90** | **0.365** | **0.068** | **+0.54** | **36 %** |
| Reentrenar con peso × 0.85 | 0.360 | 0.062 | +0.46 | 30 % |
| Reentrenar con peso × 0.80 | 0.352 | 0.061 | +0.41 | 24 % |

(MANTENER real promedio 2019–2024: 40 %.)

- **Un factor fijo sobre la probabilidad empeora**, porque el sesgo cambia
  de signo entre años (2022: predice 13 % contra 32 % real; 2023: 74 %
  contra 48 %). Un primer análisis que solo miraba 2024 sugería ese factor:
  era sobreajuste a un año.
- **Entre los pesos de reentrenamiento, × 0.90 es el mejor en F1, kappa y
  Sharpe a la vez**, así que la elección no depende de qué métrica se
  prefiera. La proporción móvil de 252 días empata en F1 y kappa (0.367 y
  0.070 contra 0.365 y 0.068), pero da menos Sharpe en 2019–2024 (+0.51
  contra +0.54), en 2025 (+0.81 contra +0.93) y en 2026 (+0.16 contra +0.29).
- Diferencia con el umbral: el peso entra en la pérdida del entrenamiento,
  así que el modelo reajusta interceptos **y** coeficientes; no es solo
  correr un umbral.

### 4.4 Confirmación en 2026 (nadie lo usó para decidir)

| Modelo | F1 | κ | MANTENER (real 34.7 %) | Sharpe | Sharpe portafolio |
|---|---:|---:|---:|---:|---:|
| Balanced (anterior) | 0.313 | 0.010 | 59.7 % | +0.38 | +0.71 |
| Proporción móvil causal | 0.350 | 0.027 | 37.0 % | +0.16 | +0.33 |
| **Peso × 0.90 (actual)** | **0.354** | **0.035** | **39.7 %** | +0.29 | +0.60 |

Comprar y mantener las 7 en el mismo periodo: Sharpe de portafolio +0.49.

**Lectura honesta:** no es una mejora estadísticamente significativa
(mejora el F1 en 4 de 6 años; Wilcoxon p = 0.31). Es un modelo
**equivalente** con una proporción de MANTENER realista, que era el
objetivo. En 2025 se pasa al otro lado (29 % predicho contra 42 % real).

---

## 5. Global contra un modelo por acción

Comparación pareada: el modelo global y el de cada acción evaluados en
**exactamente los mismos días** de esa acción. 21 pares por modelo (3
experimentos × 7 acciones), Etapa 4, 2025:

| Modelo | F1 global | F1 por acción | Pares que gana el global | p (signo) |
|---|---:|---:|---:|---:|
| **LR** | **0.394** | 0.375 | **18/21** | **0.002** |
| XGBoost | 0.359 | 0.364 | 10/21 | 1.00 |
| LSTM | 0.334 | 0.314 | 16/21 | 0.027 |
| CNN | 0.293 | 0.212 | 19/21 | <0.001 |
| CNN-LSTM | 0.305 | 0.330 | 7/21 | 0.19 |

**El global gana o empata en los cinco**; ninguno es significativamente
mejor por acción. Razones: 7 veces más datos; la etiqueta es un percentil
de cada acción (las clases significan lo mismo en las 7); las variables son
razones, comparables entre acciones; y con poca señal un modelo por acción
se ajusta al ruido de esa acción. Además, un solo modelo es más simple de
mantener.

*Advertencia:* los 21 pares no son independientes (mismo año, mismo
mercado), así que los p-valores son optimistas. Lo que da confianza es que
la dirección se repite en la Etapa 3 y en la Etapa 4.

---

## 6. ¿Hay señal o es suerte?

| Evidencia | Qué dice |
|---|---|
| Permutación 2025 | Solo 0.4 % de 500 barajadas supera al modelo → hay señal |
| Permutación 2024 | 79 % de las barajadas supera al modelo → ese año no hubo |
| IC bootstrap 2025 | LR [0.379, 0.428]: no incluye el azar (0.33) |
| Kappa | 0.14 en 2025, ≈ 0.01–0.035 en 2026: leve |
| Prueba año por año | ≈ 0.35 de media, apenas arriba del azar |

**Conclusión:** hay una señal pequeña que aparece en algunos años y en
otros no.

---

## 7. ¿Por qué decimos que se llegó al límite?

(Argumento completo: `RESULTADOS_OPTIMIZADOS/JUSTIFICACION_LIMITE_DEL_MODELO.md`.)

1. **Techo bajo:** en seis años ningún modelo pasa de 0.394.
2. **Cinco arquitecturas muy distintas convergen** a la misma franja
   (0.29–0.36 de media). Si hubiera más información aprovechable, alguna la
   habría encontrado.
3. **≈ 30 técnicas probadas** en siete iteraciones; las que "mejoran" lo
   hacen en 0.01–0.03, mientras que el mismo modelo varía 0.08 entre años.
4. **Las redes no bajan del azar** en su pérdida de validación con ninguna
   configuración.
5. **Lo único que sube claramente el desempeño es cambiar el problema**
   (horizonte de 5–7 días: F1 ~0.43) o agregar datos externos (noticias,
   macro, opciones), ambos fuera del alcance.

---

## 8. Limitaciones (dilas antes de que te las digan)

| Limitación | Qué se hizo al respecto |
|---|---|
| El paper evalúa un solo año de prueba | Prueba año por año de 6 años y evaluación 2026 |
| 7 acciones de un sector, sobrevivientes | Se reconoce; ampliar es trabajo futuro |
| Backtest simplificado (1 día, tamaño fijo, sin deslizamiento) | Costos calculados en la Etapa 4 (5 y 10 pb) |
| Probar muchas variantes sobre 2025 (*data snooping*) | Decisiones en validación / origen rodante; se aclara que las interacciones no están validadas |
| Sharpe de un año con error estándar ≈ 1 | Las conclusiones son comparativas; métrica principal de clasificación |
| Búsqueda simétrica en procedimiento, no en dimensión | Se afirma solo "una búsqueda realista no cambia el orden" |
| La ventana de las redes termina en *t − 1* | Medido: efecto ≈ 0.007 en la LR; no cambia la conclusión ([A5 §7](A5_REDES_NEURONALES.md#7-una-asimetría-que-hay-que-conocer-la-ventana-termina-un-día-antes)) |
| Producción usa un escalador global y la investigación uno por acción | Medido: 0.4125 contra 0.4086, despreciable |
| Purga de un día en los cortes | 1 de ~250 días; despreciable |

---

## 9. Trabajo futuro (en orden de valor esperado)

1. Llevar la prueba año por año y los costos al cuerpo de la evaluación (ya
   están calculados).
2. Horizonte de 5 días (ya medido: F1 ≈ 0.43), cambiando el problema de
   forma explícita.
3. Más acciones (por ejemplo, el S&P 500 histórico, con empresas que
   desaparecieron) para que las redes tengan datos suficientes.
4. Datos gratuitos adicionales: macroeconomía de FRED; sentimiento de
   noticias con FinBERT.
5. Tamaño de posición dinámico (por volatilidad) y optimizar con costos.
6. Corregir la ventana de las redes a `[t − lookback + 1, t]` y repetir la Etapa 4.

---

## Preguntas de este tema

Están desarrolladas en [D5](../D_defensa/D5_PREGUNTAS_ESTADISTICA.md) y
[D8](../D_defensa/D8_PREGUNTAS_TRAMPA.md).
