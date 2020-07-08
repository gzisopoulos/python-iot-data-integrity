import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    return app


app = create_app()
db = SQLAlchemy(app)

dt_logger = logging.getLogger('dt_logger')
app.logger.handlers.extend(dt_logger.handlers)
logging.getLogger().setLevel(logging.INFO)

# There are different ways to create an init file.
# From our point of view this is one of the simplest
from app.routes import routes
