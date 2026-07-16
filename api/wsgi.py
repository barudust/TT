"""Punto de entrada para gunicorn (Docker/Render).

`main.py` no dispara `initialize_data()`/`start_scheduler()` al importarse
(solo dentro de `if __name__ == "__main__"`) para que los tests puedan hacer
`import main` sin red ni scheduler real. Este modulo es el que gunicorn
carga (`gunicorn wsgi:app`) y se encarga de correr esa inicializacion una
sola vez por worker antes de servir requests.
"""
from main import app, initialize_data, start_scheduler

initialize_data()
start_scheduler()
