import asyncio
import aioamqp
import socket

from app import app
from app.models.service import Service
from app.tasks.integrity_tasks import check_quality
from app.tasks.task_utils import bind_to_service


async def callback(channel, body, envelope, properties):
    """
    Handles incoming event from RabbitMQ.
    """
    event_not_corrupted = await check_quality(body)
    ingest = Service.find_by_name('Ingest')
    if ingest:
        address = ingest.ip_address
        port = ingest.port
    else:
        address = app.config['INGEST_HOST']
        port = app.config['INGEST_PORT']
    push_back_services_up = bind_to_service(address, port)
    if event_not_corrupted:
        if not push_back_services_up:
            app.logger.warning('Ingest is down: Retrying in %s seconds...' % (app.config['PUSH_BACK_TIMEOUT']))
            await asyncio.sleep(int(app.config['PUSH_BACK_TIMEOUT']))
            await callback(channel, body, envelope, properties)
        await push_back_event(body, channel, envelope)
    else:
        app.logger.info('Event corrupted or unaccceptable')


async def consume(**kwargs):
    """
    Connects RabbitMQ and receives events from queue.
    """
    wait_seconds = kwargs.get('wait_seconds', None)

    if wait_seconds:
        await asyncio.sleep(int(wait_seconds))

    try:
        transport, protocol = await aioamqp.connect(
            host=str(app.config['RMQ_HOST']),
            port=int(app.config['RMQ_PORT']),
            login=str(app.config['RMQ_USERNAME']),
            password=str(app.config['RMQ_PASSWORD']),
            login_method='PLAIN'
        )
    except aioamqp.AmqpClosedConnection:
        app.logger.info('closed connections')
        await consume(wait_seconds=app.config['RMQ_RETRY'])
    except ConnectionRefusedError:
        app.logger.info('RabbitMQ is down. Retrying in %s seconds' %
                        (str(app.config['RMQ_RETRY'])))
        await consume(wait_seconds=app.config['RMQ_RETRY'])

    app.logger.info('Connected on %s:%s' % (
        str(app.config['RMQ_HOST']),
        str(app.config['RMQ_PORT'])))

    try:
        channel = await protocol.channel()
        app.logger.info('Channel Created.')
    except Exception as e:
        app.logger.info('Error on channel creation:\n' % (str(e)))
        await consume(wait_seconds=app.config['RMQ_RETRY'])

    try:
        await channel.queue_declare(
            queue_name='events',
            durable=True,
            passive=False,
            exclusive=True
        )
    except Exception as e:
        app.logger.info('Error on queue creation:\n' % (str(e)))
        await consume(wait_seconds=app.config['RMQ_RETRY'])

    # Infinite consume after run forever loop
    await channel.basic_consume(callback, queue_name='events')


async def push_back_event(body, channel, envelope):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((app.config['INGEST_HOST'], int(app.config['INGEST_PORT'])))
            s.sendall(body)
            data = s.recv(1024)
            s.close()
            await channel.basic_client_ack(envelope.delivery_tag)
            app.logger.info('Event Pushed back to Elixir Ingest')
        except ConnectionRefusedError:
            app.logger.info('Elixir Ingest Service Down. Event pushed back to queue')
            # TODO - Add redeliver tag to event.
