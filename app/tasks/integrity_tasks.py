import asyncio

import json
import datetime

from collections import namedtuple

from app import app, db
from app.tasks.task_utils import duplicate_trace
from app.models.error_trace import ErrorTrace
from app.models.error_type import ErrorType
from app.models.event import Event
from app.models.event_format import EventFormat


async def periodic_integrity_task(timeout):
    """
    Fetches a random set of events and applies integrity check
    """
    while True:
        await asyncio.sleep(int(timeout))
        start = datetime.datetime.now()
        app.logger.info('Integrity Task started at: %s' % (str(start.strftime('%Y-%m-%d %H:%M:%S'))))
        corrupted_events = 0
        events_count = Event.get_count()
        randomized_set = Event.get_randomized_set(events_count)

        if randomized_set:
            for event in randomized_set:
                event_integrity_ok = await check_quality(event)
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


async def check_quality(event):
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

    if duplicate_trace(decoded_event):
        return False

    # Case 1: Range of lat and lon.
    if wrong_coordinates(decoded_event.longitude, decoded_event.latitude):
        error_trace = ErrorTrace(device_number=decoded_event.device_number,
                                 error_code=1,
                                 event_code=decoded_event.event_code,
                                 message_date=decoded_event.message_date)
        try:
            error_trace.save_to_db()
            error_traces_list.append(error_trace)
        except Exception as e:
            db.session.rollback()
            app.logger.warning('Error on INSERT to ErrorTrace: %s' % (str(e)))

    if event_code_exists(decoded_event.event_code):
        error_trace = ErrorTrace(device_number=decoded_event.device_number,
                                 error_code=2,
                                 event_code=decoded_event.event_code,
                                 message_date=decoded_event.message_date)
        try:
            error_trace.save_to_db()
            error_traces_list.append(error_trace)
        except Exception as e:
            db.session.rollback()
            app.logger.warning('Error on INSERT to ErrorTrace: %s' % (str(e)))

    # Notify for device corruption if the error type limit is reached.
    if error_traces_list:
        for error_trace in error_traces_list:
            error_type = ErrorType.find_by_error_code(error_trace.error_code)
            if error_type:
                if notify_for_device_check(decoded_event.device_number, error_type.error_code, error_type.limit):
                    app.logger.warning('Device %s reached limit for error code %s (%s)' %
                                       (decoded_event.device_number, error_type.error_code, error_type.description))

    if error_traces_list:
        event_quality_ok = False
    # Return the flag after KPI checks
    return event_quality_ok


def event_code_exists(event_format):
    """
    Checks if code exists in EventFormat.
    """
    event_format = EventFormat.find_by_event_code(event_format)
    if event_format:
        return True
    else:
        return False


def wrong_coordinates(longitude, latitude):
    if not longitude:
        longitude = 0
    if not latitude:
        latitude = 0
    if (float(longitude) > 90 or float(longitude) < -90 or
            float(latitude) > 180 or float(latitude) < -180):
        return True


def notify_for_device_check(device_number, error_code, limit):
    """
    Checks if this devices has reached the limit of times for specific error_code
    """
    error_traces = ErrorTrace.query.filter(ErrorTrace.device_number == device_number).filter(
        ErrorTrace.error_code == error_code).all()
    if len(error_traces) >= limit:
        return True
    else:
        return False
