import asyncio

from app import app
from app.tasks.check_heartbeat import check_heartbeat
from app.tasks.consumer_tasks import consume
from app.tasks.integrity_tasks import periodic_integrity_task
from app.tasks.build_tasks.create_error_types import create_error_types
from app.tasks.build_tasks.create_services import create_services
from app.tasks.build_tasks.create_event_formats import create_event_formats

# Initialize dt_db
create_services()
create_error_types()
create_event_formats()

# AsyncIO Configuration
app.logger.info('Starting Python IOT Data Integrity. Creating services, formats and error types.')

try:
    dt_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(dt_loop)
except RuntimeError:
    app.logger.warning('No available loop')

dt_tasks = asyncio.gather(
    consume(),
    periodic_integrity_task(app.config['PERIODIC_INTEGRITY_TIMEOUT']),
    check_heartbeat(app.config['HEARTBEAT_TIMEOUT'])
)
try:
    dt_loop.run_forever()
except KeyboardInterrupt:
    app.logger.info('Canceling Tasks..')
    dt_tasks.cancel()
    app.logger.info('Closing App. Bye')
