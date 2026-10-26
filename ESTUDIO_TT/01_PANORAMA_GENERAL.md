# 01 — Panorama general del Trabajo Terminal

> **Lee esto primero.** Es la historia completa del TT en un solo documento:
> qué problema atacamos, qué construimos, qué resultó, qué decidimos y por
> qué. Los demás documentos profundizan cada parte.
>
> TT 2026-B164, ESCOM-IPN. Desarrolladores: Reyes Ramos David y Polvo
> Cuatianquiz Jesús Baruc. Directores: Abdiel Reyes Vera y Emmanuel Juárez
> Carbajal.

---

## 1. El TT en tres frases

1. **Comparamos cinco modelos** de aprendizaje automático (Regresión
   Logística, XGBoost, LSTM, CNN 1D y CNN-LSTM) para decidir cada día si
   conviene **COMPRAR, MANTENER o VENDER** cada una de 7 acciones
   tecnológicas de EE. UU., usando solo datos gratuitos de Yahoo Finance.
2. **Ganó el modelo más simple**, la Regresión Logística, y demostramos con
   varias pruebas que no es casualidad del año evaluado ni falta de
   ajuste de las redes: con estos datos, la señal que se puede extraer es
   débil y los modelos complejos aprenden ruido.
3. **Construimos una plataforma web** (API + aplicación web) que
   descarga los datos reales cada día, corre el modelo ganador y muestra las
   señales y qué tan bien le ha ido, con la misma metodología de la tesis.

Además, una parte del trabajo se publicó como **paper en MICAI 2026**
(Springer, LNAI), que es un producto extra.

---

## 2. El problema

### 2.1 Qué se predice

Cada día de mercado *t*, al cierre, para cada una de las 7 acciones (AAPL,
NVDA, TSLA, AMZN, MSFT, GOOGL, META), el modelo dice qué hacer para el día
siguiente:

| Señal | Qué significa | Posición en la simulación |
|---|---|---|
| **COMPRAR** (BUY) | Se espera una subida fuerte | Largo (+1): ganas si sube |
| **MANTENER** (HOLD) | No hay información suficiente; no operar | Fuera (0) |
| **VENDER** (SELL) | Se espera una bajada fuerte | Corto (−1): ganas si baja |

*Posición larga* = compras la acción y ganas si sube. *Posición corta* = la
vendes prestada y ganas si baja. *Fuera* = no tienes la acción.

### 2.2 Cómo se define la respuesta correcta (la "etiqueta")

Para entrenar un modelo hay que decirle, para cada día del pasado, cuál era
la respuesta correcta. Usamos:

- **Retorno logarítmico del día siguiente:** `r = ln(C_{t+1} / C_t)`, donde
  `C_t` es el precio de cierre del día *t*. Es "cuánto se movió el precio",
  en una escala que se puede sumar día con día.
- **Percentiles móviles:** se toma el último año (252 días hábiles) de
  retornos de esa misma acción. Si el retorno de mañana está en el **30 %
  más alto** de lo visto ese año → COMPRAR. Si está en el **30 % más bajo**
  → VENDER. En medio → MANTENER.

Así, en un año tranquilo "subida fuerte" puede ser +0.8 % y en un año
agitado +3 %: la etiqueta **se adapta a la volatilidad**. Y como el umbral se
calcula solo con días anteriores, el modelo nunca "ve el futuro".
Resultado: ~30 % COMPRAR, ~40 % MANTENER, ~30 % VENDER.

Detalle completo: [A1](A_modelo/A1_DATOS_Y_ETIQUETA.md).

### 2.3 Con qué información decide el modelo

**61 variables** calculadas solo con precios y volumen diarios
(apertura, máximo, mínimo, cierre, volumen) de la acción, más el índice
S&P 500 (a través del fondo SPY) y el índice de volatilidad VIX ("índice
del miedo"). Ejemplos: retornos de 1 a 10 días, distancia a medias
móviles, RSI, MACD, volatilidad, volumen relativo, forma de la vela, día de
la semana. El modelo en producción agrega **15 interacciones** (productos de
pares de variables) → **76 variables**.

Detalle de cada una: [A2](A_modelo/A2_VARIABLES.md).

### 2.4 Restricciones que nos pusimos (y por qué)

| Restricción | Razón |
|---|---|
| Solo datos gratuitos de Yahoo Finance | Cualquiera puede reproducir el trabajo sin pagar licencias |
| Exactamente 5 modelos: 2 clásicos y 3 redes neuronales | Es la pregunta del TT: ¿el aprendizaje profundo supera a los clásicos en este problema? |
| Horizonte de 1 día | Es el planteamiento más directo de "señal diaria" y el más usado en la literatura |
| 7 acciones grandes y líquidas | Datos completos, sin huecos y sin precios distorsionados por poco volumen |

---

## 3. Lo que se hizo, en orden

### 3.1 Línea de tiempo

| Fecha (2026) | Qué pasó |
|---|---|
| Marzo | Primera versión de la aplicación (API Flask + aplicación React) con datos **simulados** |
| Hasta mayo | **Etapa 1 (= TT1)**: pipeline de 8 scripts, selección de variables distinta por modelo, modelos por acción, redes con hiperparámetros fijos |
| **18 mayo** | **Entrega del reporte de TT1** (102 páginas). Conclusión de entonces: XGBoost mejor en F1 (0.369), LR mejor en Sharpe; las redes debajo; aplicación web "en desarrollo" |
| Mayo–junio | **Etapa 2 — Primeras mejoras**: optimización por modelo, más variables, ensambles; se comprueba que filtrar variables empeora (paper §6) |
| Junio | **Etapa 3 — Comparación en igualdad**: las 61 variables para todos y el mismo año de prueba (2025) en los tres experimentos. Es la corrida que se envió al congreso (paper §7) |
| 15–16 julio | Se conecta **el modelo real** a la API, base de datos SQLite, actualización automática diaria, pruebas, Docker y despliegue en Render. Se unifican los repositorios |
| 14 agosto | **Diagnóstico de las redes**: se descubre que el protocolo de la Etapa 3 les quitaba oportunidad (época, filas, búsqueda) |
| Agosto | **Etapa 4 — Protocolo final**: protocolo corregido, búsqueda Optuna para los cinco, intervalos de confianza, costos, prueba año por año (paper §8). **Resultado principal del TT** |
| 26 agosto | **Etapa 5 — Búsqueda de mejoras**: ajustes al modelo y variables nuevas; casi nada ayuda. El modelo en producción pasa a LR + 15 interacciones. Respuesta a los revisores del paper y recorte a 12 páginas |
| 8 septiembre | Se envía la versión final (*camera-ready*) del paper a Springer |
| 30 septiembre | **Etapa 6 — Plataforma y validación**: análisis del exceso de MANTENER, comparación global vs por acción, evaluación con datos de 2026, ajuste del peso de MANTENER, auditoría completa de la plataforma |
| 2–3 octubre | Material suplementario del paper para Springer |

### 3.2 Las seis etapas (resumen)

| Etapa | Idea central | Qué se aprendió |
|---|---|---|
| Etapa 1 (TT1) | Primer pipeline: 5 modelos, 3 experimentos, por acción (principal) y global; cada modelo con sus propias variables filtradas | Funciona de punta a punta; pero los modelos no recibían las mismas variables y el experimento A probaba en otro periodo, así que no eran comparables |
| Etapa 2 | Mejorar cada modelo con los datos de TT1: optimización, más variables (181 y 94), ensambles, umbrales | Algo mejora, pero se eligió con la prueba: no se reporta. Sí deja dos lecciones: usar las 61 variables para todos y hacer un protocolo limpio |
| **Etapa 3** | **Las 61 variables para todos y el mismo año de prueba (2025) en los 3 experimentos** | **Comparación en igualdad. Es la del paper (§7)** |
| **Etapa 4** | **Protocolo corregido + Optuna para los cinco + intervalos de confianza + prueba año por año** | **LR gana con significancia en A, B y C (paper §8); en la prueba año por año LR y XGBoost empatan** |
| Etapa 5 | Ajustes al modelo (calibración, promedios de pesos, mezclas) y variables nuevas (rezagos, interacciones) | Casi nada ayuda; solo las 15 interacciones, que después empatan |
| Etapa 6 | Modelo de la plataforma: exceso de mantener, ajuste, 2026 | 2026: F1 0.354 |

Detalle: [A6](A_modelo/A6_ETAPAS_DEL_PROYECTO.md). Vista general, marcas del paper y equivalencias con los nombres viejos: [mapa de experimentos](03_MAPA_DE_EXPERIMENTOS.md).

### 3.3 El protocolo de evaluación (cómo se evita hacer trampa)

- **Separación por tiempo, nunca al azar:** entrenamiento con años
  pasados, validación con el año siguiente y prueba con el último.
  Mezclar fechas al azar dejaría que el modelo "viera el futuro".
- **Tres experimentos con el mismo año de prueba (2025)** que solo cambian
  cuántos años de entrenamiento se usan: A = 10 años (2014–2023),
  B = 6 años (2018–2023, el principal), C = 4 años (2020–2023).
- **Validación anidada en la Etapa 4:** las decisiones de configuración se toman
  con 2024; 2025 se toca **una sola vez** por configuración congelada.
- **Prueba año por año de 6 años (2020–2025):** se repite todo moviendo la
  ventana un año a la vez, para no depender de un solo año.
- **Evaluación real fuera de muestra:** el modelo final se evalúa en 2026,
  un año que ninguna decisión usó.

Detalle: [A3](A_modelo/A3_PROTOCOLO_Y_METRICAS.md).

---

## 4. Los resultados que importan

### 4.1 La comparación principal (2025, Exp B, modelo global, protocolo de la Etapa 4)

| Modelo | F1-macro | Intervalo 95 % | Sharpe (sin costos) |
|---|---:|---|---:|
| **Regresión Logística** | **0.404** | [0.379, 0.428] | **+0.89** |
| CNN-LSTM | 0.372 | [0.346, 0.395] | −0.07 |
| LSTM | 0.369 | [0.341, 0.395] | −0.35 |
| XGBoost | 0.359 | [0.334, 0.381] | +0.46 |
| CNN 1D | 0.359 | [0.332, 0.386] | −0.46 |

- **F1-macro**: qué tan bien acierta cada una de las 3 clases, promediado
  (0.33 ≈ azar, 1 = perfecto). **Sharpe**: ganancia de la estrategia
  dividida entre su variabilidad, anualizada (> 0 gana, > 1 es bueno).
- La LR es **significativamente** mejor que las otras cuatro en 2025; entre
  las otras cuatro no hay diferencia significativa.

### 4.2 Lo que dice la evaluación más amplia (y hay que decirlo)

| Prueba | Resultado |
|---|---|
| Prueba año por año 2020–2025 (6 años) | F1 medio: XGBoost 0.356, **LR 0.350**, CNN-LSTM 0.328, LSTM 0.314, CNN 0.292. Ningún modelo pasa de 0.394 en ningún año |
| Con costos de transacción (10 pb por operación) | LR Sharpe +0.62; XGBoost +0.01. La LR opera menos |
| Global vs un modelo por acción | El global gana o empata en los 5 modelos |
| Modelo en producción en 2026 (fuera de muestra) | F1 0.354, kappa 0.035, Sharpe +0.29 |

**Lectura honesta:** 2025 fue el mejor año del modelo. En seis años, LR y
XGBoost empatan apenas arriba del azar y las redes quedan abajo. La
conclusión robusta es **comparativa**: en este régimen de datos, los
modelos clásicos bien regularizados igualan o superan a las redes
profundas. Detalle y todas las cifras: [A7](A_modelo/A7_RESULTADOS_Y_LIMITES.md).

### 4.3 Por qué ganó el modelo simple (la explicación en una línea)

Con poca señal y ~10 500 ejemplos de entrenamiento, un modelo con cientos
de miles de parámetros aprende ruido; la LR con regularización muy fuerte
solo aprende lo que se repite. Además, las 61 variables ya resumen la
historia reciente (medias, RSI, momentum), así que las redes que leen
secuencias no reciben información que la LR no tenga. Se midió: la pérdida
de validación de las redes nunca baja del nivel del azar (ln 3). Detalle:
[A5](A_modelo/A5_REDES_NEURONALES.md).

### 4.4 El fenómeno de "demasiado MANTENER"

El modelo dice MANTENER más veces de las que realmente ocurre (60 % contra
35 % en 2026 con el modelo anterior). La causa: **sabe cuándo habrá
movimiento pero no hacia dónde**. Reparte la probabilidad entre COMPRAR y
VENDER, ninguna supera a MANTENER y gana MANTENER. Se corrigió entrenando
con el peso de MANTENER × 0.90 (elegido con 2019–2024): en 2026 el
MANTENER predicho bajó a 40 % (real 35 %) y el F1 subió de 0.313 a 0.354.
Detalle: [A7 §4](A_modelo/A7_RESULTADOS_Y_LIMITES.md#4-el-exceso-de-mantener-y-su-ajuste).

---

## 5. El modelo que está en producción

| Aspecto | Valor |
|---|---|
| Algoritmo | Regresión Logística multinomial (3 clases con softmax) |
| Regularización | L2, C = 0.000165 (muy fuerte) |
| Escalado | RobustScaler (mediana y rango intercuartílico) |
| Variables | 61 base + 15 interacciones = 76 |
| Pesos de clase | "balanced" con MANTENER × 0.90 → VENDER 1.103, MANTENER 0.762, COMPRAR 1.097 |
| Entrenado con | 2018–2025, las 7 acciones juntas (14 063 filas) |
| Versión | `LR-v8-interactions-holdw090` |

Se reentrenó con todos los datos disponibles porque lo que se evaluó fue el
**procedimiento**, y la prueba honesta del modelo final es 2026.

---

## 6. El sistema

```
Yahoo Finance ──► API (Flask, Python) ──► Base de datos (SQLite)
                     │  descarga datos, calcula 76 variables,
                     │  corre el modelo, evalúa contra el día siguiente
                     ▼
              Aplicación web (React) ──► usuario (navegador)
```

- **API (backend):** Flask. Al arrancar, cada día hábil a las 16:30 de Nueva
  York y cada 2 minutos si falta alguna acción, descarga ~3 años de datos,
  calcula las variables con el mismo código que el entrenamiento, corre el
  modelo, compara cada señal con lo que pasó al día siguiente y calcula las
  métricas en ventanas de 30/60/90 días. Detalle: [B2](B_sistema/B2_API.md).
- **Base de datos:** SQLite con 4 tablas (activos, precios diarios,
  predicciones, métricas). Es reconstruible desde Yahoo + el modelo, por eso
  basta una base efímera. Detalle y análisis de normalización:
  [B3](B_sistema/B3_BASE_DE_DATOS.md).
- **Frontend:** React + TypeScript + Vite + Tailwind. Siete pantallas: Hoy
  (recomendación de cada empresa), detalle por empresa, Resultados, Modelos
  (comparación de los cinco y por qué se eligió la Regresión Logística), Aprende
  (qué es comprar, vender en corto y mantener, con un juego día por día con
  precios reales), Ayuda (guía de uso y glosario) y Acerca de. Detalle: [B4](B_sistema/B4_FRONTEND.md).
- **Despliegue:** Docker + gunicorn en Render (API) y sitio estático en
  Render (frontend), con despliegue automático desde la rama `main`.
  Detalle: [B5](B_sistema/B5_DESPLIEGUE.md).

**Regla de diseño importante:** todo lo que muestra la plataforma sale de
Yahoo Finance o del modelo. No hay valores simulados (al inicio sí los
había; se eliminaron en julio).

---

## 7. El paper (producto extra)

- *"A Benchmark of Five Machine-Learning Architectures for Daily
  Trading-Signal Classification on US Tech Equities"*, aceptado en
  **MICAI 2026**, capítulo 171490174 de LNAI (Springer). Autores: Polvo
  Cuatianquiz, Reyes Vera, Juárez Carbajal, Reyes Ramos y Aragón García.
  Versión final enviada el 8 de septiembre (12 páginas).
- Publica la comparación de los 5 modelos con la corrida **Etapa 3** (§7 del
  paper) y la verificación con el protocolo **Etapa 4** (§8: búsqueda simétrica e
  intervalos de confianza), más el experimento de selección de variables.
- **Lo que vino después y no está en el paper:** Etapa 5 (búsqueda de mejoras), prueba año por año,
  análisis de MANTENER, global vs por acción sobre las mismas filas,
  evaluación 2026 y la plataforma.

Detalle: [C1](C_paper/C1_PAPER_MICAI.md).

---

## 8. Las decisiones clave y su justificación

| Decisión | Por qué |
|---|---|
| Clasificar en 3 clases, no predecir el precio | Las decisiones de inversión son discretas y el valor exacto del retorno está dominado por ruido. MANTENER permite abstenerse cuando no hay información |
| Etiqueta por percentiles móviles 30/70 | Se adapta a cada régimen de volatilidad y no usa información futura |
| Separar los datos por tiempo | Separar al azar filtra información del futuro |
| F1-macro como métrica principal | Con 30/40/30, decir siempre MANTENER da 42 % de exactitud sin aprender nada; el F1-macro lo detecta |
| Evaluar también en dinero (Sharpe, drawdown…) | Un buen F1 no garantiza ganar dinero, y al revés |
| Modelo global (uno para las 7 acciones) | 7 veces más datos; gana o empata contra modelos por acción en los 5 modelos |
| Regresión Logística en producción | Gana en el protocolo del paper, empata en prueba año por año, opera menos (mejor con costos), es determinista, rápida e interpretable |
| Mantener 30/70 y horizonte de 1 día | 40/60 empeora; 5 días mejora pero cambia el problema (queda como trabajo futuro) |
| Corregir MANTENER con pesos al entrenar, no con un umbral fijo | Un umbral fijo empeora en 6 años de validación; el peso × 0.90 es el mejor en F1, kappa y Sharpe a la vez |
| SQLite y no PostgreSQL | La base es reconstruible y pequeña; el esquema es compatible con PostgreSQL si se necesita |

---

## 8b. Qué cambió desde el reporte de TT1

Los sinodales ya conocen el TT1 (18 de mayo). Lo esencial que cambió (todo
justificado en [D1](D_defensa/D1_TT1_VS_TT2.md)):

| TT1 | TT2 |
|---|---|
| Cada modelo con sus propias variables (LR 3–8, XGBoost 23–25, redes 3–25) | Las mismas 61 para los cinco (filtrar era peor en 11 de 15 casos) |
| Modelo por acción como estrategia principal | Modelo global (gana o empata en los cinco) |
| Exp A probaba en 2024–2025 | Los tres experimentos prueban en 2025 |
| Redes con hiperparámetros fijos; cuadrícula en LR y XGBoost | Optuna para los cinco (Etapa 4) |
| Un año de prueba, sin pruebas de significancia | + Intervalos bootstrap, permutación, prueba año por año 2020–2025, 2026 en vivo |
| Ganador en F1: XGBoost | Ganador: Regresión Logística (y empate con XGBoost en 6 años) |
| PostgreSQL con 9 tablas, ETL incremental en proceso aparte | SQLite con 4 tablas, recálculo completo dentro de la API |
| Aplicación "en desarrollo", local | Plataforma web terminada y desplegada |

Lo que **no cambió**: el problema, la etiqueta 30/70, las 7 acciones, los 5
modelos, la metodología CRISP-DM y la conclusión de fondo (los clásicos
igualan o superan a las redes).

---

## 9. Lo que no se hizo (y hay que decirlo así)

- **CatBoost, GRU, TabNet, Transformer y Random Forest no se corrieron.**
  Solo se consideraron. Además de los 5 modelos, solo se probó LightGBM.
- **No hay noticias, datos fundamentales, opciones ni datos intradía.**
- **El backtest es simplificado:** posición de tamaño fijo, un día, sin
  deslizamiento de precio. Los costos sí se calcularon en la Etapa 4 (5 y 10 pb),
  pero las cifras principales son sin costos.
- **No es una herramienta para invertir dinero real.** La plataforma es
  demostrativa y lo dice.

---

## 10. Si te piden contarlo en dos minutos

> "Comparamos cinco modelos —Regresión Logística, XGBoost, LSTM, CNN y
> CNN-LSTM— para generar señales diarias de comprar, mantener o vender en
> siete acciones tecnológicas, usando solo datos públicos de Yahoo Finance
> y una etiqueta basada en percentiles móviles del retorno del día
> siguiente. Con un protocolo que separa estrictamente entrenamiento,
> validación y prueba, búsqueda de hiperparámetros simétrica para los cinco
> e intervalos de confianza, la Regresión Logística fue significativamente
> mejor en 2025, con F1-macro de 0.40 y Sharpe de +0.89. En una prueba año por año
> de seis años, la LR y XGBoost empatan apenas arriba del azar y las redes
> quedan abajo: la conclusión es que en este régimen de pocos datos y poca
> señal, un modelo lineal bien regularizado es la mejor opción, y que las
> redes no aprenden nada más allá del azar porque las variables ya resumen
> la historia. Desplegamos ese modelo en una plataforma web que se
> actualiza sola cada día y lo evalúa con la misma metodología; en 2026,
> fuera de muestra, mantiene un F1 de 0.35. Parte del trabajo se publicó en
> MICAI 2026."
