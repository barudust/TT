# Arquitectura del Frontend

## Tecnologías y Entradas
- React 18 con TypeScript y Vite.
- Tailwind CSS 4 con tokens de color y variantes claro/oscuro en `src/styles/theme.css`.
- React Router 7 (Data APIs) para navegación.
- Recharts para visualizaciones.
- next-themes para control de tema vía `class` en `<html>`.

Entradas clave:
- `index.html` — contenedor y registro de Service Worker.
- `src/main.tsx` — arranque de React, ThemeProvider y App.
- `src/app/App.tsx` — Toaster y RouterProvider.
- `src/app/routes.ts` — definición de rutas.
- `src/app/Root.tsx` — layout, encabezado, navegación inferior, toggle de tema.

## Páginas y Flujo
- `Home.tsx` — listado de señales. Consume `GET /stocks`.
- `StockDetail.tsx` — detalle, métricas y gráfico. Consume `GET /stocks/:symbol`, `.../history`, `.../metrics`.
- `Performance.tsx` — comparación global. Consume `GET /metrics`.
- `About.tsx` — información del proyecto.

## Componentes
- `StockCard.tsx` — tarjeta de acción con insignia de señal.
- `MarketStatus.tsx` — estado del mercado y badges de señal.
- `LoadingStates.tsx` y `ErrorState.tsx` — estados de carga y error.
- `components/ui/*` — elementos de interfaz esenciales: `button`, `card`, `sonner`, `utils`.

## Temas y Estilos
- `src/styles/theme.css` define tokens con variables CSS; `.dark` sobreescribe para modo oscuro.
- `ThemeProvider` (`next-themes`) aplica `class="dark"` al `<html>` cuando corresponde.
- Se usan utilidades semánticas:
  - Fondos: `bg-background`, `bg-card`, `bg-muted`.
  - Texto: `text-foreground`, `text-muted-foreground`.
  - Borde: `border`, `border-border`.
  - Acentos por señal: `text-emerald-600|red-600|amber-600` con variantes `dark:*`.

## Gráficos
- `src/app/components/ui/chart.tsx` fue eliminado en la limpieza. Recharts se usa directamente en `StockDetail.tsx`.
- Tooltips personalizados se estilizan con variables CSS (`var(--color-*)`) cuando aplica.

## Configuración de API
- `src/config/api.ts` resuelve la URL base:
  - Usa `VITE_API_URL` si existe.
  - En local: `http://localhost:8000`.
  - Remoto: `https://<host>:8000`.

## PWA
- `public/manifest.json` y `public/service-worker.js` permanecen para empaquetado posterior.
- `index.html` incluye el registro del Service Worker.

## Recomendaciones
- Mantener uso de tokens de tema para garantizar contraste en ambos modos.
- Evitar colores fijos en fondos; preferir `bg-muted` + bordes coloreados.
- Colorear íconos por `text-*` (Lucide usa stroke; evitar `fill-*`).

