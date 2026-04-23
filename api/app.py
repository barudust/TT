from flask import Flask
from database import db, init_db
import models # Carga los modelos para Alembic

app = Flask(__name__)
init_db(app)

# Tus rutas existentes de la API...