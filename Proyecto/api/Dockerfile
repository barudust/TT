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

# Servidor de desarrollo de Flask (sin reloader, sin debugger): suficiente
# para esta demo de tesis. Para produccion real, cambiar a gunicorn con un
# solo worker (ver nota sobre el scheduler en start_scheduler() en main.py).
CMD ["python", "main.py"]
