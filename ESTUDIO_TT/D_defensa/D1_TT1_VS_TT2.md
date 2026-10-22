# D1 — Del reporte de TT1 a lo que se entrega en TT2

> **Para qué sirve.** El reporte de TT1 (`TT-Fin/TT1 (1.pdf`, 102 páginas,
> 18 de mayo de 2026) es lo que los sinodales ya revisaron. Mucho cambió
> después: el protocolo, la conclusión (en TT1 ganaba XGBoost; ahora la
> Regresión Logística), la estrategia (por acción → global), la base de
> datos (PostgreSQL → SQLite) y la arquitectura del sistema. Aquí está cada
> cambio con la sección del TT1 donde aparecía y **por qué** se hizo.
>
> **Regla para responder:** el TT1 dejó preguntas abiertas y trabajo
> futuro (su §5.6, §5.9 y §5.10); TT2 los resolvió. Casi todos los cambios
> hicieron el trabajo **más riguroso**, y el más importante —dar las mismas
> variables a todos los modelos— responde justo la duda que el propio TT1
> planteó.

---

## 1. Lo que el TT1 concluyó y lo que se sabe ahora

| Tema | TT1 (mayo) | TT2 (ahora) |
|---|---|---|
| Mejor modelo en F1 | **XGBoost** (0.369 promedio, por acción) | **Regresión Logística** (0.404 en 2025, global, Etapa 4; significativamente mejor que los otros cuatro) |
| Mejor en dinero | LR (Sharpe promedio 0.285, Exp B por acción) | LR (Sharpe +0.89 en 2025 global; +0.62 con costos) |
| Redes | Debajo de los clásicos; LSTM la peor | Igual: debajo de los clásicos; además se midió **por qué** (no bajan del azar en validación) |
| ¿Se rechaza H₀ (el DL no es superior)? | No se rechaza | No se rechaza, ahora con pruebas de significancia |
| Explicación que dio el TT1 | "La asimetría en el número de variables explica la superioridad de los clásicos; haría falta darles a todos las mismas" (§5.6, §5.9) | **Se hizo:** desde la Etapa 3 los cinco modelos reciben las mismas 61 variables, y los clásicos siguen arriba. La asimetría no era la explicación |
| Global vs por acción | Experimento adicional; ya mostraba que el global gana en 4 de 5 modelos (Tabla 21) | El global pasó a ser la estrategia **principal** (gana o empata en los 5, con prueba pareada) |
| Aplicación web | "En desarrollo" (objetivo 4, §5.8) | Terminada, conectada al modelo real y desplegada en Render |

**Por qué cambió el ganador (XGBoost → LR).** Tres razones medibles:

1. **En TT1 cada modelo tenía distintas variables** (LR solo 3–8, XGBoost
   23–25). Con las mismas 61 para todos, la LR mejora y XGBoost no: en el
   Exp B por acción, la LR pasa de 0.355 (TT1, 4 variables) a 0.392 (Etapa 3,
   61 variables) y XGBoost se queda igual (0.371 → 0.370). A la LR le
   perjudicaba el filtro.
2. **En TT1 la estrategia principal era por acción** (~1 500 filas por
   modelo). Con el modelo global (~10 500 filas), la LR gana más (TT1 ya lo
   anticipaba: LR 0.355 → 0.391 al pasar a global; XGBoost 0.371 → 0.369).
3. **Búsqueda de hiperparámetros mucho más amplia** (Etapa 4, Optuna 150
   intentos): la LR encontró una regularización muchísimo más fuerte
   (C = 0.000165) que la cuadrícula del TT1.

**Y aun así hay que matizar:** en la prueba año por año de 6 años, LR (0.350) y
XGBoost (0.356) empatan. Lo que se sostiene en TT1 y en TT2 es lo mismo:
**los clásicos igualan o superan a las redes**.

---

## 2. Objetivos, pregunta e hipótesis

| TT1 | Estado en TT2 |
|---|---|
| **Objetivo general** (§1.2.1): implementar y entrenar modelos que recomienden comprar, vender o mantener, evaluarlos contra modelos de referencia con simulación económica e integrarlos a una **aplicación web** | Cumplido |
| **Específico 1:** analizar las arquitecturas y diseñar el pipeline de datos (variables, etiquetado multiclase, partición temporal) | Cumplido (`scripts_v1/01`, ya corregido en v4/v5) |
| **Específico 2:** implementar y optimizar los cinco modelos | Cumplido; la optimización pasó de cuadrícula a Optuna simétrico |
| **Específico 3:** evaluar y comparar con una métrica de clasificación y métricas económicas para determinar **en qué condiciones** el DL supera al ML | Cumplido: no lo supera en este régimen, y se explican las condiciones en que podría (más datos, entradas crudas, horizonte más largo) |
| (§5.8 menciona un **objetivo 4**: desarrollar la aplicación web, que en §1.2.2 no aparece) | Cumplido. *Cuidado: el TT1 tiene 3 objetivos específicos en §1.2.2 y 4 en §5.8; en el documento final conviene unificarlos* |
| **Pregunta** (§1): ¿pueden los modelos de DL ofrecer un rendimiento superior, en clasificación y economía, frente a ML en las Magnificent 7? | Respuesta: no, con datos públicos diarios y señal de un día |
| **EMH débil** como hipótesis nula implícita (§2.1.3) | Se mantiene; los resultados (κ ≈ 0.1, F1 ≈ 0.35 en 6 años) son coherentes con un mercado casi eficiente a un día |
| **Metodología CRISP-DM + SCRUM** (§3) | Se mantiene; justamente CRISP-DM permite volver a fases anteriores, que es lo que pasó etapas 1 a 6 |

---

## 3. Datos y etiqueta

| TT1 | TT2 | Por qué |
|---|---|---|
| Yahoo Finance, 7 acciones, SPY y VIX, descarga desde 2013-01-01, `auto_adjust=True` | Igual | |
| Etiqueta: percentiles 30/70 de 252 días con `shift(1)` (§2.2.2, §3.2) | **Igual** | Se probaron otros cortes y horizontes (Etapa 5) y se mantuvo |
| Interpolación lineal si faltan < 1 % de días | No hizo falta (ninguna acción tiene huecos) | |
| **Exp A: entrenamiento 2014–2021, validación 2022–2023, prueba 2024–2025** (Tabla 3, Tabla 8) | **Exp A: 2014–2023 / 2024 / 2025** | En TT1 la prueba de A incluía 2024, así que A no se podía comparar con B y C. *El propio TT1 se contradice: §3.5.1 dice que los tres comparten la prueba 2025, y la Tabla 8 dice que A prueba en 2024–2025.* Se corrigió en la Etapa 3 |
| Exp B: 2018–2023 / 2024 / 2025; Exp C: 2020–2023 / 2024 / 2025 | Igual | |
| Solo un año de prueba (2025) | Además: **prueba año por año 2020–2025** y **2026 en vivo** | El TT1 ya lo reconocía como limitación (§5.9) |

## 4. Variables

| TT1 | TT2 | Por qué |
|---|---|---|
| El texto dice **54 características** (§3.2, §3.3, resumen) | **61** | La Tabla 4 del propio TT1 lista 61 (5+4+9+8+9+8+7+5+6). El "54" del texto es un error de conteo; el código siempre calculó 61. *Corregir en el documento final* |
| §3.3.3 dice "ocho" características de medias móviles | Son 9 (5 distancias, 3 cruces, 1 pendiente) | Mismo error de conteo |
| **Selección de variables por modelo** (§3.4): LR con Pearson + VIF (8 / 4 / 3 variables en A / B / C); XGBoost con SHAP (24 / 23 / 25); LSTM con Spearman (25 / 10 / 3); CNN-LSTM igual que LSTM + 5 canales OHLCV; consenso en ≥ 3 de 7 acciones | **Las mismas 61 variables para los cinco modelos** | Se comparó cada modelo con y sin su filtro: **usar las 61 es mejor en 11 de 15 casos** (resultado publicado en el paper). Además, el TT1 mismo identificó que la diferencia de variables impedía comparar arquitecturas (§5.6) |
| CNN-LSTM y CNN 1D con **5 canales OHLCV normalizados localmente** por ventana (§3.6.4, Tabla 9) | v4/v5: las redes reciben solo las 61 variables | Igualar la entrada de los cinco modelos. *Ojo: el paper todavía describe esos canales (§4), pero el código de la Etapa 3 (`train_all_v4.py`) no los usa* |
| 15 interacciones | Agregadas en la Etapa 5 (producción) | |

## 5. Preparación y escalado

| TT1 | TT2 | Por qué |
|---|---|---|
| StandardScaler para LR, sin escalado para XGBoost, MinMaxScaler para las redes (§3.6) | Etapa 3 igual; **Etapa 4: Optuna eligió RobustScaler** para LR y redes; producción RobustScaler | Los retornos tienen colas pesadas; la mediana y el rango intercuartílico no se distorsionan |
| Las ventanas descartan las primeras W−1 observaciones de cada segmento (§2.3.3) | Etapa 4: ventanas sobre la serie continua, asignadas por la fecha de la etiqueta | Así los cinco modelos se evalúan sobre las mismas 1 736 filas; sin fuga porque la ventana solo mira atrás y el escalador se ajusta con entrenamiento |
| §3.7.1: `X[i] = features[i : i+lookback]`, `y[i] = target[i+lookback]` ("días estrictamente anteriores al día cuya etiqueta se predice") | Igual en v4/v5 | **Consecuencia que el TT1 no notó:** la etiqueta del día *t* es el movimiento *t → t+1*, así que las redes no ven las variables del día *t* y la LR sí. Medido: cuesta ≈ 0.007 de F1. Ver [A5 §7](../A_modelo/A5_REDES_NEURONALES.md#7-una-asimetría-que-hay-que-conocer-la-ventana-termina-un-día-antes) |

## 6. Modelos

| Modelo | TT1 | TT2 |
|---|---|---|
| **LR** | One-vs-rest, L2, lbfgs, `max_iter` 2 000, C en {0.001, 0.01, 0.1, 1, 10, 100}, `class_weight="balanced"` (§3.8.1) | Multinomial (softmax), Etapa 3 elasticnet con C ∈ {0.01, 0.1, 1}; **Etapa 4 Optuna: L2, C = 0.000165, RobustScaler**; producción + interacciones + peso MANTENER × 0.90 |
| **XGBoost** | Cuadrícula: árboles {100…500}, profundidad {3, 4, 6}, tasa {0.01, 0.05, 0.1}, submuestreo {0.6, 0.8, 1}; `scale_pos_weight` (§3.8.2) | Etapa 3 Optuna 20–40 intentos; **Etapa 4 Optuna 150 intentos** (485 árboles, profundidad 9…), pesos balanceados por muestra |
| **LSTM** | **Unidireccional**, 2 capas × 128, dropout 0.3, LayerNorm, Linear(128, 3), Adam 10⁻³, weight decay 10⁻⁴, lote 64, 80 épocas, paciencia 15 sobre pérdida de validación (§3.8.3) | Etapa 3: **bidireccional** 2 × 128 (lote 128, AdamW); Etapa 4 Optuna: unidireccional 2 × 118 con atención, focal loss |
| **CNN-LSTM** | Conv1D 64 → 128 (k = 3, BatchNorm, ReLU, dropout 0.2) → LSTM 2 × 128 → LayerNorm → Linear(128, 3) + 5 canales OHLCV (§3.8.4) | Etapa 3: igual pero sin canales OHLCV; Etapa 4 Optuna: Conv 77 → 154 (k = 7) → LSTM 1 × 136 |
| **CNN 1D** | **Diseñada como ablación de la CNN-LSTM**: mismo bloque convolucional y misma entrada, pero promedio global + Linear(128, 64) + LayerNorm + Linear(64, 3), para medir el aporte del bloque recurrente (§3.8.5) | Etapa 3: 3 bloques 64 → 128 → 192 con promedio + máximo global; Etapa 4 Optuna: 2 bloques 50 → 100 (k = 7) |
| **Hiperparámetros de redes** | **Fijos a priori** "por costo computacional" (§3.10.1) | **Optuna con 17–20 hiperparámetros** (Etapa 4). El diagnóstico mostró que cada entrenamiento tarda 7–12 s: el costo no era la restricción. El TT1 ya lo proponía como trabajo futuro (§5.10) |
| **Línea base ingenua** | Clase mayoritaria y aleatoria estratificada (§3.8.6) | Se reportan como referencia: siempre MANTENER ≈ 0.20, azar ≈ 0.33 |
| Estrategia principal | **Un modelo por acción** (35 modelos por experimento); el global como experimento adicional | **Modelo global**; por acción como comparación |

**Ojo con contradicciones internas del TT1 para no repetirlas:**
- §3.10.2 dice paro temprano por **F1** con paciencia 10 y 100 épocas;
  §3.8.3 dice por **pérdida** con paciencia 15 y 80 épocas. El código de la Etapa 3
  usaba la pérdida (y por eso restauraba la época 1–2; ver diagnóstico).
- §3.10.1 dice que el lookback se eligió con validación; §5.2 dice que se
  reportó el que dio mejor F1 **en la prueba**. Lo segundo es lo que pasó;
  el paper lo transparentó y Etapa 4 lo corrigió.
- §3.8.1 dice que las métricas se calculan "sobre los primeros 90 días del
  conjunto de prueba"; los resultados son sobre todo 2025.

## 7. Evaluación

| TT1 | TT2 | Por qué |
|---|---|---|
| F1-macro (principal), F1 por clase, F1 ponderado, accuracy, matriz de confusión | Igual + **kappa de Cohen**, AUC-ROC y balanced accuracy (calculados) | Kappa es comparable entre etiquetas distintas |
| Win rate, retorno acumulado, Sharpe, drawdown, profit factor, Calmar | Igual (sin Calmar en las tablas principales) | |
| Sin costos ni deslizamiento (limitación, §3.11.4) | **Costos de 5 y 10 pb calculados** | |
| Sin pruebas de significancia | **Bootstrap por bloques, permutación, prueba de signo y Wilcoxon** | Para saber si las diferencias son reales |
| Criterio: "superior si su F1 es consistentemente mayor en los 7 activos" (§3.9.4) | Además intervalos de confianza y 6 años de prueba año por año | |
| Análisis por subperiodos = comparar A, B y C (§5.5) | Prueba año por año (cada año 2020–2025 por separado) | Los tres experimentos comparten la prueba; no son subperiodos distintos |

## 8. Resultados del TT1 (para que sepas de dónde vienen)

Todo con modelos por acción y el lookback elegido con la prueba:

| Modelo | F1 promedio (A, B, C) | Mín. | Máx. | Sharpe promedio Exp B |
|---|---:|---:|---:|---:|
| XGBoost | 0.369 | 0.304 | 0.424 | 0.270 |
| LR | 0.351 | 0.253 | 0.425 | 0.285 |
| CNN-LSTM | 0.340 | 0.207 | 0.418 | −0.430 |
| CNN 1D | 0.331 | 0.264 | 0.387 | −0.980 |
| LSTM | 0.291 | 0.124 | 0.370 | −0.400 |

Global contra por acción (Exp B, Tabla 21): LR 0.355 → 0.391, LSTM 0.288 →
0.335, CNN-LSTM 0.323 → 0.357, CNN 0.306 → 0.342, XGBoost 0.371 → 0.369.

El caso "CNN 1D en META, Exp C, Sharpe 3.64" del TT1 es un resultado
aislado (una acción, un experimento, el mejor de 105 combinaciones): no es
evidencia de superioridad, como el propio TT1 dice.

## 9. Sistema

| Componente | TT1 (§4) | TT2 | Por qué |
|---|---|---|---|
| Arquitectura | 6 capas: fuentes, pipeline ETL, modelos, base de datos, API, frontend | Las mismas responsabilidades, pero el ETL vive **dentro de la API** (programador APScheduler) | Un solo servicio que desplegar; el ETL ya no escribe por un proceso aparte |
| Pipeline diario | ETL **incremental**: solo el día en curso, 7 pasos, ~3–5 min, cron de Linux, métricas semanales (lunes) y mensuales (fin de mes), snapshot de 90 días | **Recalcula toda la ventana de ~3 años** en cada actualización (segundos), métricas en ventanas móviles de 30/60/90 días | Recalcular garantiza que todo sale del modelo vigente (si se reentrena, la historia se actualiza) y elimina estados intermedios; es barato |
| Horario | 16:30 EST con cron | 16:30 hora de Nueva York con APScheduler (maneja horario de verano) + reintentos cada 2 min | |
| Base de datos | **PostgreSQL**, 9 tablas en 3FN + 1 desnormalizada (`snapshots_90d`), JSONB para la matriz de confusión, `ON DELETE RESTRICT` | **SQLite**, 4 tablas (`assets`, `ohlcv_daily`, `predictions`, `metrics`), compatible con PostgreSQL | Ver [B3 §4](../B_sistema/B3_BASE_DE_DATOS.md#4-por-qué-sqlite-y-no-postgresql-como-decía-el-tt1). Resumen: las razones del TT1 para PostgreSQL (dos procesos escribiendo, JSONB) dejaron de aplicar |
| Tabla de variables | `features_daily` con 46 variables | No existe | Las 76 variables se recalculan en menos de un segundo |
| API | Flask, 6–7 GET + 5 POST internos para que el ETL cargara datos; puerto 5000 | Flask, 9 GET + `POST /admin/refresh`; los 5 POST de carga quedaron **desactivados (403)** | El ETL ya no necesita la API para escribir (está en el mismo proceso); dejarlos abiertos permitiría escribir datos que no son del modelo |
| Rutas | `/api/summary`, `/api/signals`, `/api/equity/{ticker}`, `/api/metrics/{ticker}` (diagrama de secuencia) y `/stocks…` (Tabla 13) | `/stocks…`, `/metrics`, `/model`, `/market-status`, `/health` | *El TT1 mezcla dos juegos de rutas; las vigentes son las de [B2](../B_sistema/B2_API.md)* |
| Frontend | React + TypeScript + Recharts, 3 niveles (panel general, tarjetas, detalle expandible con curva de capital, historial de 30 días, matriz de confusión y gráfica de pastel), consulta a la API **cada hora**, puerto 3000 | React + TypeScript + Vite + Tailwind + Recharts, 5 pantallas (Hoy, detalle, Resultados, Ayuda con guía y glosario, Acerca de), con la **curva de capital** («¿Qué habría pasado con $1,000?») y la seguridad en palabras | Se priorizó que un usuario sin contexto entienda cada recomendación y su resultado. **No se implementaron** la matriz de confusión, la gráfica de pastel ni la consulta automática cada hora: la página pide los datos al abrirse, y como el dato cambia una vez al día no hace falta |
| Requerimientos no funcionales | Carga < 2 s, navegadores modernos, diseño responsivo | Cumplidos (diseño responsivo); en el plan gratuito de Render la primera carga tras dormir tarda 20–40 s | |
| Casos de uso | CU-01 consultar señales, CU-02 detalle de activo, CU-03 comparar rendimiento | Cubiertos por Home, StockDetail y Performance | |
| Despliegue | Local (3 puertos); desplegar era trabajo futuro (§5.10) | **Render** (Docker + sitio estático), despliegue automático | |
| Modelo integrado | "Pendiente de la selección definitiva" (§4.5.3) | LR en producción (`LR-v8-interactions-holdw090`) | |

## 10. Entorno

| TT1 (§5.1) | TT2 |
|---|---|
| Ryzen 5 7600, RTX 5060 Ti, 32 GB, WSL2 | Mismo equipo |
| Python 3.12.3, scikit-learn 1.8.0, PyTorch 2.11, yfinance 1.2.0 | Python 3.13, **scikit-learn 1.7.2**, PyTorch 2.12, XGBoost 3.2, Optuna 4.8 (versiones documentadas en el suplementario del paper; producción fija scikit-learn 1.7.2) |
| Ocho scripts secuenciales (01–08) | `scripts_v1/` (vigente solo el 01) + `scripts_opt/` (etapas 3–5 y análisis) |

## 11. El trabajo futuro del TT1 y qué se hizo

| TT1 §5.10 / §5.9 | Estado |
|---|---|
| Ajustar el dataset (ventanas de entrenamiento, limpieza) | Hecho: Etapa 2, Etapa 4, Etapa 5 |
| Integrar ETL, modelos y aplicación | Hecho |
| Desplegar en producción | Hecho (Render) |
| Búsqueda sistemática de hiperparámetros (grid o bayesiana) | Hecho (Optuna, Etapa 4) |
| Experimento con las mismas variables para todos | Hecho (desde la Etapa 3) |
| Costos de transacción | Calculados (Etapa 4) |
| Periodos de prueba distintos | Prueba año por año y 2026 |
| Sentimiento, macroeconomía | Sigue como trabajo futuro |

---

**Frase para cerrar si insisten:** "El TT1 dejó explícitas sus
limitaciones: variables distintas por modelo, hiperparámetros fijos en las
redes, un solo año de prueba y la aplicación sin terminar. En TT2
resolvimos cada una, y la conclusión de fondo —los clásicos igualan o
superan a las redes con estos datos— se mantuvo, ahora con pruebas
estadísticas."
