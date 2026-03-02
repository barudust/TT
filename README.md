# 📈 TradingSignals AI - Aplicación de Predicción Bursátil

Aplicación web para visualizar señales de trading generadas por modelos de Deep Learning (LSTM, CNN-LSTM) para 8 acciones del mercado bursátil estadounidense.

**Trabajo Terminal TT 2026-B164 - ESCOM IPN**

---

## 🎯 Características Principales

### 📱 Pantalla de Acciones
- Lista de 8 acciones con señales diarias (BUY LONG, SELL SHORT, HOLD)
- Precio actual y nivel de confianza del modelo
- Actualización manual con botón de recarga
- Diseño tipo aplicación móvil (responsive)

### 📊 Detalle de Acción
- Gráfico de precios históricos (30, 60, 90 días)
- Visualización de predicciones pasadas (backtesting)
- Métricas de rendimiento del modelo:
  - Precisión Global (Accuracy)
  - Precisión para compras (Buy Precision)
  - Precisión para ventas (Sell Precision)
  - F1-Score
- Historial de señales con comparación predicción vs. realidad

### 🏆 Rendimiento Global
- Gráfico comparativo de todas las acciones
- Tabla ordenable por cualquier métrica
- Estadísticas promedio del sistema

### ℹ️ Acerca de
- Descripción del proyecto académico
- Metodología y modelos utilizados
- Disclaimer legal
- Créditos institucionales

---

## 🏗️ Arquitectura

```
Frontend (React + TypeScript)
       ↓
API REST (Supabase Edge Functions)
       ↓
KV Store (Supabase Database)
       ↑
Modelos de Deep Learning (Python/TensorFlow)
```

### Stack Tecnológico

**Frontend:**
- React 18.3
- TypeScript
- React Router 7
- Recharts (gráficos)
- Tailwind CSS 4
- Lucide React (iconos)

**Backend:**
- Supabase Edge Functions
- Hono (framework web)
- Deno runtime
- KV Store para persistencia

**Modelos (no incluidos):**
- Python + TensorFlow
- LSTM / CNN-LSTM
- Yahoo Finance API

---

## 📋 Acciones Monitoreadas

| Símbolo | Empresa | Sector |
|---------|---------|--------|
| AAPL | Apple Inc. | Tecnología |
| MSFT | Microsoft Corporation | Tecnología |
| GOOGL | Alphabet Inc. | Tecnología |
| AMZN | Amazon.com Inc. | E-commerce |
| TSLA | Tesla Inc. | Automotriz |
| META | Meta Platforms Inc. | Redes Sociales |
| NVDA | NVIDIA Corporation | Semiconductores |
| JPM | JPMorgan Chase & Co. | Financiero |

---

## 🚀 Estructura del Proyecto

```
/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── StockCard.tsx          # Tarjeta de acción
│   │   │   └── ui/                    # Componentes de UI
│   │   ├── pages/
│   │   │   ├── Home.tsx               # Lista de acciones
│   │   │   ├── StockDetail.tsx        # Detalle con gráficos
│   │   │   ├── Performance.tsx        # Rendimiento global
│   │   │   └── About.tsx              # Información del proyecto
│   │   ├── App.tsx                    # Punto de entrada
│   │   ├── Root.tsx                   # Layout principal
│   │   └── routes.ts                  # Configuración de rutas
│   └── styles/                        # Estilos globales
├── supabase/
│   └── functions/
│       └── server/
│           ├── index.tsx              # API REST
│           ├── stock_data.tsx         # Lógica de datos
│           └── kv_store.tsx           # Acceso a KV Store
├── INTEGRATION_GUIDE.md               # Guía de integración
└── package.json
```

---

## 🔌 API Endpoints

### GET `/make-server-8ca8c1f7/stocks`
Lista de todas las acciones con señales actuales.

### GET `/make-server-8ca8c1f7/stocks/:symbol`
Detalle de una acción específica con historial de señales.

### GET `/make-server-8ca8c1f7/stocks/:symbol/history?days=30`
Datos históricos de precios (30, 60 o 90 días).

### GET `/make-server-8ca8c1f7/stocks/:symbol/metrics`
Métricas de rendimiento del modelo para una acción.

### GET `/make-server-8ca8c1f7/metrics`
Métricas de todas las acciones.

---

## 📊 Formato de Datos

Consulta el archivo `INTEGRATION_GUIDE.md` para la documentación completa del formato de datos que tus modelos deben generar.

### Ejemplo de Señal:
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "currentPrice": 175.30,
  "signal": "buy",
  "confidence": 0.78,
  "lastUpdate": "2026-03-02T18:00:00Z"
}
```

---

## 🎨 Diseño UI/UX

### Colores de Señales
- 🟢 **BUY LONG**: Verde (#4CAF50) - Flecha hacia arriba
- 🔴 **SELL SHORT**: Rojo (#F44336) - Flecha hacia abajo
- 🟡 **HOLD**: Amarillo (#FFC107) - Círculo

### Navegación
- Bottom Navigation con 3 secciones
- Diseño mobile-first responsive
- Transiciones suaves y animaciones

---

## 🔄 Flujo de Actualización Diaria

1. **Cierre del mercado** (4:00 PM EST)
2. **Recolección de datos** via Yahoo Finance
3. **Ejecución de modelos** LSTM/CNN-LSTM
4. **Generación de señales** con nivel de confianza
5. **Actualización en KV Store** via API
6. **Disponibilidad en app web** para usuarios

---

## 📝 Datos Simulados

Actualmente, la aplicación utiliza **datos simulados** para demostración. Los datos incluyen:

- Precios realistas basados en valores históricos
- Señales aleatorias con distribución balanceada
- Métricas de rendimiento coherentes (60-75% accuracy)
- Historial de 30, 60 y 90 días

**Para producción:** Reemplaza con datos reales de tus modelos siguiendo la guía en `INTEGRATION_GUIDE.md`.

---

## ⚠️ Disclaimer Legal

Esta aplicación es parte de un proyecto académico con fines **exclusivamente educativos y de investigación**. 

**NO constituye asesoramiento financiero** de ningún tipo. Las señales generadas por los modelos de Deep Learning no garantizan resultados futuros.

Invertir en el mercado de valores conlleva riesgos significativos y puede resultar en pérdida de capital. Consulte siempre con un asesor financiero certificado antes de tomar decisiones de inversión.

---

## 🎓 Créditos

**Institución:** Escuela Superior de Cómputo (ESCOM)  
**Organización:** Instituto Politécnico Nacional (IPN)  
**Trabajo Terminal:** TT 2026-B164  
**Año:** 2026

### Tecnologías Utilizadas
- Python
- TensorFlow
- LSTM / CNN-LSTM
- React
- TypeScript
- Supabase
- Yahoo Finance API
- Recharts
- Tailwind CSS

---

## 📞 Soporte y Preguntas

Para integrar tus modelos de Deep Learning con esta aplicación:

1. Lee la guía completa en `INTEGRATION_GUIDE.md`
2. Revisa los ejemplos en `/supabase/functions/server/stock_data.tsx`
3. Asegúrate de seguir el formato exacto de datos

---

## 🚧 Próximos Pasos

Para poner en producción:

1. ✅ Conectar modelos reales de Deep Learning
2. ✅ Configurar actualización automática diaria
3. ✅ Integrar Yahoo Finance API para precios reales
4. ✅ Implementar sistema de notificaciones (opcional)
5. ✅ Agregar análisis de sentimiento de noticias (futuro)
6. ✅ Expandir a más acciones (futuro)

---

**Versión:** 1.0.0  
**Última actualización:** Marzo 2026
