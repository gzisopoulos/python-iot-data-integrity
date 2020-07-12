import asyncio
import datetime

from app import app
from app.models.service import Service
from app.tasks.task_utils import bind_to_service


async def check_heartbeat(timeout):
    """
    Fetches all available services and binds to their ports in order to check if their are up.
    """
    while True:
        await asyncio.sleep(int(timeout))
        start = datetime.datetime.now()
        # TODO - Remove after europython
        app.logger.info('Heartbeat Task started at: %s' % (str(start.strftime('%Y-%m-%d %H:%M:%S'))))
        services = Service.query.all()
        if services:
            response = ''
            for service in services:
                running = bind_to_service(service.ip_address, service.port)
                if not running:
                    response = response + service.name + ' '
            if response:
                total_time = int((datetime.datetime.now() - start).microseconds / 1000)
                app.logger.info('Finished in %s ms. DOWN: %s' % (str(total_time), response))
            else:
                total_time = int((datetime.datetime.now() - start).microseconds / 1000)
                app.logger.info('Finished in %s ms. Core heartbeat: OK' % (str(total_time)))
        else:
            # If no service found iterate
            app.logger.info('No Services found. Re-fetching...')
        # Sleep until next iteration.
