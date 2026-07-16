FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV API_HOST=0.0.0.0 \
    API_PORT=8000 \
    FLASK_DEBUG=0 \
    DATABASE_URL=sqlite:////data/trading_system.db

# La app escribe el .db aqui; monta un volumen en /data para persistir entre reinicios.
RUN mkdir -p /data
VOLUME ["/data"]

EXPOSE 8000

# gunicorn con un solo worker: el scheduler en memoria (start_scheduler() en
# main.py, disparado por wsgi.py) correria N veces con N workers. $PORT lo
# inyecta Render en produccion; localmente (docker-compose) cae a API_PORT.
# --timeout 300: gunicorn mata y reinicia un worker que no "avisa" (heartbeat)
# en ese lapso, y eso incluye el tiempo de carga inicial de wsgi.py
# (initialize_data() con reintentos, ver FETCH_RETRY_* en main.py) antes de
# que el worker llegue a servir su primer request.
CMD gunicorn --bind 0.0.0.0:${PORT:-$API_PORT} --workers 1 --timeout 300 wsgi:app
