# Guía para Documentar la Plataforma en la Tesis

## Índice Sugerido
1. Resumen
2. Introducción
   - Motivación y objetivos
   - Alcance y limitaciones
3. Marco Teórico
   - Series de tiempo financieras
   - Redes LSTM y CNN-LSTM
   - Métricas de clasificación y financieras
4. Estado del Arte
   - Enfoques de predicción bursátil con DL
5. Arquitectura del Sistema
   - Visión general (cliente-servidor)
   - Diagrama de componentes y flujo de datos
6. Frontend
   - Tecnologías: React, TypeScript, Vite, Tailwind, Recharts, next-themes
   - Rutas y páginas: Home, StockDetail, Performance, About
   - Diseño de UI y theming (tokens, modo claro/oscuro)
   - PWA y consideraciones Android
7. Backend (API)
   - Tecnologías: Flask, CORS, yfinance
   - Tipo de API: REST sobre HTTP, JSON
   - Endpoints y contratos de datos
   - Estrategia de actualización y cálculo de métricas
   - Integración del modelo (señal y confianza)
8. Almacenamiento de Datos
   - Esquema propuesto (SQLite local)
   - Plan de migración a Azure (SQL/PostgreSQL)
   - Consideraciones de consistencia, índices y seguridad
9. Entrenamiento del Modelo
   - Conjunto de datos, preprocesamiento y ventanas
   - Entrenamiento y validación
   - Selección de hiperparámetros
10. Resultados y Evaluación
    - Métricas (accuracy, precision, F1, Sharpe, drawdown)
    - Análisis y discusión
11. Despliegue
    - Variables de entorno (VITE_API_URL)
    - Opciones de hosting (frontend/API)
12. Seguridad y Ética
    - Advertencias de uso educativo
13. Trabajo Futuro
    - Mejoras del modelo, persistencia, app Android
14. Conclusiones
15. Anexos
    - Manual de instalación y ejecución
    - Capturas de pantalla

## Tecnologías y Descripciones Breves
- Flask: microframework de Python para construir APIs REST.
- Node/React: ecosistema JavaScript; React para interfaces declarativas.
- Vite: bundler y dev server de alto rendimiento.
- Tailwind CSS 4: utilidades CSS; theming con variables.
- Recharts: librería de gráficos basada en React.
- yfinance: obtención de datos bursátiles históricos.
- SQLite: base de datos embebida para entorno local.

## Recomendaciones de Redacción
- Mantener definiciones claras de cada módulo y su responsabilidad.
- Incluir diagramas de secuencia para el flujo de datos (inferencia → API → Frontend).
- Explicar supuestos del modelo y sus implicaciones.
- Documentar decisiones de diseño (tokens de tema, eliminación de fondos fijos).
- Señalar limitaciones y pasos de validación.

