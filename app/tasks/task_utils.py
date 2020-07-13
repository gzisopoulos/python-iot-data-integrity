import re
import socket

from app.models.error_trace import ErrorTrace


def bind_to_service(ip_address, port):
    """
    Bind to specific address. If it is in use then service is up
    """
    address = (ip_address, port)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(address)
        status = False
    except OSError:
        status = True
    return status

