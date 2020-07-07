from app import app, db
from app.models.service import Service


def create_services():
    """
    Creates all given services on service table.
    """
    # Ingest service record
    ingest_service = Service.find_by_name('Ingest')
    if not ingest_service:
        ingest_service = Service(name='Ingest', ip_address=app.config['INGEST_HOST'],
                                 port=app.config['INGEST_PORT'])
        try:
            ingest_service.save_to_db()
        except Exception as e:
            db.session.rollback()
            return {'status': False, 'response': str(e)}

    # PostgeSQL service record
    psql_service = Service.find_by_name('PostgreSQL')
    if not psql_service:
        psql_service = Service(name='PostgreSQL', ip_address='127.0.0.1', port=5432)
        try:
            psql_service.save_to_db()
        except Exception as e:
            db.session.rollback()
            return {'status': False, 'response': str(e)}

    # RabbitMQ service record
    rabbit_service = Service.find_by_name('RabbitMQ')
    if not rabbit_service:
        rabbit_service = Service(name='RabbitMQ', ip_address='127.0.0.1', port=5009)
        try:
            rabbit_service.save_to_db()
        except Exception as e:
            db.session.rollback()
            return {'status': False, 'response': str(e)}

    return {'status': True, 'response': 'Services stored'}
