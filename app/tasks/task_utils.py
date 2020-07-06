import re
import socket

from app.models.error_trace import ErrorTrace


def duplicate_trace(decoded_event):
    """
    Checks if the trace already exists.
    """
    error_trace = ErrorTrace.query.filter(ErrorTrace.device_number == decoded_event.device_number).filter(
        ErrorTrace.event_code == decoded_event.event_code).filter(
        ErrorTrace.message_date == decoded_event.message_date).first()
    if error_trace:
        return True
    else:
        return False


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


def bind_to_service(ip_address, port):
    address = (ip_address, port)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(address)
        status = False
    except OSError:
        status = True
    return status

