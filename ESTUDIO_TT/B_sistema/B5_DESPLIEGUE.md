# B5 — Despliegue, operación y control de versiones

> **Resumen.** El sistema está en **Render** como dos servicios: la API en
> un contenedor **Docker** con **gunicorn** (1 worker) y el frontend como
> sitio estático. Ambos se definen en `render.yaml` y se despliegan solos
> con cada `push` a la rama `main` de GitHub. En local se levanta todo con
> `docker compose`. Se resolvieron problemas reales de operación: arranque
> en frío y fallas de Yahoo.
>
> Documento técnico: `docs/DEPLOY_RENDER.md`.

---

## 1. Dónde está

| Servicio | Tipo en Render | URL |
|---|---|---|
| `tt-api` | Web service, Docker, plan gratuito, 1 instancia | `https://tt-api-jc7n.onrender.com` |
| `tt-frontend` | Static site | `https://tt-frontend-womf.onrender.com` |

Verificación después de un despliegue: `GET /health` debe decir
`stocksLoaded: 7` y `GET /model` debe decir `LR-v8-interactions-holdw090`.

---

## 2. Piezas

### 2.1 Docker (`api/Dockerfile`)

- Imagen base `python:3.13-slim`; instala `api/requirements.txt` con
  versiones fijas (por ejemplo, scikit-learn 1.7.2, la misma del
  entrenamiento, para que el `.pkl` cargue igual).
- Variables por defecto: `FLASK_DEBUG=0`, base en `/data/trading_system.db`.
- Comando: `gunicorn --workers 1 --timeout 300 wsgi:app`.

**Por qué Docker:** la API corre igual en la computadora y en la nube, con
las mismas versiones de todo.

### 2.2 gunicorn y por qué 1 solo worker

- gunicorn es el servidor de producción (el servidor de Flask es solo para
  desarrollo).
- **1 worker y 1 instancia** porque el programador de tareas (APScheduler)
  vive dentro del proceso: con N workers la actualización diaria correría N
  veces a la vez. Para una API de lectura con pocos usuarios, 1 worker basta.
- `--timeout 300`: la primera carga (descargar y calcular todo, con
  reintentos) puede tardar; sin ese margen gunicorn mataría al worker antes
  de que empiece a responder.
- `wsgi.py` es la entrada: corre `initialize_data()` y arranca el
  programador una vez, antes de servir.

**Si hubiera que escalar:** sacar la actualización a un *cron job* externo
que llame `POST /admin/refresh` una vez, y entonces sí usar varios workers.

### 2.3 `render.yaml` (Blueprint)

Describe ambos servicios: tipo, rama (`main`), despliegue automático,
ruta de salud (`/health`), variables de entorno, la regla de reescritura del
frontend (todas las rutas → `index.html`). Solo se despliegan `api/` y `Frontend/`; el código de
investigación no se sube a producción porque no es un servicio.

### 2.4 `docker-compose.yml` (local)

Levanta la API (puerto 8000, con volumen `/data` para que la base
persista) y el frontend con nginx (puerto 8080). Tiene un **perfil opcional
con PostgreSQL 15** (`docker compose --profile postgres up -d`) para
probar el cambio de motor; las contraseñas se leen de `.env`, no están en
el código.

### 2.5 Git y GitHub

- Repositorio `barudust/TT`.
- Ramas: **`main`** (la que despliega Render) y **`dev`** (trabajo). Las
  ramas personales (`Baru`, `David`) se fusionaron y se borraron.
- Cada cambio relevante tiene un commit descriptivo; el historial documenta
  la evolución del proyecto.

---

## 3. Problemas reales que se resolvieron

| Problema | Causa | Solución |
|---|---|---|
| La API tarda 20–40 s la primera vez | El plan gratuito "duerme" el servicio tras ~15 min sin tráfico; al despertar recalcula todo | Esperado; se documenta. El frontend muestra estado de carga |
| Catálogo vacío después de desplegar (`/stocks` = `[]`) | Yahoo falló justo en el arranque en frío | Reintentos (3 por descarga) + reintento automático cada 2 min mientras falten acciones + `stocksLoaded` en `/health` + el frontend dispara `POST /admin/refresh` si llega vacío. Verificado el 30 de septiembre: se reparó solo en ~2 min |
| `render.yaml` decía `branch: dev` pero se desplegaba `main` | Manda la rama configurada en el panel | Se corrigió el archivo para que coincidan |
| La actualización diaria no corre si el servicio está dormido | Plan gratuito | Documentado; solución: plan pago o un cron job externo que llame `POST /admin/refresh` |
| Base de datos se pierde al reiniciar | Sin disco persistente en el plan gratuito | Aceptable: la base es reconstruible (ver [B3](B3_BASE_DE_DATOS.md)) |

---

## 3b. Respecto al TT1

En TT1 el sistema solo corría en local (PostgreSQL, Flask y React en tres
puertos de la misma máquina) y desplegarlo era trabajo futuro (§5.10: "la
aplicación web se encuentra en fase de desarrollo local"). Ahora está en
Render con despliegue automático, contenedor Docker, pruebas y manejo de
fallas reales.

---

## 4. Cómo correr todo localmente

```bash
# API (http://localhost:8000)
pip install -r api/requirements.txt
python api/main.py

# Frontend (http://localhost:5173)
npm --prefix Frontend install
npm --prefix Frontend run dev

# Pruebas de la API (23)
pip install -r api/requirements-dev.txt
cd api && pytest

# Todo con Docker (API :8000, frontend :8080)
docker compose up -d --build

# Regenerar el modelo de producción
python scripts_opt/entrenar_produccion.py
```

**Si se reentrena el modelo:** actualizar `MODEL_VERSION` en
`api/ml/model.py` (hay una prueba que falla si no coincide con el `.pkl`).

---

## 5. Seguridad (lo que hay y lo que falta)

| Aspecto | Estado |
|---|---|
| Secretos fuera del código | Sí: `.env` y variables del panel de Render; `.env` en `.gitignore` |
| Escritura manual de datos | Desactivada por defecto (403) |
| HTTPS | Lo da Render |
| CORS | Abierto: la API es pública y de solo lectura |
| `POST /admin/refresh` sin autenticación | Pendiente: solo recalcula con datos públicos, pero convendría una llave |
| Documentos sujetos a licencia (paper) | El PDF con licencia de Springer y el formulario firmado no se suben al repositorio público |

---

## Preguntas de este tema

Están desarrolladas en [D6](../D_defensa/D6_PREGUNTAS_SISTEMA.md).
