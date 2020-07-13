from app import db
from app.models.error_type import ErrorType
from app.tasks.task_utils import bind_to_service


def create_error_types(psql_service):
    """
    Creates all given error types.
    """
    # Save only if database is up
    if bind_to_service(psql_service['ip_address'], psql_service['port']):
        # Broken GPS error.
        broken_gps = ErrorType.find_by_error_code(1)
        if not broken_gps:
            broken_gps = ErrorType(error_code=1, description='Broken GPS', limit=5)
            try:
                broken_gps.save_to_db()
            except Exception as e:
                db.session.rollback()
                return 'Error:' + str(e)

        # Event code not exist
        wrong_code = ErrorType.find_by_error_code(2)
        if not wrong_code:
            wrong_code = ErrorType(error_code=2, description='Wrong Event Code', limit=5)
            try:
                wrong_code.save_to_db()
            except Exception as e:
                db.session.rollback()
                return 'Error:' + str(e)

        return 'All types created'
    else:
        return 'Database is down'