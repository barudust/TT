from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    # URI para Docker local. En Azure se cambiará por la URL de producción
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user_admin:password123@localhost:5432/stocks_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate.init_app(app, db)