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
CMD gunicorn --bind 0.0.0.0:${PORT:-$API_PORT} --workers 1 --timeout 120 wsgi:app
