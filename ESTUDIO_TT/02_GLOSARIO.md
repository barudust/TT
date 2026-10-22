# 02 — Glosario

> Cada término que aparece en el TT, explicado en palabras simples y con
> dónde se usa. Está agrupado por tema y ordenado alfabéticamente dentro de
> cada grupo. Las fórmulas van solo cuando ayudan.

**Grupos:** [Finanzas y mercado](#1-finanzas-y-mercado) ·
[Indicadores técnicos](#2-indicadores-técnicos) ·
[Datos y preparación](#3-datos-y-preparación) ·
[Aprendizaje automático](#4-aprendizaje-automático-general) ·
[Modelos](#5-modelos) · [Redes neuronales](#6-redes-neuronales) ·
[Métricas](#7-métricas) · [Estadística y validación](#8-estadística-y-validación) ·
[Software y sistema](#9-software-y-sistema) · [Nombres propios del proyecto](#10-nombres-propios-del-proyecto)

---

## 1. Finanzas y mercado

| Término | Qué es | Dónde aparece |
|---|---|---|
| **Acción (ticker)** | Parte de la propiedad de una empresa que se compra y vende en bolsa. El *ticker* es su clave: AAPL = Apple | Las 7 acciones del TT |
| **Ajuste por splits y dividendos** | Corrección de los precios históricos para que una división de acciones (*split*) o el pago de un dividendo no parezcan una caída de precio. Yahoo lo hace con `auto_adjust=True` | Descarga de datos |
| **Buy & hold (comprar y mantener)** | Estrategia de referencia: comprar el primer día y no hacer nada. Sirve para comparar si el modelo agrega valor | Plataforma, análisis 2026 |
| **Cierre (Close)** | Último precio del día de mercado. Es el precio que se usa para todo | Etiqueta y variables |
| **Corto (posición corta, *short*)** | Vender una acción prestada para recomprarla más barata. Ganas si el precio baja. En el TT, VENDER = corto | Simulación económica |
| **Costos de transacción / puntos base (pb)** | Lo que cuesta cada operación (comisión, diferencia compra-venta). 1 pb = 0.01 %. Se evaluó con 5 y 10 pb | Etapa 4, A7 |
| **Deslizamiento (*slippage*)** | Diferencia entre el precio que querías y el que obtuviste al ejecutar. No se modela | Limitaciones |
| **Drawdown** | Caída desde el punto más alto de tu capital. *Máximo drawdown* = la peor caída del periodo | Métricas económicas |
| **ETF** | Fondo que cotiza en bolsa y replica un índice. SPY replica al S&P 500 | Contexto de mercado |
| **Hipótesis de mercado eficiente (EMH)** | Idea de Fama (1970): el precio ya refleja la información disponible, así que el pasado no predice el futuro. En su forma débil, los precios pasados no sirven. Es la "hipótesis nula" de fondo del TT | Marco teórico, defensa |
| **Largo (posición larga, *long*)** | Comprar la acción; ganas si sube. COMPRAR = largo | Simulación |
| **Liquidez** | Facilidad de comprar o vender sin mover el precio. Las 7 acciones son muy líquidas | Elección de acciones |
| **NYSE / Nasdaq** | Bolsas de Nueva York. Horario regular 9:30–16:00 hora de Nueva York | API (estado del mercado) |
| **OHLCV** | *Open, High, Low, Close, Volume*: apertura, máximo, mínimo, cierre y volumen de un día. Son los 5 datos crudos | Todo el TT |
| **Régimen de mercado** | Periodo con comportamiento parecido: alcista, bajista, tranquilo, agitado | Etiqueta, análisis de MANTENER |
| **Retorno logarítmico** | `ln(P_hoy / P_ayer)`. Parecido al cambio porcentual, pero se puede sumar día con día y es simétrico | Etiqueta y variables |
| **S&P 500 / SPY** | Índice de las 500 empresas más grandes de EE. UU. / el fondo que lo replica. Representa "el mercado" | Contexto de mercado |
| **Sesgo de supervivencia** | Estudiar solo empresas que sobrevivieron y crecieron; las que quebraron no están. Las 7 acciones son sobrevivientes | Limitaciones |
| **Vela (japonesa)** | Representación gráfica de un día con OHLC: el *cuerpo* va de apertura a cierre y las *sombras* (mechas) llegan al máximo y mínimo | Variables de vela |
| **VIX** | "Índice del miedo": volatilidad que el mercado de opciones espera para el S&P 500 en los próximos 30 días. Alto = nerviosismo | Contexto de mercado; explica el exceso de MANTENER |
| **Volatilidad** | Qué tanto se mueve el precio. Se mide con la desviación estándar de los retornos | Variables, etiqueta |
| **Volatilidad agrupada** | Los días agitados vienen seguidos de días agitados. Por eso la *magnitud* del movimiento es algo predecible y la *dirección* no | Explicación del exceso de MANTENER |

## 2. Indicadores técnicos

Las 61 variables se explican una por una en [A2](A_modelo/A2_VARIABLES.md).
Aquí solo los nombres que más se repiten:

| Término | Qué es |
|---|---|
| **ATR (Average True Range)** | Rango promedio de movimiento diario en 14 días, incluyendo saltos entre cierre y apertura |
| **CMF (Chaikin Money Flow)** | Presión compradora o vendedora ponderada por volumen en 20 días |
| **EMA (media móvil exponencial)** | Promedio que da más peso a los días recientes |
| **Golden cross / death cross** | La media de 50 días cruza por arriba / por abajo a la de 200 días; señal clásica alcista / bajista |
| **MA / SMA (media móvil simple)** | Promedio de los últimos *n* cierres |
| **MACD** | Diferencia entre la EMA de 12 y la de 26 días; su EMA de 9 días es la "línea de señal" |
| **MFI (Money Flow Index)** | Como el RSI, pero ponderado por volumen |
| **Momentum** | Cuánto cambió el precio en *n* días |
| **OBV (On-Balance Volume)** | Suma acumulada del volumen: suma en días de subida, resta en días de bajada |
| **RSI (Relative Strength Index)** | De 0 a 100: compara subidas contra bajadas recientes. >70 "sobrecomprado", <30 "sobrevendido" |
| **Estocástico (%K, %D)** | Dónde está el cierre dentro del rango máximo-mínimo de 14 días |
| **VWAP** | Precio promedio ponderado por volumen |
| **Williams %R** | Como el estocástico, en escala de −100 a 0 |

## 3. Datos y preparación

| Término | Qué es | Dónde aparece |
|---|---|---|
| **Dataset** | La tabla con todas las filas (un día de una acción) y columnas (variables + etiqueta) | `tesis_ml_stocks/01_raw_datasets/` |
| **Escalado (normalización)** | Poner las variables en escalas comparables. Se ajusta **solo con entrenamiento** | Antes de entrenar |
| **Etiqueta (*target*, *ground truth*)** | La respuesta correcta que el modelo debe aprender: COMPRAR / MANTENER / VENDER | A1 |
| **Fuga de información (*data leakage*, *look-ahead bias*)** | Que el modelo use, sin querer, información que no existiría en el momento de decidir (por ejemplo, datos del futuro). Infla los resultados | Todo el protocolo |
| **Horizonte** | Cuántos días hacia adelante se predice. Aquí, 1 | Etiqueta |
| **Interacción (variable de)** | Producto de dos variables (`a × b`). Permite a un modelo lineal representar que el efecto de una depende de la otra | 15 interacciones de producción |
| **Lookback (ventana)** | Cuántos días hacia atrás lee una red neuronal | LSTM, CNN |
| **MinMaxScaler** | Escala cada variable al rango [0, 1] usando mínimo y máximo | Redes en la Etapa 3 |
| **Percentil móvil** | El valor que deja abajo cierto porcentaje de los datos de una ventana que se va moviendo (aquí, el último año) | Etiqueta |
| **RobustScaler** | Resta la mediana y divide entre el rango intercuartílico (percentil 75 − percentil 25). No lo distorsionan los días extremos | Modelo de producción |
| **`shift(1)`** | Desplazar una serie un día. Se usa para que el umbral de la etiqueta del día *t* use solo días anteriores | Etiqueta |
| **StandardScaler** | Resta la media y divide entre la desviación estándar | LR en la Etapa 3, XGBoost |
| **Variable (*feature*, característica)** | Cada dato que el modelo usa para decidir (RSI, retorno de 5 días…) | 61 + 15 |

## 3b. Metodología y proceso (TT1)

| Término | Qué es |
|---|---|
| **CRISP-DM** | *Cross-Industry Standard Process for Data Mining*: 6 fases (comprensión del negocio, comprensión de los datos, preparación, modelado, evaluación, despliegue) que permiten volver a fases anteriores. Es la metodología del TT (TT1 §3) |
| **SCRUM** | Marco ágil para organizar el trabajo en *sprints* (iteraciones cortas con objetivos). En el TT organiza la ejecución de las fases de CRISP-DM |
| **ETL / ELT** | *Extract, Transform, Load*: extraer los datos, transformarlos (variables, modelo) y cargarlos en la base. ELT carga primero y transforma dentro de la base; aquí la transformación necesita Python, por eso es ETL |
| **ACID** | Propiedades de una transacción: atómica, consistente, aislada y durable. SQLite y PostgreSQL las cumplen |
| **JSONB** | Tipo de dato de PostgreSQL para guardar JSON indexable. El TT1 lo planeaba para la matriz de confusión |
| **Caso de uso** | Descripción de una interacción del usuario con el sistema (CU-01 consultar señales, CU-02 detalle, CU-03 rendimiento) |
| **Requerimiento no funcional** | Cualidad que debe cumplir el sistema (tiempo de carga, compatibilidad, diseño responsivo), no una función |
| **Línea base ingenua** | Modelo que no aprende: clase mayoritaria o aleatorio estratificado. Sirve de piso mínimo |
| **One-vs-rest** | Resolver un problema de K clases con K clasificadores binarios (cada clase contra las demás). Así era la LR del TT1; la final es multinomial |
| **Ablación** | Quitar una parte de un modelo para medir cuánto aporta (la CNN 1D del TT1 era la CNN-LSTM sin el bloque LSTM) |
| **F1 ponderado** | Promedio del F1 de cada clase ponderado por su frecuencia (el TT1 lo reportaba como complemento) |
| **Razón de Calmar** | Retorno anualizado ÷ máximo drawdown (el TT1 la planeaba en métricas mensuales) |
| **Magnificent 7** | Nombre que se da a AAPL, MSFT, GOOGL, AMZN, NVDA, META y TSLA |

## 4. Aprendizaje automático (general)

| Término | Qué es |
|---|---|
| **Argmax** | Elegir la clase con mayor probabilidad |
| **Clasificación multiclase** | Asignar cada caso a una de varias clases (aquí 3) |
| **Época** | Una pasada completa por todos los datos de entrenamiento (redes neuronales) |
| **Hiperparámetro** | Ajuste que no se aprende de los datos sino que se elige antes (C, número de árboles, capas…) |
| **Modelo global** | Un solo modelo entrenado con las 7 acciones juntas |
| **Modelo por acción (*per ticker*)** | Un modelo distinto para cada acción |
| **Parámetro** | Número que el modelo aprende de los datos (coeficientes, pesos de la red) |
| **Pesos de clase** | Cuánto cuenta cada clase en la pérdida. "balanced" = inversamente proporcional a su frecuencia: `n / (3 · n_clase)` |
| **Pérdida (*loss*)** | Número que mide qué tan mal predice el modelo; el entrenamiento la minimiza |
| **Regularización** | Penalizar la complejidad del modelo para que no memorice ruido |
| **Semilla (*seed*)** | Número que fija el azar para que un resultado se pueda repetir. Se promedian varias semillas para reducir la varianza |
| **Sesgo–varianza** | Un modelo simple se equivoca de forma sistemática (sesgo); uno complejo cambia mucho según los datos (varianza). Con poca señal, conviene aceptar sesgo para bajar varianza |
| **Sobreajuste (*overfitting*)** | Aprender los datos de entrenamiento tan bien (incluido su ruido) que falla con datos nuevos |
| **Softmax** | Convierte 3 puntajes en 3 probabilidades que suman 1: `p_k = e^{z_k} / Σ e^{z_j}` |
| **Voto suave (*soft voting*)** | Promediar las probabilidades de varios modelos o semillas y elegir el argmax |

## 5. Modelos

| Término | Qué es |
|---|---|
| **Árbol de decisión** | Serie de preguntas sí/no ("¿RSI > 65?") que termina en una predicción |
| **Boosting / gradient boosting** | Entrenar árboles uno tras otro, cada uno corrigiendo los errores de los anteriores |
| **C (en la LR)** | Inverso de la fuerza de la regularización: C chico = regularización fuerte. Producción: 0.000165 |
| **Elasticnet** | Mezcla de penalizaciones L1 y L2 |
| **L1 (Lasso)** | Penaliza la suma de valores absolutos de los coeficientes; vuelve algunos exactamente 0 |
| **L2 (Ridge)** | Penaliza la suma de cuadrados; encoge todos los coeficientes sin volverlos 0 |
| **LightGBM** | Otra biblioteca de gradient boosting; se probó y dio lo mismo que XGBoost |
| **lbfgs / SAGA** | Algoritmos para resolver la Regresión Logística. Con L2 llegan al mismo óptimo (el problema es convexo); SAGA además soporta L1 y elasticnet |
| **Regresión Logística multinomial** | Modelo lineal: un puntaje por clase (`β_k · x + b_k`) convertido en probabilidad con softmax |
| **XGBoost** | Implementación de gradient boosting con regularización incorporada. Muy usada para datos tabulares |

## 6. Redes neuronales

| Término | Qué es |
|---|---|
| **AdamW** | Optimizador que ajusta los pesos de la red; incluye *weight decay* |
| **Atención (*attention pooling*)** | Combinar todos los pasos de una secuencia con pesos aprendidos, en vez de tomar solo el último |
| **BatchNorm** | Normaliza las activaciones dentro de cada lote; estabiliza el entrenamiento |
| **Bidireccional** | LSTM que lee la secuencia hacia adelante y hacia atrás |
| **CNN 1D (convolucional)** | Red que pasa filtros a lo largo del tiempo para detectar patrones locales (por ejemplo, de 3 a 7 días) |
| **CNN-LSTM** | Primero convoluciones (patrones locales), luego LSTM (orden temporal) |
| **Capa densa (lineal)** | Cada salida es una combinación de todas las entradas |
| **Dropout** | Apagar al azar una fracción de neuronas durante el entrenamiento para que la red no dependa de ninguna en particular |
| **Early stopping** | Detener el entrenamiento cuando la validación deja de mejorar (paciencia = cuántas épocas esperar) |
| **Focal loss** | Variante de la entropía cruzada que da menos peso a los ejemplos fáciles: `−(1−p)^γ log p` |
| **Gradient clipping** | Limitar el tamaño de los gradientes para que el entrenamiento no explote |
| **Kernel** | Tamaño del filtro de una convolución (en días) |
| **Label smoothing** | Suavizar la etiqueta (por ejemplo, 0.9 en la correcta y 0.05 en las otras) para que la red no se confíe de más |
| **LayerNorm** | Normaliza el vector de cada ejemplo; se usa antes de la capa de salida |
| **LSTM** | Red recurrente con "memoria" controlada por compuertas (olvido, entrada, salida). Lee una secuencia día por día |
| **ln 3 ≈ 1.0986** | Pérdida de un modelo que dice 1/3 para cada clase, es decir, el azar. Las redes nunca bajaron de ahí en validación |
| **Pooling (GAP, GMP)** | Resumir una secuencia en un vector: promedio global (GAP) o máximo global (GMP) |
| **ReduceLROnPlateau / Cosine** | Formas de bajar la tasa de aprendizaje durante el entrenamiento |
| **ReLU** | Función de activación `max(0, x)` |
| **Tasa de aprendizaje (*learning rate*)** | Tamaño del paso con el que se ajustan los pesos |
| **Weight decay** | Penalización L2 sobre los pesos de la red |

## 7. Métricas

| Término | Qué es | Valor de referencia |
|---|---|---|
| **Accuracy (exactitud)** | % de aciertos. Engañosa aquí: decir siempre MANTENER da ~42 % | No se usa como principal |
| **F1 (por clase)** | Media armónica de precisión y *recall* de una clase | |
| **F1-macro** | Promedio simple del F1 de las 3 clases. **Métrica principal** | Azar ≈ 0.33; siempre MANTENER ≈ 0.20 |
| **Kappa de Cohen (κ)** | Acuerdo entre predicción y realidad descontando el que habría por azar | 0 = azar, 1 = perfecto; <0.20 "leve" |
| **Matriz de confusión** | Tabla real × predicho: dónde acierta y dónde se confunde | |
| **Precisión (*precision*)** | De los que el modelo dijo COMPRAR, cuántos eran COMPRAR | |
| **Profit factor** | Suma de ganancias ÷ suma de pérdidas | >1 gana |
| **Recall (sensibilidad)** | De los que eran COMPRAR, cuántos detectó el modelo | |
| **Rotación (*turnover*)** | Cuánto cambia la posición de un día a otro; más rotación = más costos | LR 0.38, XGBoost 0.65 |
| **Sharpe anualizado** | `√252 · media(retornos) / desviación(retornos)`. Ganancia por unidad de riesgo | >0 gana, >1 bueno |
| **Win rate** | % de días con posición que ganaron | 50 % = azar |

## 8. Estadística y validación

| Término | Qué es |
|---|---|
| **Bootstrap por bloques** | Remuestrear bloques de días consecutivos (20) muchas veces (2 000) para estimar un intervalo de confianza respetando que los días están correlacionados |
| **Data snooping / winner's curse** | Si pruebas muchas variantes sobre el mismo año y te quedas con la mejor, esa "mejora" puede ser suerte |
| **Experimento A / B / C** | Tres divisiones de los datos con el mismo año de prueba (2025) y 10, 6 o 4 años de entrenamiento. B es el principal |
| **Fuera de muestra (*out-of-sample*)** | Datos que el modelo no usó para entrenar ni para tomar decisiones |
| **Intervalo de confianza 95 %** | Rango donde, con 95 % de confianza, está el valor real de la métrica |
| **Modo dev / modo final (Etapa 4)** | dev: entrena 2018–2022, elige época en 2023 y configuración en 2024. final: entrena 2018–2023, elige época en 2024 y evalúa 2025 **una vez** |
| **Optuna / TPE** | Biblioteca que busca hiperparámetros aprendiendo de los intentos anteriores (TPE = *Tree-structured Parzen Estimator*) |
| **Origen rodante (*rolling origin*)** | Para cada año Y: entrenar con los años anteriores y probar en Y; repetir para varios años |
| **Poda (*pruning*, MedianPruner)** | Abandonar un intento de Optuna que va peor que la mediana de los anteriores |
| **Prueba de permutación** | Barajar las señales del modelo muchas veces para ver qué tan seguido el azar iguala su resultado |
| **Prueba de signo / Wilcoxon** | Pruebas para comparar pares (por ejemplo, global contra por acción en la misma acción) |
| **Purga / embargo** | Técnicas de López de Prado para quitar del entrenamiento observaciones cuya etiqueta se traslapa con la prueba |
| **Test / prueba** | Datos que solo se usan al final para medir |
| **Validación** | Datos para elegir hiperparámetros y época; no para reportar |
| **Prueba año por año** (*walk-forward*) | Repetir entrenamiento–validación–prueba moviendo la ventana un año cada vez (aquí, prueba 2020…2025, entrenando con los 5 años previos al de validación) |

## 9. Software y sistema

| Término | Qué es | En el TT |
|---|---|---|
| **API REST** | Servicio que responde peticiones HTTP con datos (JSON) | `api/main.py` |
| **APScheduler** | Biblioteca para programar tareas dentro del proceso (por ejemplo, cada día a las 16:30) | Actualización diaria |
| **Blueprint (Render)** | Archivo que describe los servicios a desplegar | `render.yaml` |
| **CORS** | Permiso para que una página de otro dominio llame a la API | `flask-cors` |
| **Docker / contenedor** | Empaqueta la aplicación con todo lo que necesita para correr igual en cualquier lado | `api/Dockerfile` |
| **Endpoint** | Una dirección de la API (`GET /stocks`) | B2 |
| **Flask** | Framework web ligero de Python | Backend |
| **Formas normales (1FN, 2FN, 3FN)** | Reglas de diseño de bases de datos para evitar datos repetidos e inconsistencias | B3 |
| **gunicorn** | Servidor de producción para aplicaciones Python web | Render |
| **Health check** | Endpoint que dice si el servicio está vivo (`/health`) | Render |
| **JSON** | Formato de texto para intercambiar datos | Respuestas de la API |
| **ORM / SQLAlchemy** | Biblioteca que traduce clases de Python a tablas de la base de datos | `api/models.py` |
| **`.pkl` (pickle)** | Archivo con el modelo entrenado guardado | `api/ml/artifacts/` |
| **React / TypeScript / Vite / Tailwind** | Biblioteca de interfaces / JavaScript con tipos / herramienta de compilación / estilos por clases | Frontend |
| **Render** | Plataforma en la nube donde está desplegado el sistema | B5 |
| **SPA** | Aplicación de una sola página: el navegador cambia de vista sin recargar | Frontend |
| **SQLite** | Base de datos en un solo archivo, sin servidor | B3 |
| **Upsert** | "Insertar o actualizar": si la fila existe se actualiza, si no se crea | `api/db_ops.py` |

## 10. Nombres propios del proyecto

| Término | Qué es |
|---|---|
| **Etapa (1 a 6)** | Cada vuelta de trabajo del proyecto: 1 línea base (TT1), 2 primeras mejoras, 3 comparación en igualdad, 4 protocolo final, 5 búsqueda de mejoras, 6 plataforma y validación. Ver el [mapa](03_MAPA_DE_EXPERIMENTOS.md) |
| **v1 … v8** | Nombres viejos de las corridas; equivalencias en el [mapa](03_MAPA_DE_EXPERIMENTOS.md#7-equivalencias-con-el-repositorio). No hubo v6 |
| **Experimento A / B / C** | Las tres formas de dividir los años (10, 6 y 4 años de entrenamiento; prueba 2025). No son etapas |
| **Pasos 4.1 a 4.7** | Pasos internos de la Etapa 4 (replicación, decisiones de protocolo, Optuna, costos, intervalos). Antes se llamaban V0–V6 |
| **Vía 7 / Vía 8** | Nombres viejos de las dos partes de la Etapa 5: ajustes al modelo y variables nuevas |
| **Exp B global** | Configuración principal: entrenamiento 2018–2023, validación 2024, prueba 2025, un modelo para las 7 acciones |
| **`LR-v8-interactions-holdw090`** | Nombre del modelo en producción: LR + interacciones de la Etapa 5, peso de MANTENER × 0.90 |
| **Voto dividido** | Explicación del exceso de MANTENER: la probabilidad de movimiento se reparte entre COMPRAR y VENDER |
| **`MODEL_VERSION`** | Constante en `api/ml/model.py` que debe coincidir con el `.pkl` (hay una prueba que lo verifica) |
| **MICAI** | *Mexican International Conference on Artificial Intelligence*; publica en LNAI de Springer |
| **Camera-ready** | Versión final de un paper aceptado, lista para imprenta |
