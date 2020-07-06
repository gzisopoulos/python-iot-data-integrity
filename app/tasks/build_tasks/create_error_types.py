from app import db
from app.models.error_type import ErrorType


def create_error_types():
    """
    Creates all given error types.
    """
    # Broken GPS error.
    broken_gps = ErrorType.find_by_error_code(1)
    if not broken_gps:
        broken_gps = ErrorType(error_code=1, description='Broken GPS', limit=5)
        try:
            broken_gps.save_to_db()
        except Exception as e:
            db.session.rollback()
            return {'status': False, 'response': str(e)}

    # Event code not exist
    wrong_code = ErrorType.find_by_error_code(2)
    if not wrong_code:
        wrong_code = ErrorType(error_code=2, description='Wrong Event Code', limit=5)
        try:
            wrong_code.save_to_db()
        except Exception as e:
            db.session.rollback()
            return {'status': False, 'response': str(e)}

    return {'status': True, 'response': 'Error Types stored'}
