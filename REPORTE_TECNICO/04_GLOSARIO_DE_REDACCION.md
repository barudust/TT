# 04 — Glosario de redacción

> Cómo llamar a cada cosa en el documento para que sea uniforme y no se
> confunda con nombres viejos. Si el documento ya usa una forma consistente
> que no está aquí, se puede conservar; lo importante es no mezclar.

---

## 1. Etapas del proyecto (en lugar de versiones)

El documento actual usa "v1" a "v8" en §6.6. Se sustituyen por **etapas**.

| Usar | No usar | Qué fue | Cuándo |
|---|---|---|---|
| **Etapa 1 — Línea base (TT1)** | v1, "la versión del reporte" | Sistema completo con selección de variables por modelo, por acción | Hasta mayo de 2026 |
| **Etapa 2 — Primeras mejoras** | "optimización de mayo", v0, v2, v3 | Optimización por modelo, preselección de variables, 181 y 94 variables, ensambles | Mayo–junio |
| **Etapa 3 — Comparación en igualdad de condiciones** | v4, "splits unificados" | 61 variables para los cinco, prueba 2025 en A/B/C, 120 corridas (paper §7) | Junio |
| **Etapa 4 — Protocolo final** | v5, V0–V6, "Vía 6" | Ninguna decisión con la prueba, Optuna para los cinco, mismas filas, intervalos (paper §8) | Agosto |
| **Etapa 5 — Búsqueda de mejoras** | v7, v8, "Vía 7", "Vía 8" | Calibración, mezclas, SWA, interacciones, otros horizontes | Fin de agosto |
| **Etapa 6 — Modelo de la plataforma y validación** | "análisis de septiembre" | Exceso de MANTENER, peso × 0.90, global contra por acción, 2026, plataforma | Septiembre–octubre |

**Pasos de la Etapa 4** (si hace falta citarlos): 4.1 Replicación,
4.2 Decisiones de protocolo, 4.3 Optuna para las redes, 4.4 Optuna para LR y
XGBoost, 4.5 Más variables (93), 4.6 Costos de transacción, 4.7 Intervalos y
prueba año por año.

**No existe "v6"** y no hay que mencionarlo. La frase de §6.6 "no existe una
v6 porque esa sigla se usó para una sub-etapa de la v5" se elimina.

## 2. Experimentos (particiones)

| Usar | Significa |
|---|---|
| **Experimento A** | Entrenamiento 2014–2023, validación 2024, prueba 2025 (10 años) |
| **Experimento B (principal)** | 2018–2023 / 2024 / 2025 (6 años) |
| **Experimento C** | 2020–2023 / 2024 / 2025 (4 años) |

Los experimentos **no son etapas**: se repiten dentro de las etapas 1 a 4.
"Caso A/B/C" (Tablas 5–7) → "Experimento A/B/C".

## 3. Validaciones adicionales

| Usar | No usar | Qué es |
|---|---|---|
| **Prueba año por año** (2020–2025) | walk-forward (salvo entre paréntesis la primera vez) | Para cada año T: entrenar [T−6, T−2], validar T−1, probar T |
| **Origen rodante** (2019–2024) | rolling origin | Para cada año Y: entrenar el pipeline de producción con los 6 años previos y predecir Y |
| **Prueba ciega 2026** | test 2026 | Datos del 2 de enero al 22 de octubre de 2026, no usados en ninguna decisión |
| **Análisis por subperiodos** | — | Solo si de verdad se divide un periodo; comparar A, B y C es "sensibilidad a la longitud del entrenamiento" |

## 4. Modelos

| Usar | Evitar |
|---|---|
| Regresión Logística (LR) | "RL", "regresión logística multinomial" solo cuando importe la formulación |
| XGBoost | XGB (salvo en tablas) |
| LSTM | "LSTM puro" |
| CNN 1D | "CNN puro", "CNN" sola (salvo en tablas) |
| CNN-LSTM | "híbrido", "CNN-LSTM híbrido" (basta una vez) |
| Modelos clásicos / de aprendizaje automático clásico | "ML" sin explicar |
| Redes neuronales / modelos de aprendizaje profundo | "DL" sin explicar |
| Modelo global (uno para las 7 acciones) / modelo por acción | "modelo por activo" (vale, pero elegir uno y usarlo siempre) |
| Modelo de la plataforma: `LR-v8-interactions-holdw090` | "el modelo v8": el nombre interno solo como identificador entre comillas de código |

## 5. Clases y señales

| En el texto | En tablas y fórmulas | En la plataforma |
|---|---|---|
| comprar, vender (en corto), mantener | BUY (2), SELL (0), HOLD (1) | Comprar / Vender / Mantener |

- La primera vez: "comprar (BUY, posición larga), vender (SELL, posición
  corta) y mantener (HOLD, sin posición)". Después, en español.
- "Vender" **siempre** es venta en corto en este trabajo; nunca "liquidar".
- **"Señal"** se usa en el documento técnico; en la descripción de la
  interfaz se dice "recomendación" (así aparece en la plataforma).

## 6. Métricas

| Usar | Notas |
|---|---|
| F1-macro | Métrica principal |
| exactitud (accuracy) | No como criterio principal |
| exactitud balanceada | Promedio del recall de las tres clases |
| kappa de Cohen (κ) | 0 = azar |
| AUC macro (uno contra todos) | 0.5 = azar |
| pérdida logarítmica (log-loss) | ln 3 ≈ 1.099 = decir 1/3 a todo |
| índice (razón) de Sharpe anualizado | con 0 y 10 pb de costo |
| rotación | cambio medio de posición por día |
| win rate, profit factor, caída máxima (drawdown) | Métricas secundarias de la simulación |
| pb (puntos base) | 10 pb = 0.10 % por cambio de posición |

## 7. Sistema

| Usar | No usar |
|---|---|
| Actualización diaria (programada dentro de la API) | "pipeline ETL" como proceso aparte |
| SQLite | PostgreSQL (salvo como antecedente o alternativa) |
| Plataforma web / aplicación web | "dashboard" |
| Pantalla «Hoy», «Detalle», «Resultados», «Modelos», «Aprende», «Ayuda», «Acerca de» | "Nivel 1 / 2 / 3" |
| Seguridad de la recomendación: «Nada segura», «Poco segura», «Medianamente segura» | "seguro / mitad seguro / poco seguro", "confianza 36 %" |
| Render (servicio web en Docker + sitio estático) | "servidor" sin decir cuál |
| `GET /stocks`, `GET /model`… (rutas reales) | `/api/summary`, `/api/signals`, `/api/equity/{ticker}` |

## 8. Estilo

- **Impersonal** en todo el documento ("se observó", "se corrigió"), no
  "nos dimos cuenta" ni "pensamos que lo honesto era". Las secciones que hoy
  están en primera persona: 5.3.3, 5.4.3, 5.5.3, 5.5.4, 5.5.5, 6.6.
- Números con punto decimal (0.404) como en el resto del documento; miles
  con espacio fino o coma de forma consistente (1 736 o 1,736).
- Fechas: "2 de enero de 2026" en texto; ISO (2026-01-02) solo en tablas
  técnicas o nombres de archivo.
- Los nombres de archivos y funciones del repositorio, en `monoespaciado`.
