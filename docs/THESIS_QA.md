# Guía de Preguntas y Respuestas (Defensa)

## Arquitectura
- Separación Frontend/Backend: justificación, ventajas para despliegue y escalabilidad.
- PWA: motivos y beneficios para Android.
- Enrutamiento y estado en el cliente: elección de React Router 7.

## Modelado
- Selección de LSTM/CNN-LSTM: razones y escenarios de uso.
- Etiquetado de clases (buy/sell/hold) y umbrales.
- Preprocesamiento: ventanas temporales, normalización.
- Métricas: accuracy, precision por clase, F1-Score; métricas financieras (retorno, Sharpe, drawdown).
- Limitaciones: no considera costes de deslizamiento reales, latencias, ni eventos exógenos.

## Datos
- Fuente: Yahoo Finance, alcance y calidad.
- Ventanas 30/60/90 días: propósito comparativo.
- Riesgos: periodos sin datos, splits, mercados cerrados.

## API
- Endpoints y contratos de datos.
- Estrategia de actualización: inicialización y refresco.
- CORS y seguridad básica.

## Frontend
- Tokens de tema y accesibilidad (contraste).
- Razonamiento detrás de `bg-muted` y uso de `text-*` en íconos.
- Reducción de componentes a lo esencial.

## Despliegue
- Variables de entorno (`VITE_API_URL`).
- Opciones futuras: TWA/Capacitor para Android.

## Ética y Riesgos
- Este sistema es educativo; no constituye asesoría financiera.
- Divulgación de limitaciones al usuario.

## Mejoras Futuras
- Integración del modelo final en `api/main.py`.
- Persistencia durable de datos y cachés.
- Entrenamiento incremental y evaluación en producción.

