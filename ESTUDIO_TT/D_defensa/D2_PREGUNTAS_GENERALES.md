# D2 — Preguntas generales y de planteamiento

> Cada pregunta tiene una **respuesta corta** (lo que dices, 30–60 s) y, a
> veces, **si repreguntan** (el fondo). Las respuestas repiten información
> de otros documentos a propósito: cada una se entiende sola.

---

### G1. ¿De qué trata su Trabajo Terminal?

**Respuesta corta.** Comparamos cinco modelos de aprendizaje automático
—Regresión Logística, XGBoost, LSTM, CNN 1D y CNN-LSTM— para generar cada
día una señal de comprar, mantener o vender para siete acciones
tecnológicas de EE. UU., usando solo datos públicos de Yahoo Finance. El
mejor fue la Regresión Logística, y lo desplegamos en una plataforma web
que se actualiza sola cada día y mide su desempeño con la misma
metodología de la tesis.

### G2. ¿Cuál es la aportación del trabajo?

**Respuesta corta.** Cuatro cosas:
1. Una comparación de cinco familias de modelos bajo **el mismo protocolo**,
   con validación temporal estricta, búsqueda de hiperparámetros simétrica
   e intervalos de confianza; la mayoría de los trabajos compara uno o dos
   modelos.
2. Evaluación **de clasificación y económica** (Sharpe, drawdown, costos),
   no solo exactitud.
3. **Evidencia medida** de por qué las redes no superan a un modelo lineal
   aquí (no bajan del azar en validación, el tamaño no importa) y de que
   filtrar variables no ayuda (11 de 15 casos).
4. Un **sistema desplegado** que aplica el modelo con datos reales y se
   autoevalúa día con día.

Además, parte del trabajo fue aceptado en MICAI 2026 (Springer).

### G3. ¿Qué problema resuelve y para quién?

**Respuesta corta.** Da una señal diaria, explicable y evaluada con
transparencia, para apoyar la decisión de un inversionista sobre siete
acciones muy negociadas. El valor principal es metodológico: muestra cuánto
se puede predecir realmente con datos públicos diarios y qué tipo de modelo
conviene. La plataforma es demostrativa; no es una recomendación de
inversión y lo dice.

### G4. ¿Por qué es relevante para Ingeniería en Sistemas Computacionales?

**Respuesta corta.** Integra un ciclo completo de ingeniería: adquisición y
procesamiento de datos, diseño experimental y entrenamiento de modelos
(incluido cómputo en GPU), validación estadística, y un sistema en
producción con API REST, base de datos, aplicación web,
contenedores, despliegue continuo en la nube, pruebas automáticas y
manejo de fallas reales (arranque en frío, caídas del proveedor de datos).

### G5. ¿Por qué clasificación y no predecir el precio (regresión)?

**Respuesta corta.** La decisión de inversión es discreta (comprar, no
operar, vender) y el valor exacto del retorno de mañana está dominado por
ruido. Clasificar en "subida fuerte / normal / bajada fuerte" es más
aprendible y se traduce directo a una acción. Además, el error cuadrático de
una regresión no se traduce limpiamente en ganancia.

### G6. ¿Por qué tres clases y no dos (sube/baja)?

**Respuesta corta.** Porque hace falta poder **abstenerse**. Con dos clases
el modelo opera todos los días aunque no tenga información, con más costos
y riesgo. Lo medimos: forzar comprar o vender todos los días da un Sharpe
similar en 2025 pero un drawdown peor (−61 % contra −52 %) y en 2024 pierde
más. MANTENER es la "opción de rechazo" de la teoría de decisión (Chow,
1970).

### G7. ¿Por qué esas 7 acciones?

**Respuesta corta.** Son las 7 tecnológicas más grandes de EE. UU.
(~30 % del S&P 500): muy líquidas, con historia completa y sin huecos, y con
perfiles de volatilidad distintos dentro de un mismo sector (estables como
MSFT y AAPL, volátiles como TSLA y NVDA). El sector común permite entrenar un
solo modelo con las siete, que multiplica los datos por 7.

**Si repreguntan (limitaciones):** son sobrevivientes (sesgo de
supervivencia) y de un solo sector, así que no garantizamos que las
conclusiones valgan para otros sectores o mercados.

### G8. ¿Por qué solo Yahoo Finance? ¿No es poco serio?

**Respuesta corta.** Por reproducibilidad: cualquiera puede descargar los
mismos datos y repetir todo sin pagar. Para precios diarios de acciones
grandes la calidad es adecuada. Y comprobamos que agregar más series de
Yahoo (bonos, dólar, oro, petróleo, sectores) no mejora, así que el límite no
es la fuente sino la poca señal del problema.

### G9. ¿Cuál fue el resultado principal?

**Respuesta corta.** En la prueba principal (2025, protocolo corregido) la
Regresión Logística obtuvo F1-macro de 0.404 con intervalo de 95 % [0.379,
0.428] y Sharpe de +0.89, significativamente mejor que los otros cuatro
modelos. En seis años de prueba año por año la LR y XGBoost empatan alrededor de
0.35 y las redes quedan abajo. En 2026, fuera de muestra, el modelo en
producción da F1 0.354.

### G10. Un F1 de 0.40 parece bajo. ¿Es un buen resultado?

**Respuesta corta.** Para este problema sí es significativo, aunque
modesto. El azar da 0.33 y decir siempre MANTENER da 0.20. Predecir la
dirección de una acción al día siguiente con datos públicos es casi
imposible según la hipótesis de mercado eficiente; que haya una señal
estadísticamente distinguible del azar ya es un resultado. Lo importante es
que lo medimos con honestidad, incluyendo los años en que no funciona.

### G11. ¿Cumplieron los objetivos?

**Respuesta corta.** Sí. El objetivo general del TT1 era implementar y
entrenar modelos que recomienden comprar, vender o mantener, evaluarlos
contra modelos de referencia con simulación económica e integrarlos a una
aplicación web. Por objetivo específico:

1. **Analizar las arquitecturas y diseñar el pipeline** (variables,
   etiquetado multiclase, partición temporal): hecho, y corregido en la Etapa 3
   (mismas variables para todos, misma prueba en los tres experimentos).
2. **Implementar y optimizar los cinco modelos**: hecho; la optimización
   pasó de cuadrícula y redes fijas a Optuna para los cinco.
3. **Evaluar y comparar para determinar en qué condiciones el DL supera al
   ML**: hecho; en este régimen no lo supera, y explicamos en qué
   condiciones podría (más datos, entradas crudas, horizontes largos).
4. **Aplicación web** (que el TT1 dejó "en desarrollo"): terminada,
   conectada al modelo real y desplegada.

**Cuidado:** el TT1 lista 3 objetivos específicos en §1.2.2 y 4 en §5.8 (el
cuarto es la aplicación). En el documento final conviene unificarlos.

### G12. ¿Qué cambió respecto al TT1?

**Respuesta corta.** Cinco cosas principales: (1) todos los modelos reciben
ahora las mismas 61 variables en lugar de un filtro distinto por modelo;
(2) el modelo global pasó a ser el principal en lugar del modelo por
acción; (3) el experimento A prueba en 2025 como los demás; (4) la búsqueda
de hiperparámetros pasó a Optuna para los cinco, incluidas las redes, y se
agregaron intervalos de confianza, prueba año por año y evaluación en 2026; (5)
el sistema se terminó y se desplegó, con SQLite y el ETL dentro de la API
en lugar de PostgreSQL y un proceso aparte. Detalle en
[D1](D1_TT1_VS_TT2.md).

### G12b. En TT1 dijeron que ganaba XGBoost; ahora dicen que la Regresión Logística. ¿Cuál es?

**Respuesta corta.** El TT1 tenía una limitación que él mismo señaló: cada
modelo recibía distintas variables (la LR solo 3 a 8, XGBoost 23 a 25) y se
entrenaba por acción. Al corregirlo —mismas 61 variables, modelo global y
búsqueda de hiperparámetros simétrica— la LR mejora mucho (de 0.355 a 0.404)
y XGBoost no. En 2025 la LR es significativamente mejor; en seis años de
prueba año por año ambos empatan (0.350 contra 0.356). Lo que no cambió entre TT1
y TT2 es la conclusión de fondo: los modelos clásicos igualan o superan a
las redes.

### G12c. ¿Qué metodología siguieron?

**Respuesta corta.** CRISP-DM como marco del proceso (comprensión del
negocio, de los datos, preparación, modelado, evaluación y despliegue) y
SCRUM para organizar el trabajo en iteraciones. CRISP-DM permite regresar a
fases anteriores cuando una evaluación lo exige, y eso es justo lo que pasó:
cada versión etapas 1 a 6 volvió a la preparación de datos o al modelado
después de evaluar.

### G12d. ¿Cuál es la brecha que cubre su trabajo frente a la literatura?

**Respuesta corta.** Tres cosas que no encontramos juntas: (1) la mayoría
de los trabajos predicen el precio (regresión) y no una señal accionable de
tres clases; (2) ninguno compara a la vez LR, XGBoost, LSTM, CNN 1D y
CNN-LSTM con el mismo protocolo, las mismas variables y métricas de
clasificación y económicas; (3) ninguno estudia las Magnificent 7 como
universo. El más cercano, Nabipour et al. (2020), compara modelos clásicos
y redes, pero en clasificación binaria y en la bolsa de Teherán.

### G12e. ¿En qué se diferencian de herramientas comerciales como TrendSpider o Trade Ideas?

**Respuesta corta.** Esas plataformas cobran de 52 a 228 dólares al mes,
dan señales de entrada/salida sin una clase explícita de mantener, no
documentan sus modelos y no publican una evaluación económica
reproducible. Nuestra plataforma es gratuita, documenta el modelo y su
entrenamiento, muestra cómo le ha ido a cada señal y tiene la opción de no
operar.

### G13. ¿Qué parte hizo cada integrante?

**Respuesta corta.** *(Complétenlo ustedes con la división real.)* Lo que
muestra el historial del repositorio: el pipeline de investigación, la
plataforma y el paper fueron trabajo conjunto; David trabajó la calibración
de MANTENER de julio y figuras del paper, y Baruc la integración del modelo
en la API, el despliegue y la respuesta a los revisores.

> **Atención:** verifiquen y ajusten esta respuesta antes de la defensa; es
> una pregunta casi segura.

### G14. ¿Por qué tantas versiones etapas 1 a 6? ¿No tenían un plan?

**Respuesta corta.** Sí había plan, pero en investigación cada resultado
cambia la siguiente pregunta. etapas 1–2 construyeron el pipeline y probaron más
variables; la Etapa 3 hizo la comparación justa; la Etapa 4 corrigió el protocolo después de
un diagnóstico; la Etapa 5 agotó las mejoras razonables y la Etapa 6 validó el modelo de la plataforma. Que la conclusión
se mantenga a través de todas es lo que la hace creíble.

**Si preguntan por los nombres viejos (v1 … v8):** así se llamaban las corridas mientras se
trabajaba; no había v6 porque se llamó V0–V6 a los pasos internos de v5. Para el documento se
ordenaron en seis etapas ([mapa](../03_MAPA_DE_EXPERIMENTOS.md)).

### G15. ¿Qué harían con seis meses más?

**Respuesta corta.** (1) Cambiar a horizonte de 5 días, que ya medimos que
sube el F1 a ~0.43; (2) ampliar a cientos de acciones para que las redes
tengan datos suficientes; (3) agregar datos gratuitos de macroeconomía y
sentimiento de noticias; (4) optimizar con costos de transacción y tamaño
de posición por volatilidad; (5) corregir la ventana de las redes para que
incluya el último día y repetir la comparación.

### G16. ¿Usarían el modelo con su propio dinero?

**Respuesta corta.** No. El acuerdo con la realidad es leve (kappa 0.035 en
2026), el Sharpe de un año tiene un error estándar cercano a 1 y no
modelamos deslizamiento ni tamaño de posición. La plataforma es
demostrativa y tiene un aviso legal. El aporte es saber con rigor cuánto se
puede predecir y con qué modelo.
