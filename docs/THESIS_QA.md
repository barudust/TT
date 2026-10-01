# Guía de Preguntas y Respuestas (Defensa)

## Arquitectura
- Separación Frontend/Backend: justificación, ventajas para despliegue y escalabilidad.
- PWA: motivos y beneficios para Android.
- Enrutamiento y estado en el cliente: elección de React Router 7.

## Modelado
- Selección final: Regresión Logística regularizada (global) por encima de
  XGBoost, LightGBM, LSTM, CNN y CNN-LSTM. Banco completo de preguntas y
  respuestas: `RESULTADOS_OPTIMIZADOS/GUIA_DEFENSA_TT.md` (Cap. 15 y 17);
  por qué no se puede mejorar más:
  `RESULTADOS_OPTIMIZADOS/JUSTIFICACION_LIMITE_DEL_MODELO.md`; modelo
  desplegado: `docs/MODEL_INTEGRATION.md`.
- Etiquetado de clases (buy/sell/hold) y umbrales.
- Preprocesamiento: ventanas temporales, normalización.
- Métricas: F1-macro y F1 por clase, kappa; estrategia de un día (retorno, Sharpe, drawdown, win rate). En la plataforma cada señal se evalúa contra el día siguiente con la misma etiqueta del entrenamiento (`docs/API_FRONTEND_METRICS.md`).
- Por qué tanto MANTENER y cómo se ajustó: `GUIA_DEFENSA_TT.md` P17.1–P17.8.
- Limitaciones: no considera costes de deslizamiento reales, latencias, ni eventos exógenos.

## Datos
- Fuente: Yahoo Finance, alcance y calidad.
- Ventanas 30/60/90 días: propósito comparativo.
- Riesgos: periodos sin datos, splits, mercados cerrados.

## API
- Endpoints y contratos de datos.
- Estrategia de actualización: inicialización y refresco.
- CORS y seguridad básica; overrides manuales desactivados (todo dato mostrado sale del modelo o de Yahoo Finance).

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
- ~~Integración del modelo final en `api/main.py`~~ — hecho, ver `docs/MODEL_INTEGRATION.md`.
- ~~Persistencia durable de datos~~ — hecho, SQLite vía SQLAlchemy, ver `docs/DATABASE.md`.
- ~~Refresco automático programado~~ — hecho, APScheduler corre `initialize_data()`
  cada día hábil a las 16:30 hora de Nueva York (ver `docs/API.md`).
- ~~Tests automatizados~~ — hecho, `api/tests/` (pytest, sin red real).
- ~~Empaquetado de despliegue~~ — hecho, `Dockerfile`(s) + `docker-compose.yml`.
- Entrenamiento incremental y evaluación en producción.
- Empaquetado Android nativo (se decidió no perseguirlo; el proyecto queda
  como aplicación web/PWA).

