import logging
import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv


def create_app():
    app = Flask(__name__)
    dotenv_path = os.path.join(os.path.dirname(app.root_path), 'config/.env')
    load_dotenv(dotenv_path)
    app.config.from_object('config.Config')
    return app


app = create_app()
db = SQLAlchemy(app)
migrate = Migrate(app, db)

alfred_logger = logging.getLogger('alfred_logger')
app.logger.handlers.extend(alfred_logger.handlers)
logging.getLogger().setLevel(logging.INFO)


from app.routes import routes
