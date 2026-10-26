# 02 — Contradicciones

> Lista de control. Cada renglón es un lugar donde el documento dice dos
> cosas distintas, o dice algo distinto de lo que hace el sistema o de lo que
> publica el paper. Al terminar la corrección **ninguna** debe quedar.
> "Resolución" dice cuál versión es la correcta; el detalle de cómo
> redactarlo está en `correcciones/`.

---

## A. Contradicciones internas del documento

| ID | Tema | Lo que dice en un lugar | Lo que dice en otro | Resolución |
|---|---|---|---|---|
| C-01 | **Número de características** | 54: Resumen (p. 1), Abstract (p. 2), §4.2 (p. 38), §4.3 (p. 39–40), §4.4.6 (p. 51), §5.2.1 y Fig. 2 (p. 69), §5.2.2 (p. 70), §6.1 (p. 82) | 46: Fig. 3 (p. 71), Fig. 4 (p. 72), Tabla 12 (p. 73). 61: Tabla 4 (p. 42–46, cuenta sus filas: 5+4+9+8+9+8+7+5+6) | **61** características base en 9 familias; en producción **76** (61 + 15 interacciones). El 46 era la unión de las variables seleccionadas en TT1; desaparece |
| C-02 | Medias móviles | "ocho características" (§4.3.3, p. 40) | La Tabla 4 lista 9 (5 distancias, 3 cruces, 1 pendiente) | **9** |
| C-03 | Tabla de características | "La tabla 3 presenta…" y "Ver Tabla 3, categoría…" (p. 40–42, nueve veces) | La tabla es la **Tabla 4**; la Tabla 3 es la partición temporal | Referencias cruzadas automáticas de Word |
| C-04 | **Partición del Experimento A** | Tablas 3 (p. 39) y 8 (p. 52): A prueba en **2024–2025**, valida en 2022–2023 | §4.5.1 (p. 52): "Los tres experimentos comparten el mismo conjunto de prueba (2025)"; §6 (p. 82) y §6.2.1 (p. 83): "prueba de 2025" | **A = 2014–2023 / 2024 / 2025** (desde la Etapa 3). La de TT1 se menciona solo como antecedente |
| C-05 | **Primeros días de cada conjunto en las redes** | §2.3.4 (p. 18–19): "las primeras W−1 observaciones de cada segmento se descartan"; §6.4 (p. 90): las redes usan 228 o 188 días de prueba contra 248 | §4.5.2 (p. 53): "la ventana del primer día de validación usa los últimos días del entrenamiento como contexto" | Etapa 1: se descartaban. **Etapa 4: ventanas sobre la serie continua, asignadas por la fecha de la etiqueta → mismas 1 736 filas para los cinco** |
| C-06 | Formulación de la LR | §2.4.1 (p. 19): softmax multinomial | §4.8.1 (p. 57): one-vs-rest con sigmoide | **Multinomial (softmax)** en las Etapas 3–4 y en producción. One-vs-rest fue TT1 |
| C-07 | Pooling de la CNN 1D | §2.5.3 (p. 24): *max pooling* ("retiene únicamente la activación máxima") | §4.8.5 (p. 59–60): *Global Average Pooling* | Etapa 3: promedio + máximo global; **Etapa 4 (final): promedio global**. Ver `tablas/T-05` |
| C-08 | **Búsqueda de hiperparámetros de las redes** | §4.8.3 (p. 58), §4.8.4, §6.1 (p. 83): "no se realiza búsqueda; arquitectura fija" | §4.10.1 (p. 63): "búsqueda en rejilla reducida (unidades, dropout, tasa)" | **Etapa 4: Optuna, 80 intentos, 17–20 hiperparámetros** para cada red |
| C-09 | **Paro temprano** | §4.8.3 (p. 58): pérdida de validación, paciencia 15, máximo 80 épocas | §4.10.2 (p. 63): F1 de validación, paciencia 10, máximo 100 épocas | **Etapa 4:** hasta 100 épocas, paciencia 20, criterio elegido por Optuna (pérdida, F1 o F1 promedio de 3) |
| C-10 | Con qué se entrena el modelo final | §4.8.1 (p. 57) y §6.1 (p. 83): se reentrena con entrenamiento + validación | §4.10.1 (p. 63): "entrenar el modelo final sobre el conjunto de entrenamiento completo" | **Clásicos:** entrenamiento + validación. **Redes:** solo entrenamiento (reentrenarlas las empeoraba −0.024 a −0.047) |
| C-11 | Periodo evaluado | §4.8.1 (p. 57): "sobre los primeros 90 días del conjunto de prueba" | §7.2 obj. 2 (p. 100): "todos sobre el conjunto de prueba completo del año 2025" | **Año completo** (248 días hábiles por acción; 1 736 filas) |
| C-12 | **Cómo se eligió el lookback** | §4.10.1 (p. 63): en validación | §6.2 (p. 83): "la configuración de lookback que produjo el mayor F1-macro sobre el conjunto de prueba" | Etapas 1 y 3: **con la prueba** (error de protocolo, el paper lo declara). Etapa 4: con 2024 |
| C-13 | **Qué significa VENDER y MANTENER en la simulación** | §2.6.3 (p. 26): vender = "liquidar la posición o mantener efectivo"; mantener = "preserva la posición existente" | Resumen (p. 1), §2.2.2, §4.9.3 (p. 62) y §4.11.1 (p. 65): vender = **posición corta**; mantener = **fuera del mercado** (capital sin cambio) | **COMPRAR = +1, VENDER = −1 (corto), MANTENER = 0 (fuera)**. Corregir §2.6.3 |
| C-14 | Fórmula del retorno acumulado | §4.9.3 (p. 62): `Π(1 + r_t · dirección) − 1` con `r_t` logarítmico | §4.11.2 (p. 65): suma de retornos logarítmicos y luego `e^R − 1` | **Una sola:** `R = Σ posición_t · r_{t+1}` (log) y `R% = e^R − 1`; con costos, restar `c · |pos_t − pos_{t−1}|` |
| C-15 | Fórmula de exactitud | §2.6.1 (p. 25): `Σ_k TP_k / n` | §4.9.1 (p. 61): `(TP+TN)/(TP+TN+FP+FN)` (binaria) | **`Σ_k TP_k / n`** (multiclase) |
| C-16 | **Significancia estadística** | §2.1.3 (p. 12): buscar señales "con valor predictivo estadísticamente significativo; la EMH es la hipótesis nula"; §2.5.4 (p. 25): "mejora estadísticamente significativa" | Cap. 4 (p. 36): "no se realiza una prueba de significancia estadística formal" | **Sí se hacen:** bootstrap por bloques (IC 95 %), diferencias pareadas, permutación, Wilcoxon/signo, prueba año por año, prueba ciega 2026 |
| C-17 | Modelos en la pregunta e hipótesis | Cap. 4 (p. 35–36): "modelos de DL (LSTM y CNN-LSTM)" | Todo el documento compara tres redes (LSTM, CNN 1D, CNN-LSTM) | Incluir la **CNN 1D** |
| C-18 | **Mismas características para todos** | §3.6 (p. 34): "con los mismos datos, las mismas características de entrada y las mismas métricas" | §4.1 (p. 36): "cada modelo recibe una representación de entrada distinta en número de características"; §4.4 y Tablas 5–7 | **Mismas 61 para los cinco** (Etapa 3 en adelante) |
| C-19 | Qué es el capítulo 7 | Índice (p. 4) y título (p. 99): "Análisis parcial de resultados" | Introducción (p. 8): "El capítulo 7 presenta las conclusiones" | **Conclusiones** (TT2 es el documento final) |
| C-20 | Títulos de 6.3 y 6.4 | 6.3 "Resultados económicos por experimento" | Su contenido es la jerarquía de clasificación; el contenido económico está en 6.4 "Comparativa entre modelos" | Se resuelve con la estructura nueva; si no, intercambiar títulos |
| C-21 | "Los clásicos superan a las redes en todos los experimentos" | §6.3.1 (p. 87) | Tabla 17 y §6.2.3 (p. 85): en C, CNN-LSTM 0.356 > LR 0.350 | Con cifras de TT1 la frase es falsa. En la Etapa 4 sí es cierta (la LR es la mejor en A, B y C con significancia) |
| C-22 | Conteo de la Tabla 20 | §6.3.3 (p. 88): "LR lidera en cuatro de los siete activos en F1 y en cinco en Sharpe" | La Tabla 20 da **3 y 3** (F1: AAPL, NVDA, GOOGL; Sharpe: AAPL, NVDA, META) | Si se conserva (Etapa 1), corregir a 3 y 3 |
| C-23 | Promedios por activo de las redes | Tabla 16 (p. 85): LSTM 0.297, CNN-LSTM 0.342, CNN 0.329 | Tabla 21 (p. 88): 0.288, 0.323, 0.306 | La Tabla 21 usa lookback 20; la 16, el mejor lookback **elegido con la prueba**. Si se conservan, decirlo |
| C-24 | **Aporte del bloque recurrente** | §6.3.6 (p. 89) y §7.3 (p. 101): en A la diferencia es "0.012 a favor del CNN-LSTM"; §7.2 obj. 3: "CNN-LSTM supera consistentemente a LSTM y CNN 1D" | Tabla 15 y §6.2.1 (p. 83): en A, **CNN 1D 0.333 > CNN-LSTM 0.321**. Con lookback 20 la diferencia es 0.017, no 0.019 | En TT1 el signo cambia según el experimento. En la Etapa 4 sus intervalos se traslapan en B (0.372 contra 0.359, no significativa) |
| C-25 | Sharpe de TSLA y MSFT | §6.4.1 (p. 91): "Sharpe negativo en ambos modelos" | Tabla 28: XGBoost TSLA en B = +0.885 | Solo MSFT es negativo en ambos |
| C-26 | "TSLA es el único activo con Sharpe positivo de XGBoost en los tres experimentos" | §6.5.3 (p. 94) | Tabla 28: AMZN (0.138, 0.255, 1.068) y META (0.848, 0.917, 0.258) también | Corregir o eliminar |
| C-27 | **Activo más difícil** | §6.2.3 (p. 86): TSLA; §6.5.4 (p. 95): NVDA, F1 0.269, "ningún modelo produce Sharpe positivo en los tres experimentos" | §7.3 (p. 101): TSLA 0.269 y NVDA 0.284. Con las Tablas 15–17, el promedio de NVDA es ≈ 0.299 y el de TSLA ≈ 0.300. La LR en NVDA tiene Sharpe positivo en los tres (0.730, 1.479, 0.735) | Eliminar las cifras 0.269/0.284; si se conserva el análisis, recalcular |
| C-28 | Activos más sensibles para la LR | §6.5.2 (p. 93): "TSLA y GOOGL (0.066 y 0.079)" | Tabla 27: AAPL tiene 0.078; GOOGL marcado "Ambos" aunque LR (0.079) > XGBoost (0.053) | Corregir o eliminar |
| C-29 | **Rutas de la API** | Tabla 13 (p. 74–75): `/health`, `/metrics`, `/stocks`, `/stocks/<s>`, `.../history`, `.../metrics`, `.../info` (7 rutas) | Fig. 1, Tabla 10, §5.1.1: "6 endpoints". §5.4.2, §5.5.1, Fig. 5 y Fig. 6: `/api/summary`, `/api/signals`, `/api/equity/{ticker}`, `/api/metrics/{ticker}` | **Las del sistema real:** 9 GET + `POST /admin/refresh` (`tablas/T-14`) |
| C-30 | Número de tablas de la base de datos | Fig. 1 y Tabla 10: "9 tablas 3FN + 1 desnormalizada" (10) | Fig. 4 y Tabla 12: 9 tablas en total (8 + `snapshots_90d`) | **SQLite con 4 tablas** (sistema real) |
| C-31 | Cómo obtiene la señal el servidor | Cap. 5: el ETL calcula y guarda una vez al día; la API solo lee | §7.2 obj. 4 (p. 100): "al recibir una solicitud, el servidor descarga los datos más recientes del activo… y devuelve la señal del mejor modelo para ese activo en el Experimento B" | **Actualización programada diaria dentro de la API; un solo modelo global** para las 7 acciones |
| C-32 | **Estado de la plataforma** | §5.5.3–5.5.5: servidor y página ya vinculados y probados | §5.5.6 (p. 81): "la integración del modelo ganador está pendiente"; §7.2 obj. 4: "en desarrollo"; §7.5 (p. 102): "componentes independientes", "fase de desarrollo local" | **Terminada, integrada y desplegada en Render** con `LR-v8-interactions-holdw090` |
| C-33 | Búsqueda de hiperparámetros como trabajo futuro | §7.5 (p. 102): "la configuración actual se obtuvo mediante ajuste manual; implementar grid search o Bayesian optimization" | §4.10.1: grid search; §6.6.3: Optuna con 150/80 intentos | **Ya se hizo (Optuna, Etapa 4)**; sale de trabajo futuro |
| C-34 | **Un modelo por acción o uno global** | §2.1.2 (p. 12), §4.8 (p. 56), §6.1 (p. 82): "estrategia principal: un modelo independiente por activo"; §7.2 obj. 3: "la recomendación debe considerar el activo específico" | Tabla 21 (p. 88): el global supera al por activo en 4 de 5 modelos; la plataforma usa **un solo modelo global** | **Global como estrategia principal** (Etapa 3 en adelante); por acción como comparación |
| C-35 | Cuál es la conclusión | §7.1 (p. 99): "XGBoost obtiene el mayor F1-macro promedio"; §7.2 obj. 3: "XGBoost es el modelo con mayor F1" | §6.6.8 (p. 98): "refuerzan la conclusión del capítulo 7: un modelo lineal bien regularizado iguala o supera a las arquitecturas profundas" | **LR**, con el matiz de que en seis años empata con XGBoost |
| C-36 | Año de la aplicación | Tabla 1 (p. 33): "Año de lanzamiento: 2025" | Portada: 2026; despliegue en 2026 | **2026** |
| C-37 | Scripts del pipeline de TT1 | §6.1 (p. 82): "Los Scripts 06, 07 y 08 entrenan LSTM, CNN-LSTM y CNN 1D" | En el repositorio, `scripts_v1/08_evaluate_models.py` evalúa; la CNN 1D no está en `scripts_v1/` | Describir el pipeline final por etapa (`tablas/T-16`) |

---

## B. El documento contra el sistema y el repositorio

| ID | Tema | Documento | Realidad (con fuente) |
|---|---|---|---|
| S-01 | Base de datos | PostgreSQL 12+, 9 tablas en 3FN + 1 desnormalizada, JSONB, `ON DELETE RESTRICT`, psycopg2, puerto 5432 (Fig. 1, 4, 6; Tablas 10, 12, 14; §5.1.1, §5.3) | **SQLite** con SQLAlchemy, 4 tablas (`assets`, `ohlcv_daily`, `predictions`, `metrics`), restricciones únicas, borrado en cascada; perfil opcional de PostgreSQL 15 en `docker-compose.yml` (`api/models.py`, `ESTUDIO_TT/B_sistema/B3_BASE_DE_DATOS.md`) |
| S-02 | Pipeline diario | Script aparte con cron de Linux, incremental (solo el día), 7 pasos, 3–5 min, métricas semanales y mensuales, `snapshots_90d` (§5.2.2, Tabla 11, Fig. 3, §5.5.2) | **Dentro de la API con APScheduler**, 16:30 hora de Nueva York de lunes a viernes, al arrancar, cada 2 min si falta una acción y con `POST /admin/refresh`; **recalcula ~3 años** en segundos; métricas en ventanas de 30/60/90 días (`api/main.py`, `B2_API.md`) |
| S-03 | API | 6–7 GET, formato `{status, data, message}`, lectura de `snapshots_90d` en < 50 ms, puerto 5000 | 9 GET (`/health`, `/model`, `/market-status`, `/stocks`, `/stocks/:s`, `.../history`, `.../metrics`, `/metrics`, `.../info`) + `POST /admin/refresh`; 5 POST de carga **desactivados (403)**; formato `{success, data}` / `{success: false, error}`; caché en memoria; puerto 8000 local (`B2_API.md`) |
| S-04 | Interfaz | 3 niveles (panel, tarjetas, detalle expandible), matriz de confusión, gráfica de pastel, consulta a la API cada hora, puerto 3000 (§5.4, Fig. 5) | **7 pantallas** (Hoy, Detalle, Resultados, Modelos, Aprende, Ayuda, Acerca de); curva «¿Qué habría pasado con $1,000?»; seguridad en palabras; **sin** matriz de confusión, sin pastel, sin consulta cada hora; Vite en el puerto 5173 (`B4_FRONTEND.md`) |
| S-05 | Niveles de seguridad | "seguro", "mitad seguro" y "poco seguro" (§5.4.3, §5.5.5) | **«Nada segura» (acertó 37 de cada 100), «Poco segura» (38), «Medianamente segura» (42)**; azar 33. No hay nivel «Segura» (`Frontend/src/app/format.ts`, `calibrar_niveles_confianza.py`) |
| S-06 | Despliegue | Solo local; producción como trabajo futuro | **Render**: API en Docker con gunicorn (1 worker) y sitio estático; despliegue automático desde `main` (`render.yaml`, `B5_DESPLIEGUE.md`) |
| S-07 | Modelo en producción | "Pendiente de selección" | **`LR-v8-interactions-holdw090`**: LR L2, C = 0.000165, RobustScaler, 76 variables, pesos balanceados con MANTENER × 0.90, entrenada con 2018–2025 (`scripts_opt/entrenar_produccion.py`, `api/ml/model.py`) |
| S-08 | Pruebas | Pruebas manuales | **24 pruebas automáticas** (pytest) + pruebas funcionales (`api/tests/`) |
| S-09 | Versiones | Python 3.12.3, scikit-learn 1.8.0, PyTorch 2.11.0, pandas 3.0.0, yfinance 1.2.0 (§6.1) | Investigación (suplementario del paper): Python 3.13.5, **scikit-learn 1.7.2**, PyTorch 2.12 (CUDA 12.8), XGBoost 3.2.0, Optuna 4.8. Producción: scikit-learn 1.7.2, pandas 3.0.2, numpy 2.4.4, yfinance 1.3.0, Flask 3.1.3 (`api/requirements.txt`, `scripts_opt/requirements.txt`) |
| S-10 | Costos de transacción | "No se incorporan" (§4.9.3, §4.11, §6.4, §7.4) | Calculados con 5 y 10 pb en la Etapa 4 (LR B: Sharpe +0.89 → +0.62) |
| S-11 | Pruebas de significancia | "No se realiza" | Bootstrap por bloques (2 000 réplicas, bloques de 20 días), permutación (500), Wilcoxon/signo (`run_v5.py`, `v5/v6_ic_*`) |
| S-12 | Dataset | Termina el 31/12/2025; "el año 2026 no se incluye" (§4.1.1) | Sigue así para el desarrollo; **2026 se usa solo para validar** (enero–22 de octubre, `tesis_ml_stocks/01_raw_datasets_2026/`) y la plataforma descarga datos diarios |
| S-13 | Interpolación de faltantes | "interpolación lineal si faltan < 1 %" (§4.2) | No hay huecos en las 7 acciones; SPY/VIX se alinean con `ffill` (último valor conocido), nunca con valores futuros (`01_build_raw_dataset.py`) |
| S-14 | "Datos desde 2009" | §4.3 (p. 39) | Descarga desde **2013-01-01** (`DOWNLOAD_START`); el comentario del código que dice 2009 está desactualizado |

---

## C. El documento contra el paper (MICAI 2026)

| ID | Tema | Reporte | Paper | Resolución en el reporte |
|---|---|---|---|---|
| P-01 | Mejor modelo | XGBoost (TT1) | LR (0.399 promedio §7; 0.404 [0.379, 0.428] §8) | LR |
| P-02 | Variables | Selección por modelo | 61 para todos; §6: filtrar empeora en 11 de 15 | 61 para todos |
| P-03 | Estrategia | Por activo | Global y por activo; global principal | Global principal |
| P-04 | Partición A | 2014–2021 / 2022–2023 / 2024–2025 | 2014–2023 / 2024 / 2025 | La del paper |
| P-05 | Significancia | No | Intervalos bootstrap §8 | Sí |
| P-06 | Búsqueda de las redes | Fija | Optuna simétrico §8 | Optuna |
| P-07 | CNN-LSTM con 5 canales OHLCV | Sí (§4.4.5, §4.6.4) | El paper también lo dice (§4), **pero el código de la Etapa 3 no los usa** | No repetirlo: desde la Etapa 3 las cinco reciben las mismas 61 variables |
| P-08 | LSTM | Unidireccional (TT1) | Bidireccional (Etapa 3, §4) | Etapa 3 bidireccional; Etapa 4 (Optuna) unidireccional con atención |
| P-09 | Lo que el paper no tiene | — | No tiene costos, prueba año por año, 2026, plataforma | El reporte sí; decir que el TT es más amplio que el paper |

Detalle de qué toma el paper de cada etapa: `../PAPER_MICAI/04_PAPER_VS_TT.md`.
