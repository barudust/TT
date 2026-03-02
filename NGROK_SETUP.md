# Configuración de ngrok para TradingSignals AI

Esta guía te ayuda a configurar ngrok para exponer la app y la API simultáneamente en Android.

## Paso 1: Crear cuenta en ngrok

1. Ve a https://ngrok.com/signup
2. Crea una cuenta gratuita
3. Verifica tu email

## Paso 2: Obtener tu Auth Token

1. Inicia sesión en https://dashboard.ngrok.com
2. Ve a "Your Authtoken" en el menú izquierdo
3. Copia el token (ej: `26_XXXXXXXXXXXXXXXXXXXXX`)

## Paso 3: Configurar ngrok en tu máquina

### Windows/Mac/Linux:

```bash
# Instalar ngrok si no lo tienes
# Descarga desde: https://ngrok.com/download

# O si tienes Homebrew (Mac):
brew install ngrok

# O si tienes Chocolatey (Windows):
choco install ngrok
```

## Paso 4: Crear archivo de configuración

Copia `ngrok.example.yml` a `ngrok.yml` en la raíz del proyecto:

```bash
cp ngrok.example.yml ngrok.yml
```

Edita `ngrok.yml` y reemplaza `YOUR_NGROK_AUTH_TOKEN_HERE` con tu token:

```yaml
version: "3"
authtoken: 26_XXXXXXXXXXXXXXXXXXXXX    <-- TU TOKEN AQUÍ

tunnels:
  api:
    proto: http
    addr: 8000

  app:
    proto: http
    addr: 5173
```

## Paso 5: Ejecutar ngrok

En la carpeta del proyecto:

```bash
ngrok start --all
```

Verás algo como esto:

```
Session Status                online
Session Expires               2 hours, 59 minutes
Version                       3.8.0
Region                        us (United States)
Latency                       45ms
Web Interface                 http://127.0.0.1:4040

Forwarding                    https://1234-56-78-90.ngrok-free.app -> http://localhost:8000
Forwarding                    https://5678-90-12-34-56.ngrok-free.app -> http://localhost:5173
```

## Paso 6: Ejecutar la app y la API

En 2 terminales separadas:

**Terminal 1: API (Python)**
```bash
cd api
python main.py
```

**Terminal 2: App (React)**
```bash
npm run dev
```

## Paso 7: Conectar desde Android

### Opción A: app sin ngrok, API por ngrok (RECOMENDADO)

1. En tu celular, edita `.env.local`:
   - Copia `VITE_API_URL=https://1234-56-78-90.ngrok-free.app` (la URL de la API)

2. Abre en el navegador del celular:
   ```
   http://localhost:5173
   ```
   (o la IP local de tu PC si está en otra red)

3. Menú → "Instalar app"

### Opción B: app Y API por ngrok

1. Abre en el navegador del celular:
   ```
   https://5678-90-12-34-56.ngrok-free.app
   ```
   (la URL de la app desde ngrok)

2. La app detectará automáticamente que está en esa URL
3. Edita `.env.local` con la URL de la API:
   ```
   VITE_API_URL=https://1234-56-78-90.ngrok-free.app
   ```

4. Menú → "Instalar app"

## Archivo .env.local

El archivo `.env.local` es para especificar URLs personalizadas:

```
# Ejemplo: si tu API está en ngrok
VITE_API_URL=https://1234-56-78-90.ngrok-free.app

# La app detectará automáticamente:
# - Si está en localhost → usa http://localhost:8000
# - Si está en otro dominio → usa ese dominio:8000
```

## Notas Importantes

⚠️ **ngrok gratuito tiene limitaciones:**
- Las URLs son temporales (cambian cada vez que ejecutas)
- Límite de 1 sesión simultánea (usa múltiples endpoints en el mismo archivo)
- Velocidad limitada

✅ **Soluciones:**
- Usa Cloudflare Tunnel (gratis, sin límites)
- Compra plan pagado de ngrok
- Despliega en producción (Vercel, Netlify, etc)

## Troubleshooting

**"Unable to parse configuration file"**
- Verifica que el YAML válido (sin tabs, solo espacios)
- Usa: https://www.yamllint.com/

**"You have connected from a new IP"**
- ngrok puede pedirte verificar desde dashboard.ngrok.com
- Sigue las instrucciones

**"Connection refused"**
- Verifica que la API esté corriendo: `python main.py`
- Verifica que la app esté corriendo: `npm run dev`
