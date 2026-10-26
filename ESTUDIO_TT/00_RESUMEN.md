# Resumen de todo el TT (leer antes de profundizar)

> Una página por módulo, con lo mínimo para saber qué se hizo y dónde
> profundizar. Siguiente nivel: el resumen de cada sección
> ([A0](A_modelo/A0_RESUMEN_MODELO.md), [B0](B_sistema/B0_RESUMEN_SISTEMA.md),
> [C0](C_paper/C0_RESUMEN_PAPER.md), [D0](D_defensa/D0_RESUMEN_DEFENSA.md)). Si solo tienes 15 minutos, lee esto. Para la historia
> completa: [01 Panorama](01_PANORAMA_GENERAL.md). Términos:
> [glosario](02_GLOSARIO.md).

---

## En una frase

Comparamos cinco modelos (Regresión Logística, XGBoost, LSTM, CNN 1D y
CNN-LSTM) para dar cada día una señal de **COMPRAR, MANTENER o VENDER** en
7 acciones tecnológicas de EE. UU. con datos gratuitos de Yahoo Finance;
**ganó la Regresión Logística**, demostramos por qué las redes no la
superan, y la desplegamos en una **plataforma web** que se actualiza sola
cada día. Parte del trabajo se publicó en **MICAI 2026**.

## Las 6 cifras que hay que saberse

| Qué | Cifra |
|---|---|
| LR en 2025 (prueba principal, protocolo de la Etapa 4) | **F1-macro 0.404**, intervalo 95 % [0.379, 0.428], **Sharpe +0.89** |
| Los otros cuatro en 2025 | 0.359–0.372 (la LR es significativamente mejor) |
| Seis años de prueba año por año (2020–2025) | LR 0.350 y XGBoost 0.356 empatan; redes 0.29–0.33 |
| Techo | Ningún modelo pasa de **0.394** en ningún año |
| Modelo en producción, 2026 (nunca visto) | **F1 0.354**, kappa 0.035 |
| Referencias | Azar ≈ 0.33; decir siempre MANTENER ≈ 0.20 |

## Cómo llegamos aquí (línea de tiempo)

| Cuándo | Qué |
|---|---|
| Hasta 18 mayo | **Etapa 1 — Línea base (TT1)**: XGBoost mejor en F1, LR mejor en Sharpe, redes abajo; app "en desarrollo" |
| Mayo–junio | **Etapa 2 — Primeras mejoras**: optimización por modelo, más variables, ensambles; filtrar variables empeora (paper §6). Cifras no reportables (se eligió con la prueba) |
| Junio | **Etapa 3 — Comparación en igualdad**: las 61 variables para todos y prueba 2025 en A, B y C (paper §7) |
| Julio | Modelo conectado a la API, base de datos, despliegue en Render |
| Agosto | **Etapa 4 — Protocolo final**: diagnóstico de las redes, Optuna para los cinco, intervalos, costos, prueba año por año (paper §8). **Resultado principal** |
| Fin de agosto | **Etapa 5 — Búsqueda de mejoras**: casi nada ayuda; se adoptan 15 interacciones; cambiar la etiqueta queda fuera del planteamiento |
| Sep–oct | **Etapa 6 — Plataforma y validación**: exceso de MANTENER y su ajuste, 2026 fuera de muestra, niveles de seguridad, auditoría de la plataforma |

Detalle y equivalencias con los nombres viejos (v1 … v8): [mapa de experimentos](03_MAPA_DE_EXPERIMENTOS.md).

---

## Módulo A — El modelo

### A1. Datos y etiqueta → [detalle](A_modelo/A1_DATOS_Y_ETIQUETA.md)
- **Datos:** precios diarios (OHLCV) de AAPL, NVDA, TSLA, AMZN, MSFT, GOOGL y
  META, 2013–2025, más el S&P 500 (SPY) y el VIX. 21 119 filas.
- **Etiqueta:** retorno del día siguiente comparado con los percentiles 30 y
  70 de los últimos 252 días de esa acción: arriba del 70 → COMPRAR, abajo
  del 30 → VENDER, en medio → MANTENER (~30/40/30). Se adapta a la
  volatilidad y no usa información futura (`shift(1)`).

### A2. Variables → [detalle](A_modelo/A2_VARIABLES.md)
- **61 variables** en 9 familias: retornos, momentum, medias móviles,
  volatilidad, osciladores (RSI, MACD…), volumen, forma de la vela,
  calendario y mercado (SPY, VIX). Producción agrega **15 interacciones = 76**.
- Las más importantes son de volatilidad y del VIX.
- En TT1 cada modelo tenía su propio filtro de variables; filtrar resultó
  peor en 11 de 15 casos, así que ahora todos usan las 61.

### A3. Protocolo y métricas → [detalle](A_modelo/A3_PROTOCOLO_Y_METRICAS.md)
- Separación **por tiempo**: 3 experimentos con prueba 2025 y 10, 6 u 4 años
  de entrenamiento (B = 2018–2023 es el principal).
- **Etapa 4:** toda decisión se toma con 2024; 2025 se evalúa una sola vez.
- Métricas: **F1-macro** (principal), kappa, y simulación económica
  (Sharpe, drawdown, win rate, profit factor; también con costos).
- Contra la suerte: bootstrap por bloques, permutación, prueba año por año, 2026.

### A4. Regresión Logística y XGBoost → [detalle](A_modelo/A4_MODELOS_CLASICOS.md)
- **LR en producción:** multinomial, L2, **C = 0.000165** (regularización muy
  fuerte), RobustScaler, pesos "balanced" con MANTENER × 0.90, 231
  parámetros, entrenada con 2018–2025.
- **XGBoost:** 485 árboles; empata con la LR en 6 años pero opera más, y con
  costos pierde (Sharpe +0.01 contra +0.62).

### A5. Redes neuronales → [detalle](A_modelo/A5_REDES_NEURONALES.md)
- Ganadoras de Optuna: **LSTM** 2 capas × 118 con atención (198 mil
  parámetros); **CNN 1D** 2 bloques 50→100, kernel 7 (67 mil); **CNN-LSTM**
  2 bloques 77→154 + 1 LSTM de 136 (276 mil).
- **Por qué no ganan:** su pérdida de validación nunca baja del azar (ln 3),
  una LSTM 57 veces más chica rinde igual, y las variables ya resumen la
  historia que ellas leerían.
- Asimetría a conocer: su ventana termina un día antes que la de la LR
  (cuesta ≈ 0.007 de F1; no cambia la conclusión).

### A6. Las seis etapas → [detalle](A_modelo/A6_ETAPAS_DEL_PROYECTO.md)
- 1 línea base (TT1) · 2 primeras mejoras · **3 comparación en igualdad** (paper §7) ·
  **4 protocolo final** (paper §8, resultado principal) · 5 búsqueda de mejoras ·
  6 plataforma y validación.

### A7. Resultados y límites → [detalle](A_modelo/A7_RESULTADOS_Y_LIMITES.md)
- La señal existe pero es **débil e inestable entre años**; 2025 fue el mejor.
- **Exceso de MANTENER:** el modelo sabe cuándo habrá movimiento pero no
  hacia dónde ("voto dividido"). Ajuste con peso × 0.90: en 2026 MANTENER
  60 % → 40 % (real 35 %) y F1 0.313 → 0.354.
- El modelo **global** gana o empata contra uno por acción en los 5 modelos.

---

## Módulo B — El sistema

### B1. Arquitectura → [detalle](B_sistema/B1_ARQUITECTURA.md)
```
Investigación (offline) ──► modelo .pkl
Yahoo Finance ──► API Flask (calcula variables, predice, evalúa) ──► SQLite
                     └──► JSON ──► App web React ──► navegador
```
Nada es simulado: todo sale de Yahoo o del modelo.

### B2. API → [detalle](B_sistema/B2_API.md)
- **Flask** con ~10 rutas de lectura (`/stocks`, `/metrics`, `/model`…).
- Se actualiza sola lunes a viernes a las 16:30 de Nueva York (y reintenta
  cada 2 min si falla Yahoo); recalcula ~3 años con el mismo código del
  entrenamiento. **24 pruebas automáticas.**

### B3. Base de datos → [detalle](B_sistema/B3_BASE_DE_DATOS.md)
- **SQLite**, 4 tablas: `assets`, `ohlcv_daily`, `predictions`, `metrics`.
- 1FN y 2FN; 3FN en las tablas base, con columnas derivadas a propósito
  (registro de lo mostrado).
- El TT1 proponía PostgreSQL con 9 tablas; se cambió porque ahora hay un
  solo escritor y la base es reconstruible (el esquema sigue siendo
  compatible con PostgreSQL).

### B4. Frontend → [detalle](B_sistema/B4_FRONTEND.md)
- **React + TypeScript + Vite + Tailwind**, aplicación web.
- 7 pantallas: Hoy, detalle por empresa, Resultados, **Modelos** (la comparación de los cinco con gráficas y por qué se eligió la Regresión Logística), **Aprende** (comprar, vender en corto y mantener, con ejemplos que se mueven y un juego con precios reales), Ayuda (guía + glosario) y Acerca de.
- Seguridad de cada recomendación en palabras (Nada / Poco / Medianamente segura).
- Muestra las 3 probabilidades, el resultado real de cada señal y el F1
  contra el azar.

### B5. Despliegue → [detalle](B_sistema/B5_DESPLIEGUE.md)
- **Render**: API en Docker con gunicorn (1 worker) + sitio estático;
  despliegue automático con cada cambio en `main`.
- Problemas reales resueltos: arranque en frío y fallas de Yahoo.

---

## Módulo C — El paper → [detalle](C_paper/C1_PAPER_MICAI.md)

- *"A Benchmark of Five Machine-Learning Architectures for Daily
  Trading-Signal Classification on US Tech Equities"*, **MICAI 2026**
  (Springer LNAI). Enviado el 8 de septiembre.
- Publica la comparación Etapa 3 y su verificación Etapa 4 (la LR significativamente
  mejor) y que filtrar variables no ayuda.
- Es un **producto extra**: el TT es más amplio (prueba año por año, 2026,
  análisis de MANTENER, plataforma).

---

## Módulo D — La defensa

| Documento | Para qué |
|---|---|
| [D1 TT1 → TT2](D_defensa/D1_TT1_VS_TT2.md) | **El más importante:** qué cambió desde el TT1 y por qué |
| [D2 Generales](D_defensa/D2_PREGUNTAS_GENERALES.md) | Contribución, objetivos, metodología, brecha |
| [D3 Datos](D_defensa/D3_PREGUNTAS_DATOS.md) | Etiqueta, variables |
| [D4 Modelos](D_defensa/D4_PREGUNTAS_MODELOS.md) | Capas de las redes, por qué ganó la LR |
| [D5 Estadística](D_defensa/D5_PREGUNTAS_ESTADISTICA.md) | Significancia, fuga de información, MANTENER |
| [D6 Sistema](D_defensa/D6_PREGUNTAS_SISTEMA.md) | API, base de datos, frontend, despliegue |
| [D7 Paper](D_defensa/D7_PREGUNTAS_PAPER.md) | Revisión y relación con el TT |
| [D8 Trampa](D_defensa/D8_PREGUNTAS_TRAMPA.md) | Las preguntas incómodas |

**Las tres ideas que sostienen la defensa:**
1. **Del TT1 a TT2 se corrigió lo que el propio TT1 señaló** (variables
   distintas por modelo, redes sin búsqueda, un año de prueba, app sin
   terminar), y la conclusión se mantuvo: los clásicos igualan o superan a
   las redes.
2. **Lo medimos con honestidad:** 2025 fue el mejor año; en seis años y en
   2026 la señal es débil. Eso también es un resultado.
3. **El sistema funciona en producción** con la misma metodología de la
   tesis, y se autoevalúa cada día.

**Lo que nunca hay que decir:** que se probaron CatBoost, GRU, Transformer,
TabNet o Random Forest (no se corrieron; solo LightGBM), o que el modelo
sirve para invertir dinero real.
