import asyncio
import datetime

from app import app
from app.tasks.task_utils import bind_to_service
from app.tasks.build_tasks.create_services import create_services


async def check_heartbeat(services_dict, timeout):
    """
    Fetches all available services and binds to their ports in order to check if their are up.
    """
    while True:
        # Periodic task with infinite loop and timeout
        await asyncio.sleep(int(timeout))
        # These datetimes are used only for logging
        start = datetime.datetime.now()
        app.logger.info('Heartbeat Task started at: %s' % (str(start.strftime('%Y-%m-%d %H:%M:%S'))))
        if services_dict:
            # build a response for hartbeat task
            response = ''
            for service_name in services_dict.keys():
                running = bind_to_service(services_dict[service_name]['ip_address'], services_dict[service_name]['port'])
                # if one service is down build the response with every not running service name
                # this is a simple log notification. You may want to send an email to your admin
                if not running:
                    response = response + service_name + ' '
            if response:
                # Total time is only for logging purposes
                total_time = int((datetime.datetime.now() - start).microseconds / 1000)
                app.logger.info('Finished in %s ms. DOWN: %s' % (str(total_time), response))
            else:
                total_time = int((datetime.datetime.now() - start).microseconds / 1000)
                app.logger.info('Finished in %s ms. Core heartbeat: OK' % (str(total_time)))
        else:
            # If no service found iterate
            app.logger.info('No Services found. Re-fetching...')
            services_dict = create_services()
        # Sleep until next iteration.
