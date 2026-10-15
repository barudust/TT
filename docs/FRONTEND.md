# Arquitectura del Frontend

SPA en `Frontend/`. Todo lo que muestra sale de la API (`docs/API.md`): no
hay valores fijos ni simulados en las páginas.

## Tecnologías y entradas
- React 18 con TypeScript y Vite.
- Tailwind CSS 4 con tokens de color y variantes claro/oscuro en `src/styles/theme.css`.
- React Router 7 (Data APIs) para navegación.
- Recharts para gráficas.
- next-themes para el tema vía `class` en `<html>`.

Entradas clave:
- `index.html` — contenedor y registro del Service Worker.
- `src/main.tsx` — arranque de React, ThemeProvider y App.
- `src/app/App.tsx` — Toaster y RouterProvider.
- `src/app/routes.ts` — definición de rutas.
- `src/app/Root.tsx` — layout, encabezado, navegación inferior, toggle de tema.
- `src/app/types.ts` — tipos de las respuestas de la API.
- `src/app/format.ts` — colores, nombre y frase de cada recomendación
  (`SIGNAL_CONFIG`), escala de seguridad (`NIVELES_SEGURIDAD`) y formato de
  porcentajes, dinero, fechas y drawdown.
- `src/app/glosario.ts` — definiciones en lenguaje sencillo de cada término
  que aparece en pantalla (las usa la página de Ayuda y los íconos «?»).

## Páginas y endpoints que consumen
- `Home.tsx` (ruta `/`, pestaña «Hoy») — «¿Qué hacer hoy con cada acción?».
  Para qué sesión es la recomendación (`nextTradingDay`) y con qué cierre se
  calculó. `GET /stocks`, `GET /market-status`. Si el catálogo llega vacío
  (arranque en frío de Render) dispara `POST /admin/refresh` una vez y
  reintenta.
- `StockDetail.tsx` (`/stock/:symbol`) — recomendación, seguridad en
  palabras, probabilidades; gráfica de precio con un punto de color por
  recomendación (ejes rotulados); gráfica «¿Qué habría pasado con $1,000?»
  (siguiendo las recomendaciones vs comprar y esperar, calculada con la misma
  fórmula que la API); resultados del periodo con rendimiento de la inversión
  (ROI) y su equivalente en dinero; últimas 10 recomendaciones con porcentajes.
  `GET /stocks/:symbol`, `.../history?days=`, `.../metrics?days=`.
- `Performance.tsx` (`/performance`, pestaña «Resultados») — resumen de las 7
  empresas, ganancia por empresa vs comprar y esperar, calificación F1 por
  empresa con la línea de azar y tabla ordenable con unidades.
  `GET /metrics?days=`.
- `Help.tsx` (`/ayuda`, pestaña «Ayuda») — dos pestañas: **Guía de uso**
  (manual corto por pantalla, escala de seguridad, cuándo se actualiza,
  instalación en el celular) y **Glosario** (buscable, por categorías). Los
  íconos «?» enlazan a `/ayuda?tab=glosario#<término>`.
- `About.tsx` (`/about`) — descripción del proyecto y ficha del modelo en
  producción, leída de `GET /model`.

## Componentes
- `StockCard.tsx` — tarjeta de una empresa: nombre, precio, recomendación con
  su frase y nivel de seguridad.
- `SeguridadBadge.tsx` — nivel de seguridad en palabras con barras azules (no
  verdes/rojas, para no confundirse con COMPRAR/VENDER).
- `MetricCard.tsx` — tarjeta de una métrica con su «?» al glosario.
- `InfoLink.tsx` — ícono «?» que lleva al término del glosario.
- `MarketStatus.tsx` — para qué sesión es la recomendación, con qué cierre se
  calculó, si la bolsa está abierta y hace cuánto se actualizó.
- `LoadingStates.tsx` y `ErrorState.tsx` — estados de carga y error.
- `components/ui/*` — `button`, `card`, `sonner`, `utils`.

## Cómo se muestran los datos
- **Vocabulario para cualquier usuario:** «recomendación» en lugar de
  «señal»; «rendimiento de la inversión (ROI)» con su equivalente sobre
  $1,000; «comprar y esperar» en lugar de buy & hold; «peor caída» en lugar
  de drawdown; el nombre técnico queda entre paréntesis o en el glosario.
- **Seguridad de la recomendación** (antes «confianza», un porcentaje entre
  33 % y 45 % difícil de interpretar): tres niveles con palabras según la
  probabilidad de la opción elegida.

  | Nivel | Probabilidad | Acierto 2019–2025 | Días |
  |---|---|---:|---:|
  | Nada segura | < 0.350 | 37 % | 30 % |
  | Poco segura | 0.350–0.366 | 38 % | 30 % |
  | Medianamente segura | ≥ 0.366 | 42 % | 40 % |

  Azar ≈ 33 %. Los cortes son los percentiles 30 y 60 de la confianza del
  modelo actual y el acierto se midió con modelos que no habían visto el año
  evaluado (`scripts_opt/calibrar_niveles_confianza.py`). No hay un nivel
  «Segura» porque ningún tramo acierta ni la mitad de las veces.
- **Fechas**: largas con día de la semana («jueves 15 de octubre de 2026») en
  los encabezados; cortas («15 oct») en los ejes.
- **Gráficas**: ejes con título y unidades; puntos de 6 px; leyendas en texto
  bajo cada gráfica; líneas rectas entre días (sin suavizado que invente
  valores).
- **Resultado de una recomendación**: se compara con el movimiento del cierre
  de ese día al cierre del siguiente día hábil (misma etiqueta que en
  entrenamiento). El día más reciente aparece como «Pendiente».
- **Sharpe** se muestra como «—» con menos de 5 días con posición en la
  ventana (no es interpretable con tan pocas operaciones).
- Definiciones exactas de cada métrica: `docs/API_FRONTEND_METRICS.md`.

## Temas y estilos
- `src/styles/theme.css` define tokens con variables CSS; `.dark` sobrescribe para modo oscuro.
- Utilidades semánticas: `bg-background`, `bg-card`, `bg-muted`,
  `text-foreground`, `text-muted-foreground`, `border-border`.
- Colores de cada recomendación centralizados en `format.ts` (`SIGNAL_CONFIG`).

## Configuración de API
- `src/config/api.ts` resuelve la URL base: `VITE_API_URL` si existe; en local
  `http://localhost:8000`; en otro host `https://<host>:8000`.
- En Render, `VITE_API_URL` se fija en el dashboard del static site
  (`docs/DEPLOY_RENDER.md`).

## PWA
- `public/manifest.json` y `public/service-worker.js`.
- El service worker es **network-first** con caché `trading-signals-v2`:
  siempre pide la versión nueva y solo usa la caché sin conexión. La versión
  anterior era cache-first con nombre fijo y dejaba a los usuarios con la
  interfaz vieja después de cada despliegue. Si se vuelve a cambiar su
  estrategia, cambiar también `CACHE_NAME` para que se borre la caché previa.
- Las respuestas de la API (otro origen) nunca se cachean.
