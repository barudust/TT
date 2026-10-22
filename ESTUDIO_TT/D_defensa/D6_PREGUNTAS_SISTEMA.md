# D6 — Preguntas del sistema: arquitectura, API, base de datos, frontend y despliegue

> Respuesta corta = lo que dices. Detalle en la [parte B](../B_sistema/B1_ARQUITECTURA.md).

---

## Arquitectura

### S1. Describa la arquitectura del sistema.

**Respuesta corta.** Dos partes. **Fuera de línea**, el pipeline de
investigación en Python construye el dataset, entrena y compara los modelos
y produce un archivo `.pkl` con el ganador. **En línea**, una API en Flask
descarga cada día los datos de Yahoo Finance, calcula las 76 variables con el
mismo código del entrenamiento, corre el modelo, evalúa cada señal contra el
día siguiente, guarda todo en SQLite y lo sirve en JSON; una aplicación web
en React lo muestra. La API corre en Docker en
Render y el frontend como sitio estático; se despliegan solos con cada
cambio en la rama `main`.

### S2. ¿Por qué separar el entrenamiento de la API?

**Respuesta corta.** Entrenar es pesado (GPU, búsquedas de horas) y se hace
pocas veces; servir es ligero y diario. La API solo necesita el modelo
entrenado (`.pkl`) y el código de las variables. Además, así el servidor de
producción no necesita GPU ni las bibliotecas de redes neuronales.

### S3. ¿Cómo garantizan que la API use el modelo correctamente?

**Respuesta corta.** (1) El cálculo de variables es una copia exacta del de
entrenamiento, con pruebas; (2) el `.pkl` guarda el modelo, el escalador y la
lista exacta de variables, y la API falla al arrancar si falta alguna; (3)
`MODEL_VERSION` debe coincidir con el `.pkl` (hay una prueba); (4) la
etiqueta en vivo coincide al 100 % con la del entrenamiento (otra prueba);
(5) `GET /model` describe el modelo leyendo el `.pkl`, no un texto fijo.

### S4. ¿Qué patrón o estilo arquitectónico siguen?

**Respuesta corta.** Cliente-servidor con una API REST: el frontend (SPA) es
el cliente y la API el servidor, comunicándose por HTTP/JSON sin estado. La
API está organizada en capas: rutas (`main.py`), lógica del modelo
(`ml/`), acceso a datos (`db_ops.py`, `models.py`). Y un proceso por lotes
programado (la actualización diaria) que precalcula todo, de modo que las
peticiones solo leen resultados.

---

## API

### S5. ¿Por qué Flask y no FastAPI o Django?

**Respuesta corta.** La API tiene una decena de rutas, casi todas de
lectura, sin usuarios ni administración: Flask es mínimo y suficiente.
Django traería ORM, administración y autenticación que no se usan. FastAPI
sería igual de válido (validación y documentación automáticas), pero el
proyecto ya estaba en Flask desde su primera versión y migrar no aportaba
nada al objetivo.

### S6. ¿Qué endpoints tiene?

**Respuesta corta.** De lectura: `/health`, `/model`, `/market-status`,
`/stocks`, `/stocks/:símbolo`, `/stocks/:símbolo/history?days=`,
`/stocks/:símbolo/metrics?days=`, `/metrics?days=` y
`/stocks/:símbolo/info`. De escritura: `POST /admin/refresh` para forzar la
actualización; los de escritura manual existen pero están desactivados
(responden 403) para que todo lo mostrado salga del modelo.

### S7. ¿Cómo y cuándo se actualizan los datos?

**Respuesta corta.** Un programador de tareas dentro de la API (APScheduler)
corre la actualización de lunes a viernes a las 16:30 de Nueva York (30 min
después del cierre, para que Yahoo publique), al arrancar el servidor, y cada
2 minutos si falta alguna acción. Cada actualización recalcula toda la
ventana de ~3 años.

### S8. ¿Por qué recalcular todo y no solo el día nuevo?

**Respuesta corta.** Cuesta segundos y garantiza que todo lo mostrado sale
del modelo vigente: si se reentrena, la historia se actualiza sola. Además
hace que la base de datos sea reconstruible en cualquier momento.

### S9. ¿Qué pasa si Yahoo Finance falla?

**Respuesta corta.** Cada descarga se reintenta 3 veces con 5 segundos de
espera. Si aun así falla una acción, se omite (nunca se inventan datos); y el
programador reintenta cada 2 minutos hasta completar las 7. `/health`
reporta cuántas están cargadas. Esto se diseñó después de que, en un
despliegue real, Yahoo falló en el arranque y el catálogo quedó vacío; con
el reintento se reparó solo en ~2 minutos.

### S10. ¿Cómo evitan usar información del futuro en vivo?

**Respuesta corta.** Mientras NYSE está abierto, Yahoo devuelve la vela del
día con un precio intermedio como "cierre"; esa fila se descarta hasta el
cierre. Y el acierto de una señal solo se calcula cuando existe el cierre del
día siguiente; antes aparece como "pendiente".

### S11. ¿Las métricas de la plataforma son las mismas que las de la tesis?

**Respuesta corta.** Sí. Cada señal se compara con el movimiento del cierre
de ese día al siguiente usando la misma etiqueta (percentiles 30/70 de 252
días), y la simulación es la misma: COMPRAR largo, VENDER corto, MANTENER
fuera, un día, sin costos. Lo verificamos en una auditoría el 30 de
septiembre, donde corregimos errores de versiones anteriores (por ejemplo,
"correcta" se comparaba contra el día anterior y el Sharpe se calculaba sobre
el precio de la acción).

### S12. ¿Cómo probaron la API?

**Respuesta corta.** 24 pruebas automáticas con pytest: cálculo de
variables (RSI acotado, retornos, calentamiento), carga y forma de la
predicción del modelo, versión del modelo, métricas con valores conocidos,
evaluación contra el día siguiente, coincidencia de la etiqueta en vivo con
la del entrenamiento, horario y feriados de NYSE, descarte de la vela en
curso, reintentos, endpoints desactivados y una corrida completa sin red con
datos simulados.

### S13. ¿Y la seguridad?

**Respuesta corta.** La API es pública y de solo lectura con datos
públicos, así que el riesgo es bajo. Los secretos van en variables de
entorno (no en el código); la escritura manual está desactivada; Render da
HTTPS. Pendientes que reconocemos: CORS abierto y `POST /admin/refresh` sin
autenticación (solo recalcula con datos públicos, pero convendría una
llave).

---

## Base de datos

### S14. ¿Qué base de datos usan y por qué?

**Respuesta corta.** SQLite, a través de SQLAlchemy. Los datos son pocos
(miles de filas), hay un solo escritor (la actualización diaria) y todo se
puede regenerar desde Yahoo y el modelo, así que no hace falta un servidor de
base de datos. Como usamos SQLAlchemy con tipos genéricos, cambiar a
PostgreSQL es cambiar la variable `DATABASE_URL`; el `docker-compose` ya
tiene un perfil con PostgreSQL 15.

### S15. ¿Por qué relacional y no NoSQL (por ejemplo MongoDB)?

**Respuesta corta.** Los datos tienen estructura fija y relaciones claras
(una acción tiene muchos precios, señales y métricas), y nos interesan
restricciones de integridad (llaves foráneas, unicidad por acción y fecha).
Eso es justo lo que da el modelo relacional; un almacén de documentos no
aporta nada aquí.

### S16. Describa el esquema.

**Respuesta corta.** Cuatro tablas: `assets` (acciones), `ohlcv_daily`
(precio por acción y día, único por acción + fecha), `predictions` (señal,
tres probabilidades, confianza, si acertó y versión del modelo, única por
acción + fecha) y `metrics` (métricas por acción y ventana de 30/60/90 días,
única por acción + ventana). Las tres últimas tienen llave foránea a
`assets` con borrado en cascada.

### S17. ¿Está normalizada?

**Respuesta corta.** Está en primera y segunda forma normal. Las tablas de
datos base están en tercera forma normal (`ohlcv_daily` sí; en `assets`,
sector depende de industria, una dependencia transitiva menor). Las tablas
de señales y métricas tienen **columnas derivadas a propósito**: la
confianza es el máximo de las probabilidades, `actual_price` repite el
cierre, `correct` se deriva del día siguiente y `metrics` es un agregado.

**Por qué es aceptable:** la normalización evita anomalías de
actualización, y aquí no pueden ocurrir: un solo proceso escribe y recalcula
todo desde la fuente en cada pasada, nadie edita filas a mano. Esas columnas
funcionan como registro de lo que la plataforma calculó y mostró con cada
versión del modelo (auditoría), y simplifican la lectura. Es la
desnormalización típica de tablas de hechos y agregados.

**Si piden llevarla a 3FN:** tabla de industrias/sectores, tabla de
versiones de modelo con llave foránea, quitar `confidence` y `actual_price`
(obtenerlas con una consulta) y convertir `metrics` y `correct` en vistas.

### S18. ¿Para qué sirve la base si la API responde desde memoria?

**Respuesta corta.** La memoria es la ruta rápida de lectura; la base es el
registro persistente: guarda la historia entre reinicios, permite auditar
qué señal dio cada versión del modelo con qué probabilidades, y permite
consultas SQL para análisis. Si se escalara a varios procesos, leer de la
base en vez de la memoria de cada proceso sería el siguiente paso.

### S19. En Render la base se borra al reiniciar. ¿No es un problema?

**Respuesta corta.** No, porque no es la fuente de verdad: la fuente de
verdad son los datos de Yahoo y el modelo versionado, y la base se
reconstruye completa en cada arranque. En el plan gratuito no hay disco
persistente; en local con Docker se monta un volumen y persiste; y con
PostgreSQL o un disco de pago persistiría sin cambiar código.

### S20. ¿Por qué no guardan las 76 variables en la base?

**Respuesta corta.** Se calculan en menos de un segundo a partir de los
precios guardados; almacenarlas sería redundante y obligaría a mantenerlas
sincronizadas con el código de las fórmulas.

---

## Frontend

### S21. ¿Qué tecnologías usa el frontend y por qué?

**Respuesta corta.** React 18 con TypeScript, compilado con Vite, estilos
con Tailwind CSS y gráficas con Recharts. React por componentes
reutilizables; TypeScript porque los tipos de las respuestas de la API
detectan errores antes de ejecutar; Vite por compilación rápida a archivos
estáticos; Tailwind por consistencia y modo oscuro sin hojas de estilo
enormes.

### S24. ¿Qué pantallas tiene?

**Respuesta corta.** Seis: **Hoy** (una tarjeta por empresa con su
recomendación, precio y seguridad en palabras); **detalle** de cada empresa
(recomendación, probabilidades, gráfica de precio con la recomendación de
cada día, gráfica de qué habría pasado con $1,000, resultados de 30/60/90
días y últimas 10 recomendaciones); **Resultados** (las 7 empresas
comparadas); **Aprende** (qué es comprar, vender en corto y mantener, con
ejemplos que se mueven y un juego día por día con precios reales); **Ayuda**
(guía de uso y glosario) y **Acerca de** (metodología, ficha del modelo leída
de la API, aviso legal).

### S25. ¿Cómo comunican la incertidumbre al usuario?

**Respuesta corta.** Mostramos las tres probabilidades y aclaramos que el
azar es 33 %; el resultado de cada señal contra lo que realmente pasó; el
F1 contra la línea del azar; comprar y mantener como referencia; el Sharpe
no se muestra con menos de 5 operaciones; y un aviso legal de que no es
recomendación de inversión.

---

## Despliegue

### S26. ¿Cómo está desplegado?

**Respuesta corta.** En Render, definido en `render.yaml`: la API como
servicio web en un contenedor Docker con gunicorn (1 worker, 1 instancia) y
el frontend como sitio estático. Cada `push` a la rama `main` de GitHub
despliega automáticamente. Después de desplegar se verifica `/health`
(7 acciones cargadas) y `/model` (versión del modelo).

### S27. ¿Por qué Docker?

**Respuesta corta.** Para que la API corra igual en local y en la nube, con
las mismas versiones de todo; en particular scikit-learn 1.7.2, la misma
con la que se entrenó, porque un `.pkl` puede no cargar en otra versión.

### S28. ¿Por qué un solo worker? ¿No limita la escalabilidad?

**Respuesta corta.** El programador de tareas vive dentro del proceso; con N
workers la actualización correría N veces. Para una API de lectura con pocos
usuarios un worker basta. Para escalar, sacaríamos la actualización a un
*cron job* externo que llame `POST /admin/refresh` una vez, y entonces sí
varios workers o instancias.

### S29. ¿Qué limitaciones tiene el plan gratuito y cómo las manejan?

**Respuesta corta.** El servicio se duerme tras ~15 minutos sin tráfico: la
primera petición tarda 20–40 s (lo mostramos como carga). La actualización
diaria solo corre si está despierto a esa hora; la solución sería un plan
pago o un cron externo. La base es efímera, lo cual es aceptable porque se
reconstruye.

### S30. ¿Cómo manejan el control de versiones?

**Respuesta corta.** Git con GitHub (`barudust/TT`): `main` es la rama que
se despliega y `dev` la de trabajo; las ramas personales se fusionaron y
eliminaron. Los commits son descriptivos y el historial documenta la
evolución del proyecto. El modelo también está versionado
(`MODEL_VERSION`).

---

## Cambios respecto al TT1

### ST1. En TT1 justificaron PostgreSQL sobre SQLite. ¿Por qué cambiaron?

**Respuesta corta.** Las razones del TT1 dejaron de aplicar. El TT1 eligió
PostgreSQL porque el ETL y la API eran dos procesos escribiendo y leyendo a
la vez, y SQLite no está diseñado para varios escritores concurrentes; ahora
el ETL corre dentro del proceso de la API, hay un solo escritor protegido por
un candado y las lecturas salen de memoria. La segunda razón era JSONB para
la matriz de confusión, que ya no se guarda. La tercera, los índices
compuestos, también los tiene SQLite con las restricciones únicas por
acción y fecha. Además la base ahora se reconstruye completa desde Yahoo y
el modelo, y el plan gratuito de Render no ofrece PostgreSQL permanente.
El esquema sigue siendo compatible: volver a PostgreSQL es cambiar una
variable de entorno.

### ST2. El TT1 tenía 9 tablas. ¿Dónde quedaron?

**Respuesta corta.** Se conservaron `assets`, `ohlcv_daily` y
`predictions`. `features_daily` se eliminó porque las variables se
recalculan en menos de un segundo. `daily_returns`, las métricas semanales
y mensuales y `snapshots_90d` se sustituyeron por una sola tabla `metrics`
con ventanas móviles de 30, 60 y 90 días, que además cumple el papel de la
tabla desnormalizada que el TT1 ya justificaba como vista materializada.

### ST3. En TT1 el ETL era incremental. ¿No es más eficiente que recalcular todo?

**Respuesta corta.** Sí, pero aquí recalcular todo cuesta segundos y tiene
ventajas: garantiza que todo lo mostrado sale del modelo vigente (si se
reentrena, la historia se actualiza sola), no deja estados intermedios que
reparar si un día falla la descarga, y hace la base reconstruible. Con
miles de acciones convendría volver a un esquema incremental.

### ST4. ¿Dónde están la curva de capital, la matriz de confusión y la actualización cada hora que describía el TT1?

**Respuesta corta.** La curva de capital sí está: en el detalle de cada
empresa, «¿Qué habría pasado con $1,000?», con la misma fórmula que la API
(coincide al centavo con el capital final). La matriz de confusión no se
implementó: para un usuario sin contexto se priorizó el resultado de cada
recomendación y la comparación contra el azar. La actualización cada hora no
hace falta porque la recomendación cambia una vez al día; la página pide los
datos al abrirse y tiene un botón de actualizar.

### ST4b. ¿Por qué la «confianza» aparece en palabras y no en porcentaje?

**Respuesta corta.** Porque un porcentaje como «36 %» no le dice nada a un
usuario: con tres opciones el azar es 33 % y el modelo casi nunca pasa de
45 %. Medimos qué tan seguido acierta el modelo actual según su confianza en
7 años que no había visto: 37 % en el 30 % de días menos seguros, 38 % en el
30 % siguiente y 42 % en el 40 % más seguros (azar ≈ 34 %). Con eso hicimos
tres niveles: Nada segura, Poco segura y Medianamente segura. No pusimos
«Segura» porque ningún nivel acierta ni la mitad de las veces y sería
engañoso.

### ST4c. ¿Cómo entiende un usuario sin conocimientos los términos?

**Respuesta corta.** Cada métrica tiene un «?» que lleva a su definición en
un glosario dentro de la app, escrito en lenguaje sencillo y con ejemplos; hay
una guía de uso por pantalla; los nombres técnicos se reemplazaron por
descripciones («peor caída» en vez de drawdown, «comprar y esperar» en vez de
buy & hold), dejando el nombre técnico entre paréntesis; y el rendimiento se
muestra también en dinero sobre $1,000.

### ST5. En TT1 había endpoints POST para el ETL. ¿Por qué los desactivaron?

**Respuesta corta.** Porque el ETL ya no escribe a través de la API: corre
dentro del mismo proceso. Dejarlos abiertos permitiría a cualquiera escribir
señales o métricas que no salen del modelo. Responden 403 salvo que se
activen explícitamente para pruebas locales.
