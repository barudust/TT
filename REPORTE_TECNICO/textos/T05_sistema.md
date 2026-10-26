# T05 — Sistema: borradores del capítulo 5

> Borradores para reescribir el capítulo 5 con el sistema real. Fuentes:
> `ESTUDIO_TT/B_sistema/B1`–`B5`, `docs/`. Figuras `diagramas/D01`–`D07`.
> Lo que ya está bien en el documento (justificación de Flask y React,
> lecciones de pruebas e integración) se conserva con tono impersonal.

---

## 1. Introducción del capítulo

Este capítulo describe la plataforma web que pone en operación el modelo
seleccionado. Cada día hábil, después del cierre del mercado, la plataforma
descarga los datos de las siete acciones y del contexto de mercado, calcula
las 76 características con el mismo código usado en el entrenamiento,
obtiene la recomendación del modelo para la siguiente sesión, evalúa las
recomendaciones anteriores contra lo que ocurrió y publica todo en una
aplicación web pensada para usuarios sin conocimientos de finanzas, que
incluye además la comparación de los cinco modelos evaluados. Se compone de
una API en Flask que integra la actualización diaria y una base de datos
SQLite, y de una aplicación en React; ambas están desplegadas en Render.

---

## 2. Arquitectura (5.2)

El sistema se divide en dos partes con una sola interfaz entre ellas
(Figura D01):

- **Fuera de línea (investigación).** Scripts de Python que construyen el
  conjunto de datos, comparan los cinco modelos y entrenan el modelo de
  producción. Requieren GPU y horas de búsqueda, y se ejecutan una vez.
- **En línea (plataforma).** Un servicio web que cada día descarga datos,
  calcula las características, ejecuta el modelo, evalúa sus señales y las
  sirve a la aplicación web.

Lo único que pasa de una parte a la otra es el archivo del modelo (`.pkl`,
con el escalador, la lista de características y sus metadatos) y el código
de las características, que se copió sin cambios del pipeline de
investigación y tiene pruebas automáticas que verifican que ambos producen
lo mismo. Así, la plataforma mide exactamente lo mismo que la evaluación del
trabajo.

| Componente | Tecnología | Responsabilidad |
|---|---|---|
| Investigación | Python, pandas, scikit-learn, XGBoost, PyTorch, Optuna | Datos, entrenamiento, comparación |
| Modelo | `.pkl` + `.metrics.json` + `interaction_pairs.json` | Modelo entrenado y su evidencia |
| API | Flask 3, gunicorn, APScheduler, yfinance, SQLAlchemy 2 | Actualización diaria, inferencia, evaluación, JSON |
| Base de datos | SQLite (compatible con PostgreSQL) | Registro persistente de precios, señales y métricas |
| Aplicación web | React 18, TypeScript, Vite, Tailwind CSS 4, React Router 7, Recharts | Mostrar recomendaciones, resultados y comparación |
| Despliegue | Docker, Render, GitHub | Publicar y actualizar ambos servicios |

---

## 3. Del modelo de investigación al de producción (5.3)

El modelo de producción se entrena con `scripts_opt/entrenar_produccion.py`
(Figura D02): carga las siete acciones de 2018 a 2025 (14 063 filas), agrega
las 15 interacciones, ajusta un escalador robusto con todas las filas,
calcula los pesos de clase (balanceados, con el peso de mantener × 0.90),
entrena la Regresión Logística multinomial con penalización L2 y C =
0.000165, y guarda el modelo, el escalador, la lista de las 76
características y los metadatos (hiperparámetros, rango de entrenamiento,
evidencia del ajuste) en `api/ml/artifacts/`.

La API carga ese archivo una sola vez al arrancar, verifica que contenga
todas las características esperadas (si no, se detiene, porque es preferible
fallar a predecir con datos incompletos) y expone su ficha en `GET /model`.
La versión del modelo (`LR-v8-interactions-holdw090`) se declara en el
código y una prueba automática falla si no coincide con la del archivo. El
diseño es agnóstico al modelo: para cambiarlo basta sustituir el archivo y la
versión.

---

## 4. Actualización diaria (5.4)

La actualización corre **dentro del proceso de la API**, programada con
APScheduler (Figura D03). Se ejecuta:

1. al arrancar el servidor;
2. de lunes a viernes a las 16:30, hora de Nueva York (30 minutos después
   del cierre, para que Yahoo Finance publique los datos; el horario de
   verano se maneja con la zona horaria de Nueva York);
3. cada dos minutos mientras falte alguna acción (por ejemplo, si Yahoo
   falló durante el arranque);
4. a petición, con `POST /admin/refresh`.

Cada actualización descarga unos tres años de datos diarios de las siete
acciones, del SPY y del VIX (la media de 200 días y la normalización de 252
días del VIX necesitan historia previa), con tres reintentos por descarga.
Si el mercado sigue abierto, descarta la vela del día, porque su precio aún
no es un cierre. Luego calcula las 76 características, obtiene las tres
probabilidades del modelo para cada día, calcula la etiqueta real de cada día
que ya tiene el cierre siguiente y si la señal acertó (el último día queda
"pendiente"), calcula las métricas de las ventanas de 30, 60 y 90 días, y
guarda todo en una caché en memoria y en la base de datos. Un candado impide
que dos actualizaciones corran al mismo tiempo.

**Por qué se recalcula toda la ventana.** El diseño de TT1 proponía un
proceso incremental que calculara solo el día nuevo. Recalcular toda la
ventana cuesta segundos y garantiza que todo lo que se muestra salió del
modelo vigente: si el modelo se reentrena, la historia se actualiza sola, no
hay estados intermedios que reparar y la base de datos se puede reconstruir
en cualquier momento.

**Manejo de fallas.** Si una acción falla se omite (no se inventan datos) y
se reintenta cada dos minutos; si fallan SPY o VIX se omiten todas, porque
sin contexto de mercado las características no son válidas; si falla la base
de datos se revierte la transacción de esa acción y la API sigue sirviendo
desde memoria.

---

## 5. Base de datos (5.5)

La base de datos es SQLite con cuatro tablas definidas con SQLAlchemy
(Figura D04): `assets` (las acciones), `ohlcv_daily` (un precio por acción y
día), `predictions` (una señal por acción y día, con sus tres
probabilidades, la confianza, el cierre, si acertó y la versión del modelo) y
`metrics` (una fila por acción y ventana de 30, 60 o 90 días). Las tres
últimas tienen llave foránea hacia `assets`; las restricciones únicas
(acción, fecha) y (acción, ventana) evitan duplicados y crean los índices de
consulta; la inserción es un *upsert*, de modo que recalcular no duplica
filas.

**Normalización.** Las tablas cumplen la primera y la segunda formas
normales. `ohlcv_daily` está en tercera forma normal. `predictions` y
`metrics` contienen columnas derivadas a propósito (la confianza es el
máximo de las probabilidades; el acierto se deriva de la señal y del cierre
siguiente; las métricas son agregados): son el registro de lo que la
plataforma calculó y mostró con cada versión del modelo. Como hay un solo
proceso que escribe y en cada pasada recalcula todo desde la fuente, esas
columnas no pueden quedar desincronizadas. Es la misma desnormalización
intencional que el diseño de TT1 justificaba para su tabla de resumen de 90
días, ahora en la tabla `metrics`.

**Por qué SQLite y no PostgreSQL.** El diseño de TT1 eligió PostgreSQL por
tres razones: el ETL y la API eran procesos distintos que escribían y leían a
la vez, se guardaba la matriz de confusión en JSONB y se necesitaban índices
compuestos por fecha. En el sistema final la actualización corre en el mismo
proceso que la API, así que hay un solo escritor (protegido por un candado) y
la limitación de concurrencia de SQLite no aplica; SQLite también garantiza
transacciones ACID; no se guarda ninguna estructura que requiera JSONB; y las
restricciones únicas crean los mismos índices. Además, como la base se puede
reconstruir desde Yahoo Finance y el modelo, el servicio puede usar el plan
gratuito de Render, que no ofrece disco persistente. El esquema usa tipos
genéricos de SQLAlchemy y funciona igual en PostgreSQL cambiando la variable
`DATABASE_URL` (el archivo `docker-compose.yml` incluye un perfil con
PostgreSQL 15). Convendría volver a PostgreSQL si hubiera varios procesos
escribiendo o si se guardara información que no se puede regenerar, como
usuarios o carteras.

---

## 6. API REST (5.6)

La API expone nueve rutas de lectura y una de mantenimiento (Tabla T-14).
Todas las respuestas tienen la forma `{"success": true, "data": …}` o
`{"success": false, "error": "…"}` y salen de la caché en memoria que llena
la actualización. El diseño de TT1 incluía cinco rutas `POST` para que un
proceso externo cargara datos; existen, pero están desactivadas (responden
403), porque permitirían escribir valores que no salen del modelo y el
proceso de actualización ya no las necesita. CORS está habilitado porque la
aplicación y la API están en dominios distintos.

---

## 7. Aplicación web (5.7)

La aplicación es una SPA en React 18 con TypeScript, compilada con Vite, con
estilos de Tailwind CSS 4, navegación con React Router 7 y gráficas de
Recharts. Tiene siete pantallas (Figura D05, Tabla T-14b) y está escrita para
un usuario sin conocimientos de finanzas: la recomendación se acompaña de
una frase corta y prudente («Podría subir», «Podría bajar», «Mejor
esperar»), la seguridad del modelo se expresa en palabras, cada métrica
tiene un «?» que lleva a su definición en el glosario y las gráficas tienen
los ejes rotulados con unidades. No contiene datos fijos ni simulados: todo
lo pide a la API, salvo la comparación de modelos, que lee un archivo
generado por la investigación.

**Seguridad de la recomendación.** El modelo entrega tres probabilidades y
la más alta suele estar entre 0.36 y 0.45, porque la regularización es muy
fuerte. Un porcentaje como "36 %" se percibe como una calificación
reprobatoria aunque con tres clases el azar sea 33 %. Por eso se muestran
tres niveles en palabras, con cortes calibrados en siete años evaluados sin
haberlos visto: «Nada segura» (acertó 37 de cada 100), «Poco segura» (38) y
«Medianamente segura» (42). No hay un nivel «Segura» porque ningún tramo
acierta ni la mitad de las veces.

**Respuesta a la revisión.** La pestaña «Modelos» presenta explícitamente el
modelo elegido y por qué, la tabla de igualdad de condiciones, la prueba
2025 de los cinco con selector de experimento, los intervalos de confianza,
la prueba año por año, la prueba ciega 2026, el desempeño económico con y sin
comisiones, la comparación global contra por acción y el análisis de
multicolinealidad.

---

## 8. Integración cliente-servidor (5.8)

La aplicación y la API se comunican solo por HTTP (Figura D06). Al abrir
«Hoy», la aplicación pide `GET /market-status` (para qué sesión es la
recomendación y si la bolsa está abierta) y `GET /stocks`. Si la lista llega
vacía —la API acaba de despertar y Yahoo falló—, llama una vez a
`POST /admin/refresh` y vuelve a pedirla. Al abrir el detalle de una acción
pide `GET /stocks/:s`, `GET /stocks/:s/history?days=` y
`GET /stocks/:s/metrics?days=`; «Resultados» pide `GET /metrics?days=` y
«Acerca de» `GET /model`. Las llamadas se hacen con `fetch` dentro de
`useEffect`, cada pantalla maneja sus estados de carga y error, y la URL de
la API se define en la variable de compilación `VITE_API_URL`. No hay
consulta periódica: la recomendación cambia una vez al día y la página pide
los datos al abrirse o con «Actualizar».

Durante la integración se resolvieron dos problemas que conviene documentar:
el bloqueo por CORS, que ocurre en el navegador y no deja rastro en el
servidor, y el desfase de fechas: JavaScript interpreta una fecha ISO como
medianoche UTC y, en la zona horaria de la Ciudad de México, la mostraba como
el día anterior; se resolvió tratando las fechas como días de calendario.

---

## 9. Despliegue (5.9)

El sistema está desplegado en Render como dos servicios definidos en
`render.yaml` (Figura D07):

- **API** (`https://tt-api-jc7n.onrender.com`): contenedor Docker con
  Python 3.13 y gunicorn. Usa **un solo proceso de trabajo** porque el
  programador de tareas vive dentro del proceso; con varios, la actualización
  diaria se ejecutaría varias veces. El tiempo de espera es de 300 s para que
  la primera actualización termine antes de servir.
- **Aplicación** (`https://tt-frontend-womf.onrender.com`): sitio estático
  con una regla que envía cualquier ruta a `index.html`, para que la
  navegación funcione al recargar.

Ambos se despliegan automáticamente con cada cambio en la rama `main` del
repositorio. Después de un despliegue se verifica que `GET /health` reporte
las siete acciones cargadas y que `GET /model` muestre la versión esperada.
En el plan gratuito el servicio se duerme tras unos 15 minutos sin tráfico:
la primera carga tarda de 20 a 40 segundos y la actualización programada solo
corre si el servicio está despierto a esa hora; la base de datos se
reconstruye en cada arranque, lo cual es aceptable porque no guarda nada que
no pueda regenerarse. En local, la API corre en el puerto 8000 y la
aplicación en el 5173 (o todo con Docker Compose: API en 8000 y aplicación
con nginx en 8080).

---

## 10. Pruebas (5.10)

La API tiene 24 pruebas automáticas (pytest) que verifican las
características (columnas, ausencia de vacíos tras el calentamiento, rangos
de los osciladores), el modelo (características del archivo, forma de la
predicción, versión) y la API (métricas con valores conocidos, días
pendientes, que el acierto se evalúe contra el día siguiente, **que la
etiqueta calculada en vivo coincida con la del entrenamiento**, horario y
feriados del mercado, descarte de la vela en curso, escrituras manuales
desactivadas y una actualización completa con datos simulados, sin red).

Además se hicieron pruebas de estabilidad (solicitudes repetidas durante
periodos largos, varias pestañas abiertas) y pruebas funcionales
recorriendo cada pantalla como un usuario nuevo, incluidos los casos de
error: servidor apagado, respuesta lenta y acción inexistente. En la primera
versión, con PostgreSQL [confirmar con el equipo que fue en esa versión], las pruebas de estabilidad revelaron que las
conexiones no se cerraban cuando una consulta fallaba y que los errores
inesperados devolvían páginas HTML en lugar de JSON; ambos se corrigieron y
hoy todas las respuestas de error usan el formato estándar.
