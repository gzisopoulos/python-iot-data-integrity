from app import app, db
from app.models.service import Service


def create_services():
    """
    Gathers all services info inside a dict.
    """
    # We prefer our integrity module to be independent from db
    # Here you may use redis or something like this as storage solution
    services_dict = {
        'Ingest': {
            'ip_address': app.config['INGEST_HOST'],
            'port': int(app.config['INGEST_PORT'])
        },
        'PostgreSQL': {
            'ip_address': app.config['POSTGRESQL_HOST'],
            'port': int(app.config['POSTGRESQL_PORT'])
        },
        'RabbitMQ': {
            'ip_address': app.config['RMQ_HOST'],
            'port': int(app.config['RMQ_PORT'])
        }
    }

    return services_dict
