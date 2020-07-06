from app import db
from app.models.event_format import EventFormat


def create_event_formats():
    """
    Creates all given formats on event format table.
    """
    # Ignition on event format
    ignition_on = EventFormat.find_by_event_code(7000)
    if not ignition_on:
        ignition_on = EventFormat(event_code=7000, event_description='Ignition On')
        try:
            ignition_on.save_to_db()
        except Exception as e:
            db.session.rollback()
            return {'status': False, 'response': str(e)}

    # Ignition off event format
    ignition_off = EventFormat.find_by_event_code(7003)
    if not ignition_off:
        ignition_off = EventFormat(event_code=7003, event_description='Ignition Off')
        try:
            ignition_off.save_to_db()
        except Exception as e:
            db.session.rollback()
            return {'status': False, 'response': str(e)}

    # Acceleration event format
    acceleration = EventFormat.find_by_event_code(7001)
    if not acceleration:
        acceleration = EventFormat(event_code=7001, event_description='Acceleration')
        try:
            acceleration.save_to_db()
        except Exception as e:
            db.session.rollback()
            return {'status': False, 'response': str(e)}

    # Deceleration event format
    deceleration = EventFormat.find_by_event_code(7002)
    if not deceleration:
        deceleration = EventFormat(event_code=7002, event_description='Deceleration')
        try:
            deceleration.save_to_db()
        except Exception as e:
            db.session.rollback()
            return {'status': False, 'response': str(e)}

    return {'status': True, 'response': 'Event formats stored'}
