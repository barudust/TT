# 🚀 Quick Start Guide - TradingSignals AI

Esta guía te ayudará a empezar rápidamente con la aplicación.

---

## ✅ La Aplicación Ya Está Lista

La aplicación web ya está completamente funcional con **datos simulados** para demostración. Puedes usarla inmediatamente para:

- ✅ Ver señales de trading para 8 acciones
- ✅ Explorar gráficos históricos
- ✅ Analizar métricas de rendimiento
- ✅ Comparar performance entre acciones

---

## 📱 Características Actuales

### Página Principal (/)
- Lista de 8 acciones con señales BUY/SELL/HOLD
- Precios actuales y nivel de confianza
- Estado del mercado y última actualización
- Botón de actualizar datos

### Detalle de Acción (/stock/:symbol)
- Gráfico interactivo de precios (30/60/90 días)
- Visualización de predicciones en el gráfico
- Métricas de rendimiento (Accuracy, Precision, F1-Score)
- Historial de señales con comparación

### Rendimiento (/performance)
- Gráfico comparativo entre todas las acciones
- Tabla ordenable por cualquier métrica
- Estadísticas promedio del sistema

### Acerca De (/about)
- Información del proyecto académico
- Metodología y modelos
- Disclaimer legal

---

## 🎯 Para Usar Con Tus Modelos Reales

### Paso 1: Preparar Tu Modelo de Deep Learning

```python
# Entrena tu modelo LSTM o CNN-LSTM
import tensorflow as tf

model = tf.keras.Sequential([
    tf.keras.layers.LSTM(128, return_sequences=True, input_shape=(60, 5)),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.LSTM(64),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(3, activation='softmax')  # buy/sell/hold
])

# Entrena con tus datos históricos
model.fit(X_train, y_train, epochs=50, validation_data=(X_val, y_val))

# Guarda el modelo
model.save('trading_model.h5')
```

### Paso 2: Crear Script de Actualización

Usa el archivo `update_script_example.py` como plantilla:

```python
# 1. Cargar tu modelo entrenado
model = tf.keras.models.load_model('trading_model.h5')

# 2. Obtener datos de Yahoo Finance
import yfinance as yf
ticker = yf.Ticker("AAPL")
data = ticker.history(period="90d")

# 3. Preprocesar datos
# ... tu código de preprocesamiento ...

# 4. Hacer predicción
prediction = model.predict(X)
signal = "buy" if prediction[0][0] > 0.5 else ("sell" if prediction[0][2] > 0.5 else "hold")
confidence = max(prediction[0])

# 5. Guardar en la base de datos (ver INTEGRATION_GUIDE.md)
```

### Paso 3: Formato de Datos

Los datos deben guardarse en el KV Store con este formato:

```typescript
// Señales diarias
await kv.set("stocks:list", [
  {
    symbol: "AAPL",
    name: "Apple Inc.",
    currentPrice: 175.30,
    signal: "buy",  // "buy", "sell", o "hold"
    confidence: 0.78,
    lastUpdate: "2026-03-02T18:00:00Z"
  },
  // ... más acciones
]);
```

### Paso 4: Configurar Actualización Automática

**Linux/Mac (crontab):**
```bash
# Editar crontab
crontab -e

# Ejecutar diariamente a las 6 PM
0 18 * * 1-5 /usr/bin/python3 /ruta/al/update_script.py
```

**Windows (Task Scheduler):**
1. Abrir Task Scheduler
2. Crear tarea básica
3. Trigger: Diario a las 6:00 PM
4. Acción: Ejecutar `python update_script.py`

---

## 📚 Documentación Completa

Para información detallada, consulta:

- **`INTEGRATION_GUIDE.md`**: Formato de datos y cómo integrar tus modelos
- **`TECHNICAL_NOTES.md`**: Arquitectura, endpoints, troubleshooting
- **`update_script_example.py`**: Script de ejemplo para actualización diaria
- **`README.md`**: Descripción completa del proyecto

---

## 🎨 Estructura de Archivos Importantes

```
/src/app/
├── App.tsx                    # Entrada principal
├── Root.tsx                   # Layout con navegación
├── routes.ts                  # Configuración de rutas
├── components/
│   ├── StockCard.tsx          # Tarjeta de acción
│   ├── MarketStatus.tsx       # Estado del mercado
│   ├── LoadingStates.tsx      # Componentes de carga
│   └── ErrorState.tsx         # Manejo de errores
└── pages/
    ├── Home.tsx               # Lista de acciones
    ├── StockDetail.tsx        # Detalle con gráficos
    ├── Performance.tsx        # Comparación global
    └── About.tsx              # Información

/supabase/functions/server/
├── index.tsx                  # API REST
└── stock_data.tsx             # Lógica de datos y simulación
```

---

## 🔧 Endpoints de la API

```
Base URL: https://uawrdarivadefdvxbgoj.supabase.co/functions/v1/make-server-8ca8c1f7

GET  /stocks                      → Lista de acciones con señales
GET  /stocks/:symbol              → Detalle de una acción
GET  /stocks/:symbol/history      → Historial de precios (?days=30|60|90)
GET  /stocks/:symbol/metrics      → Métricas de rendimiento
GET  /metrics                     → Métricas de todas las acciones
```

---

## 💡 Tips Rápidos

### Para Desarrolladores Frontend
- La app usa React Router 7 con Data Mode
- Tailwind CSS 4 para estilos
- Recharts para gráficos
- Todos los estilos están inline, puedes modificarlos fácilmente

### Para Científicos de Datos
- Los modelos deben generar 3 clases: buy, sell, hold
- Usa Yahoo Finance para datos históricos (`yfinance` en Python)
- Calcula métricas: accuracy, precision, recall, F1-score
- Guarda predicciones diarias para backtesting

### Para Testing
- Los datos simulados son consistentes
- Puedes modificar `stock_data.tsx` para ajustar simulación
- Las métricas están en el rango 60-75% (realista)

---

## 🚨 Datos Actuales (Simulados)

La aplicación actualmente usa **datos simulados** que incluyen:

- ✅ Precios realistas basados en valores históricos
- ✅ Señales aleatorias balanceadas
- ✅ Métricas coherentes (60-75% accuracy)
- ✅ Historial de 30, 60 y 90 días
- ✅ Backtesting con resultados mixtos (realista)

**Para producción**: Reemplaza con datos reales siguiendo `INTEGRATION_GUIDE.md`

---

## 📊 Acciones Incluidas

| Símbolo | Empresa | Precio Base Simulado |
|---------|---------|---------------------|
| AAPL | Apple Inc. | ~$175 |
| MSFT | Microsoft Corporation | ~$410 |
| GOOGL | Alphabet Inc. | ~$140 |
| AMZN | Amazon.com Inc. | ~$175 |
| TSLA | Tesla Inc. | ~$195 |
| META | Meta Platforms Inc. | ~$485 |
| NVDA | NVIDIA Corporation | ~$875 |

---

## ⚡ Próximos Pasos

1. **Explora la aplicación** para familiarizarte con el UI/UX
2. **Lee `INTEGRATION_GUIDE.md`** para entender el formato de datos
3. **Entrena tus modelos** LSTM/CNN-LSTM con datos históricos
4. **Adapta `update_script_example.py`** para tu caso
5. **Configura cron job** para actualización automática
6. **Reemplaza datos simulados** con predicciones reales

---

## 🎓 Proyecto Académico

Este proyecto es parte del **Trabajo Terminal TT 2026-B164** de ESCOM-IPN.

**Uso exclusivamente educativo** - No constituye asesoramiento financiero.

---

## ❓ ¿Necesitas Ayuda?

1. **Para formato de datos**: Lee `INTEGRATION_GUIDE.md`
2. **Para arquitectura técnica**: Lee `TECHNICAL_NOTES.md`
3. **Para el proyecto completo**: Lee `README.md`
4. **Para script de Python**: Revisa `update_script_example.py`

---

**¡Éxito con tu proyecto!** 🚀📈
