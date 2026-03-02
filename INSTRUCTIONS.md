# INSTRUCTIONS - Ejecutar TradingSignals AI Local

## 📋 PRIMERO: Instalar Dependencias (UNA SOLA VEZ)

Abre PowerShell o CMD en tu proyecto y ejecuta:

```
pip install flask flask-cors
```

Si tienes problemas con pip, intenta:

```
python -m pip install flask flask-cors
```

O con Python 3:

```
python3 -m pip install flask flask-cors
```

Deberías ver algo como:
```
Successfully installed flask-3.0.0 flask-cors-4.0.0
```

---

## 🚀 SEGUNDO: Ejecutar la Aplicación

### Opción A: Dos terminales (Recomendado)

**TERMINAL 1 - API Backend:**
```
cd api
python main.py
```

Deberías ver:
```
[*] API iniciada en http://localhost:8000
[*] Flask en modo debug
 * Running on http://0.0.0.0:8000
```

**TERMINAL 2 - Frontend React:**
```
npm run dev
```

Deberías ver:
```
VITE v6.3.5  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

---

### Opción B: Una terminal (Modo fondo)

```
start python main.py
npm run dev
```

---

## 🌐 TERCERO: Abrir en Navegador

Abre tu navegador en:
```
http://localhost:5173
```

Deberías ver la pantalla con las 8 acciones y sus señales (BUY, SELL, HOLD).

---

## 📤 CUARTO: Enviar Datos Simulados (Opcional)

Abre TERMINAL 3:

```
cd api
python send_data.py
```

Elige una opción:
- 1: Todas las acciones
- 2: Una acción específica
- 3: Múltiples acciones

Después, **actualiza el navegador (F5)** para ver los cambios.

---

## 🔧 TROUBLESHOOTING

### "No se encuentra python"
**Solución:** Usa `python3` en lugar de `python`, o agrega Python al PATH.

### "Error: flask not found"
**Solución:** Ejecuta el comando de instalación de nuevo:
```
pip install flask flask-cors
```

### "Error: Port 8000 already in use"
**Solución:** La API ya está corriendo. O cambia el puerto en `api/main.py` línea 319.

### "Error: Port 5173 already in use"
**Solución:** Ese puerto está siendo usado. Intenta con: `npm run dev -- --port 5174`

### Los datos no se actualizan
**Solución:**
1. Ejecuta `python send_data.py` en Terminal 3
2. Presiona F5 en el navegador para refrescar

---

##🎯 Flujo Completo

```
TERMINAL 1          TERMINAL 2          TERMINAL 3
   API              Frontend            (Opcional)
   |                  |                    |
python              npm run dev         python send_data.py
main.py             en puerto 5173      genera datos
en puerto 8000
   |                  |                    |
   ↓                  ↓                    ↓
http:/              http://           Envía requests
localhost:          localhost:         POST a la API
8000                5173
```

---

## 📱 Navegación en la App

1. **Pantalla Principal** - Lista de 8 acciones con señales
   - BUY LONG = Precio va a subir (verde)
   - SELL SHORT = Precio va a bajar (rojo)
   - HOLD = Mantener posición (amarillo)

2. **Clic en acción** - Ver detalles:
   - Gráfico de precios (30, 60, 90 días)
   - Métricas del modelo
   - Historial de señales

3. **Rendimiento** - Dashboard global:
   - Comparación de acciones
   - Tabla con métricas detalladas
   - Precisión promedio

4. **Acerca de** - Información legal y disclaimers

---

## 📚 Archivos Importantes

- `API_LOCAL_SETUP.md` - Guía detallada de setup
- `SETUP_COMPLETADO.md` - Análisis de cambios realizados
- `api/README.md` - Documentación de API endpoints
- `api/model_integration_example.py` - Cómo integrar tus modelos

---

## ✅ Checklist

- [ ] Instalé Flask y Flask-CORS
- [ ] Ejecuté `python main.py` en Terminal 1
- [ ] Ejecuté `npm run dev` en Terminal 2
- [ ] Abrí http://localhost:5173 en navegador
- [ ] Veo las 8 acciones con señales
- [ ] La app carga datos correctamente

Si completaste todo ✅, tu setup está listo!

---

## 🎓 Próximos Pasos

Cuando tengas tus modelos LSTM/CNN-LSTM:

1. Lee: `api/model_integration_example.py`
2. Modifica `api/main.py` para importar tus modelos
3. Reemplaza datos aleatorios con predicciones reales
4. Integra APIs financieras (Yahoo Finance, etc.)

¡Listo para empezar! 🚀
