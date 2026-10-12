# B4 — El frontend (aplicación web / PWA)

> **Resumen.** Aplicación de una sola página (SPA) en **React 18 +
> TypeScript**, compilada con **Vite**, con estilos de **Tailwind CSS 4** y
> gráficas de **Recharts**. Es una **PWA**: se puede instalar en el celular
> como una app. Tiene 4 páginas: señales del día, detalle por acción,
> desempeño global y "acerca de". No tiene ningún dato fijo ni simulado:
> todo lo pide a la API.
>
> Código: `Frontend/src/`. Documento técnico: `docs/FRONTEND.md`.

---

## 1. Tecnologías y por qué

| Tecnología | Qué es | Por qué |
|---|---|---|
| **React 18** | Biblioteca para construir interfaces con componentes | Estándar de la industria; la interfaz se arma con piezas reutilizables (tarjeta de acción, estado del mercado…) |
| **TypeScript** | JavaScript con tipos | Los tipos de las respuestas de la API (`src/app/types.ts`) detectan errores antes de ejecutar (por ejemplo, un campo mal escrito) |
| **Vite** | Herramienta de compilación y servidor de desarrollo | Arranque y recarga casi instantáneos; compila a archivos estáticos |
| **Tailwind CSS 4** | Estilos con clases utilitarias | Diseño consistente sin hojas de estilo enormes; modo claro/oscuro con variables |
| **React Router 7** | Navegación entre páginas | Cambiar de vista sin recargar |
| **Recharts** | Gráficas | Gráficas de precio, retorno y F1 declarativas en React |
| **next-themes** | Tema claro/oscuro | |
| **sonner** | Notificaciones (*toasts*) | Avisos de error o actualización |
| **PWA** (`manifest.json` + *service worker*) | App instalable | El TT1 pedía que funcionara en celulares (requerimiento no funcional de diseño responsivo); la PWA además se instala como app sin hacer una app nativa |

---

## 2. Páginas

| Ruta | Página | Qué muestra | Endpoints que usa |
|---|---|---|---|
| `/` | **Señales del día** (`Home.tsx`) | Una tarjeta por acción con la señal para el siguiente día hábil y su confianza; estado del mercado, fecha del cierre usado y hace cuánto se recalculó | `GET /stocks`, `GET /market-status` |
| `/stock/:symbol` | **Detalle** (`StockDetail.tsx`) | Precio y señal diaria en una gráfica; las 3 probabilidades; métricas de la ventana elegida (30/60/90 días); últimas 10 señales con su resultado real | `GET /stocks/:s`, `.../history?days=`, `.../metrics?days=` |
| `/performance` | **Rendimiento global** (`Performance.tsx`) | Promedio de las 7 acciones, retorno de la estrategia contra buy & hold, F1-macro por acción con la línea del azar, tabla ordenable | `GET /metrics?days=` |
| `/about` | **Acerca de** (`About.tsx`) | Descripción del proyecto, metodología, ficha del modelo en producción (leída de la API), aviso legal y créditos | `GET /model` |

### Componentes

- `Root.tsx`: encabezado, navegación inferior (estilo app móvil), cambio de
  tema.
- `StockCard.tsx`: tarjeta de una acción.
- `MarketStatus.tsx`: mercado abierto/cerrado (de la API, no fijo).
- `LoadingStates.tsx`, `ErrorState.tsx`: estados de carga y error.
- `format.ts`: colores y textos de cada señal, formato de porcentajes y
  fechas (centralizado para que toda la app los muestre igual).

---

## 3. Cómo se muestra la información (decisiones de diseño)

| Qué | Cómo | Por qué |
|---|---|---|
| Confianza | Probabilidad de la señal elegida, con la aclaración de que el azar es 33 % | Que el usuario no lea "38 %" como "baja confianza" sin contexto, ni "45 %" como "casi segura" |
| Las 3 probabilidades | Barras por señal | Muestra cuándo la decisión fue reñida |
| Resultado de una señal | Se compara con el movimiento del cierre de ese día al siguiente, con la etiqueta de la tesis; el último día dice "Pendiente" | Mismo criterio que la evaluación de la tesis; no se inventa el resultado |
| Sharpe | "—" con menos de 5 días con posición | Con tan pocas operaciones no es interpretable |
| F1 por acción | Con la línea del azar | Para ver si el modelo supera al azar |
| Buy & hold | Junto al retorno de la estrategia | Referencia honesta |
| Aviso legal | En "Acerca de" | La plataforma es demostrativa, no una recomendación de inversión |

---

## 4. Conexión con la API

- `src/config/api.ts` decide la URL de la API: la variable de compilación
  `VITE_API_URL` si existe; en local `http://localhost:8000`.
- En Render, `VITE_API_URL` se fija en el panel del sitio estático y queda
  "horneada" en los archivos compilados.
- **Arranque en frío:** si `GET /stocks` llega vacío (la API acaba de
  despertar y Yahoo falló), la página de inicio llama una vez a
  `POST /admin/refresh` y vuelve a pedir los datos.

---

## 5. La PWA y el *service worker*

- `public/manifest.json`: nombre, ícono, colores, modo "standalone" (se abre
  sin barra del navegador). Permite "Agregar a la pantalla de inicio".
- `public/service-worker.js`: estrategia **network-first** — siempre pide
  la versión nueva y solo usa la copia guardada si no hay conexión. Las
  respuestas de la API nunca se guardan (siempre datos frescos).
- **Problema que se corrigió:** la versión anterior era *cache-first* con un
  nombre de caché fijo; quien ya había abierto la app se quedaba con la
  interfaz vieja después de cada despliegue. Se cambió a network-first y se
  renombró la caché (`trading-signals-v2`) para borrar la anterior.
- El servidor envía `service-worker.js` con `Cache-Control: no-cache` para
  que las actualizaciones lleguen.

---

## 6. Compilación y despliegue

- `npm run dev`: servidor de desarrollo (http://localhost:5173).
- `npm run build`: genera archivos estáticos en `Frontend/dist/`.
- **Render:** sitio estático (gratuito y siempre disponible), con una regla
  que manda cualquier ruta a `index.html` para que la navegación de React
  funcione al recargar en `/stock/AAPL`.
- **Docker (local):** compila con Node 20 y sirve con nginx
  (`Frontend/Dockerfile`, `nginx.conf`).

---

## 6b. Lo que planteaba el TT1 y qué se implementó

El TT1 (§4.4) definió un actor (usuario consultor, sin registro), tres casos
de uso y una interfaz de **tres niveles**:

| TT1 | Final |
|---|---|
| CU-01 consultar señales del día | Página de inicio (tarjetas por acción) |
| CU-02 revisar el detalle de un activo | Página de detalle |
| CU-03 comparar el rendimiento del portafolio y contra el S&P 500 | Página de rendimiento (contra comprar y mantener **cada acción**, no contra el S&P 500) |
| Nivel 1: panel general del portafolio | Página de rendimiento |
| Nivel 2: tarjetas por activo (retorno 90 d, Sharpe, win rate, señal) | Tarjetas con señal y confianza; las métricas están en el detalle |
| Nivel 3: detalle expandible con **curva de capital** (estrategia vs buy & hold), historial de 30 días, F1 por clase y **matriz de confusión** | Detalle con gráfica de precio y señal, 3 probabilidades, métricas 30/60/90, últimas 10 señales con su resultado. **No se implementaron** la curva de capital ni la matriz de confusión |
| Gráfica de pastel con la distribución de señales | No implementada (la distribución se muestra como porcentajes) |
| **Consulta automática a la API cada hora** | No implementada: la página pide los datos al abrirse o al pulsar "Actualizar"; como la señal cambia una vez al día, no hace falta |
| Requerimientos no funcionales: carga < 2 s, navegadores modernos, responsivo | Responsivo y PWA instalable. La primera carga después de que Render duerme el servicio tarda 20–40 s; después es inmediata |
| Puerto 3000, sin autenticación | Sitio estático en Render, sin autenticación |

**Si preguntan por lo que falta:** la curva de capital y la matriz de
confusión se pueden construir con datos que la API ya calcula (el historial
de señales con su resultado); se priorizó mostrar el resultado de cada
señal contra el día siguiente y la comparación contra el azar, que es lo que
permite al usuario juzgar el modelo.

---

## 7. Limitaciones y deuda técnica

- `package.json` arrastra dependencias de la plantilla inicial que no se
  usan (varios componentes de Radix UI, Material UI, etc.). Vite solo
  empaqueta lo que se importa, así que no afectan al tamaño final, pero
  sobran.
- No hay pruebas automáticas del frontend (las 23 pruebas son de la API).
- El texto "Acerca de" y el encabezado describen el proyecto como una
  comparación de Machine Learning y Deep Learning, lo cual es correcto; la
  descripción de la PWA (`manifest.json` e `index.html`) decía "Deep
  Learning - LSTM y CNN-LSTM" y se corrigió el 2026-10-12.

---

## Preguntas de este tema

Están desarrolladas en [D6](../D_defensa/D6_PREGUNTAS_SISTEMA.md).
