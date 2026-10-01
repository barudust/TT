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
- `src/app/format.ts` — colores/etiquetas de cada señal y formato de
  porcentajes, fechas y drawdown (con espacio no separable antes de `%`).

## Páginas y endpoints que consumen
- `Home.tsx` — señales del día. `GET /stocks`, `GET /market-status`. Si el
  catálogo llega vacío (arranque en frío de Render) dispara
  `POST /admin/refresh` una vez y reintenta.
- `StockDetail.tsx` — precio, señal, probabilidades de las 3 clases,
  métricas de la ventana elegida (30/60/90 días) y las últimas 10 señales con
  su resultado real. `GET /stocks/:symbol`, `.../history?days=`,
  `.../metrics?days=`.
- `Performance.tsx` — promedio de las 7 acciones, retorno de la estrategia vs
  buy & hold, F1 por acción con la línea de azar y tabla ordenable.
  `GET /metrics?days=`.
- `About.tsx` — descripción del proyecto y ficha del modelo en producción,
  leída de `GET /model`.

## Componentes
- `StockCard.tsx` — tarjeta de acción con su señal y confianza.
- `MarketStatus.tsx` — mercado abierto/cerrado (de la API), fecha del cierre
  usado y hace cuánto se recalcularon las señales.
- `LoadingStates.tsx` y `ErrorState.tsx` — estados de carga y error.
- `components/ui/*` — `button`, `card`, `sonner`, `utils`.

## Cómo se muestran los datos
- **Confianza** = probabilidad del modelo para la señal elegida; se aclara que
  el azar es 33 %.
- **Resultado de una señal**: se compara con el movimiento del cierre de ese
  día al cierre del siguiente día hábil (misma etiqueta que en
  entrenamiento). El día más reciente aparece como "Pendiente".
- **Sharpe** se muestra como "—" con menos de 5 días con posición en la
  ventana (no es interpretable con tan pocas operaciones).
- Definiciones exactas de cada métrica: `docs/API_FRONTEND_METRICS.md`.

## Temas y estilos
- `src/styles/theme.css` define tokens con variables CSS; `.dark` sobrescribe para modo oscuro.
- Utilidades semánticas: `bg-background`, `bg-card`, `bg-muted`,
  `text-foreground`, `text-muted-foreground`, `border-border`.
- Colores de señal centralizados en `format.ts` (`SIGNAL_CONFIG`).

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
