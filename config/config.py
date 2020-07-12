import os

from dotenv import load_dotenv


class Config(object):
    """
    Config file loads variable values from .env (dotenv) file
    """
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    # Flask app Configuration
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')

    # SQLAlchemy Configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = ''.join(
        ['postgresql://', os.getenv('DT_USER'), ':', os.getenv('DT_KEY'), '@localhost/dt_db'])
    BIND_CONNECTION_STRING = ''.join(
        ['postgresql://', os.getenv('INGEST_USER'), ':', os.getenv('INGEST_KEY'), '@localhost/ingest_db'])
    # Bind to a second database (fetch event table)
    SQLALCHEMY_BINDS = {
        'ingest_db': BIND_CONNECTION_STRING
    }

    # Tests Configuration
    TESTS_URL = 'https://127.0.0.1:5000'

    # RabbitMQ Configuration
    RMQ_HOST = os.getenv('RMQ_HOST')
    RMQ_PORT = os.getenv('RMQ_PORT')
    RMQ_USERNAME = os.getenv('RMQ_USERNAME')
    RMQ_PASSWORD = os.getenv('RMQ_PASSWORD')
    RMQ_RETRY = os.getenv('RMQ_RETRY')

    # Ingest Configuration
    INGEST_HOST = os.getenv('INGEST_HOST')
    INGEST_PORT = os.getenv('INGEST_PORT')
    PUSH_BACK_TIMEOUT = os.getenv('PUSH_BACK_TIMEOUT')
    RANDOMIZED_SET_SCALE = os.getenv('RANDOMIZED_SET_SCALE')

    # Tasks Configuration
    PERIODIC_INTEGRITY_TIMEOUT = os.getenv('PERIODIC_INTEGRITY_TIMEOUT')
    HEARTBEAT_TIMEOUT = os.getenv('HEARTBEAT_TIMEOUT')
