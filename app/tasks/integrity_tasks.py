import asyncio
import json
import datetime
import sqlalchemy

from collections import namedtuple

from app import app, db
from app.models.error_trace import ErrorTrace
from app.models.error_type import ErrorType
from app.models.event import Event
from app.models.event_format import EventFormat
from app.tasks.task_utils import bind_to_service
from app.tasks.build_tasks.create_error_types import create_error_types
from app.tasks.build_tasks.create_event_formats import create_event_formats


async def periodic_integrity_task(psql_service, timeout):
    """
    Fetches a random set of events and applies integrity check
    """
    while True:
        await asyncio.sleep(int(timeout))
        start = datetime.datetime.now()

        # run this task only if postgresql is up
        if bind_to_service(psql_service['ip_address'], psql_service['port']):
            app.logger.info('Integrity Task started at: %s' % (str(start.strftime('%Y-%m-%d %H:%M:%S'))))
            corrupted_events = 0
            # get a randomized set to apply checks
            events_count = Event.get_count()
            randomized_set = Event.get_randomized_set(events_count)
            if randomized_set:
                for event in randomized_set:
                    try:
                        event_integrity_ok = check_quality(event)
                    # rollback broken transaction if something goes wrong during query
                    except sqlalchemy.exc.StatementError:
                        db.session.rollback()
                        app.logger.warning('Rolling back db transaction. Retrying in %s seconds...' % (str(timeout)))
                        await asyncio.sleep(int(timeout))
                        continue
                    if not event_integrity_ok:
                        corrupted_events += 1
                if corrupted_events:
                    total_time = int((datetime.datetime.now() - start).microseconds / 1000)
                    app.logger.warning('Checked: %s random events in %s ms. Corrupted: %s' % (
                        str(len(randomized_set)), str(total_time), str(corrupted_events)))

                else:
                    total_time = int((datetime.datetime.now() - start).microseconds / 1000)
                    app.logger.info('Checked: %s random events in %s ms. Everything ok.' % (
                        str(len(randomized_set)), str(total_time)))
            else:
                app.logger.info('Integrity Task - Something went wrong. Retrying in %s seconds..' % (str(timeout)))
        else:
            app.logger.info('Integrity Task - Database is down. Retrying in %s seconds..' % (str(timeout)))


def check_quality(event):
    """
    Transforms event of rabbitmq event into an immutable object and applies some checks.
    """
    error_traces_list = []
    event_quality_ok = True

    # if event is string then check event integrity was called from consumer

    if isinstance(event, str) or isinstance(event, bytes):
        decoded_event = json.loads(event, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    else:
        decoded_event = event

    # Case 1: Range of lat and lon
    if wrong_coordinates(decoded_event.longitude, decoded_event.latitude):
        error_trace = ErrorTrace(device_number=decoded_event.device_number,
                                 error_code=1,
                                 message_date=decoded_event.message_date)
        try:
            if not duplicate_trace(error_trace):
                error_trace.save_to_db()
                error_traces_list.append(error_trace)
        except Exception as e:
            db.session.rollback()
            app.logger.warning('Error on INSERT to ErrorTrace: %s' % (str(e)))
    # Case 2: Event code doesn't matching with any format
    if not event_code_exists(decoded_event.event_code):
        error_trace = ErrorTrace(device_number=decoded_event.device_number,
                                 error_code=2,
                                 message_date=decoded_event.message_date)
        try:
            if not duplicate_trace(error_trace):
                error_trace.save_to_db()
                error_traces_list.append(error_trace)
        except Exception as e:
            db.session.rollback()
            app.logger.warning('Error on INSERT to ErrorTrace: %s' % (str(e)))

    # Notify for device corruption if the error type limit is reached.
    if error_traces_list:
        for error_trace in error_traces_list:
            all_types = ErrorType.query.all()
            # Check if error types are created properly
            if not all_types:
                create_error_types()
            error_type = ErrorType.find_by_error_code(error_trace.error_code)
            if not error_type:
                if notify_for_device_check(decoded_event.device_number, error_type.error_code, error_type.limit):
                    app.logger.warning('Device %s reached limit for error code %s (%s)' %
                                       (decoded_event.device_number, error_type.error_code, error_type.description))
    if error_traces_list:
        event_quality_ok = False
    # Return the flag after KPI checks
    return event_quality_ok


def event_code_exists(event_code):
    """
    Checks if code exists in EventFormat.
    """
    # Check if all formats created properly
    all_formats = EventFormat.query.all()
    if not all_formats:
        create_event_formats()
    event_format = EventFormat.find_by_event_code(event_code)
    if event_format:
        return True
    else:
        return False


def wrong_coordinates(longitude, latitude):
    """
    Check if coordinates are wrong and if longitude and latitude are correct
    """
    try:
        lon = float(longitude)
        lat = float(latitude)
    # Value error will be raised when longitude or latitude can not be converted to float
    except ValueError:
        db.session.rollback()
        return True
    # Value error will be raised when longitude or latitude value is None
    except TypeError:
        return True

    # check if longitude and latitude are within coordinates values range
    if lon > 90 or lon < -90 or lat > 180 or lat < -180:
        return True
    else:
        return False


def notify_for_device_check(device_number, error_code, limit):
    """
    Checks if this devices has reached the limit of times for specific error_code
    """
    error_traces = ErrorTrace.query.filter(ErrorTrace.device_number == device_number).filter(
        ErrorTrace.error_code == error_code).all()
    # look for similar error traces and if they reach this error type's limit notify.
    if len(error_traces) >= limit:
        return True
    else:
        return False


def duplicate_trace(new_error_trace):
    """
    Checks if the trace already exists.
    """
    error_trace = ErrorTrace.query.filter(ErrorTrace.device_number == new_error_trace.device_number).filter(
        ErrorTrace.message_date == new_error_trace.message_date).first()
    if error_trace:
        return True
    else:
        return False