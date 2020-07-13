import asyncio
import aioamqp
import socket
import sqlalchemy

from app import app, db
from app.models.service import Service
from app.tasks.integrity_tasks import check_quality
from app.tasks.task_utils import bind_to_service


async def callback(channel, body, envelope, properties):
    """
    Handles incoming event from RabbitMQ.
    """
    # Before do anything check that ingest and database are up
    ingest_is_up = bind_to_service(app.config['INGEST_HOST'], int(app.config['INGEST_PORT']))
    postgresql_is_up = bind_to_service(app.config['POSTGRESQL_HOST'], int(app.config['POSTGRESQL_PORT']))

    if not ingest_is_up or not postgresql_is_up:
        app.logger.warning('Cannot push back signal. Retrying in %s seconds...' % (app.config['PUSH_BACK_TIMEOUT']))
        await asyncio.sleep(int(app.config['PUSH_BACK_TIMEOUT']))
        await callback(channel, body, envelope, properties)
    else:
        # if everything is ok check quality of incoming event
        try:
            event_not_corrupted = check_quality(body)
        # if connection with db is lost during execution rollback the broken transaction
        except sqlalchemy.exc.StatementError:
            db.session.rollback()
            app.logger.warning('Rolling back db transaction. Retrying in %s seconds...' % (app.config['PUSH_BACK_TIMEOUT']))
            await asyncio.sleep(int(app.config['PUSH_BACK_TIMEOUT']))
            await callback(channel, body, envelope, properties)

        if event_not_corrupted:
            await push_back_event(body, channel, envelope)
        else:
            await channel.basic_client_ack(envelope.delivery_tag)
            app.logger.info('Event corrupted or unaccceptable')


async def consume(**kwargs):
    """
    Connects RabbitMQ and receives events from queue.
    """
    wait_seconds = kwargs.get('wait_seconds', None)
    services_dict = kwargs.get('services_dict', None)
    if wait_seconds:
        await asyncio.sleep(int(wait_seconds))

    try:
        # create connection with rabbitmq container
        transport, protocol = await aioamqp.connect(
            host=str(app.config['RMQ_HOST']),
            port=int(app.config['RMQ_PORT']),
            login=str(app.config['RMQ_USERNAME']),
            password=str(app.config['RMQ_PASSWORD']),
            login_method='PLAIN'
        )
    except aioamqp.AmqpClosedConnection:
        app.logger.info('closed connections')
        await consume(wait_seconds=app.config['RMQ_RETRY'], services_dict=services_dict)
    except ConnectionRefusedError:
        app.logger.info('RabbitMQ is down. Retrying in %s seconds' %
                        (str(app.config['RMQ_RETRY'])))
        await consume(wait_seconds=app.config['RMQ_RETRY'], services_dict=services_dict)

    app.logger.info('Connected on %s:%s' % (
        str(app.config['RMQ_HOST']),
        str(app.config['RMQ_PORT'])))

    try:
        # get channel of created connection
        channel = await protocol.channel()
        app.logger.info('Channel Created.')
    except Exception as e:
        app.logger.info('Error on channel creation:\n' % (str(e)))
        await consume(wait_seconds=app.config['RMQ_RETRY'], services_dict=services_dict)

    try:
        # We have to ensure that the queue is created in Ingest, If not we create it now
        await channel.queue_declare(
            queue_name=app.config['RMQ_QUEUE'],
            durable=True,
        )
    except Exception as e:
        app.logger.info('Error on queue creation:\n' % (str(e)))
        await consume(wait_seconds=app.config['RMQ_RETRY'], services_dict=services_dict)

    # Infinite consume after run forever loop
    await channel.basic_consume(callback, queue_name=app.config['RMQ_QUEUE'], no_ack=False)


async def push_back_event(body, channel, envelope):
    """
    Tries to open a socket and send back to ingest the incoming event
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((app.config['INGEST_HOST'], int(app.config['INGEST_PORT'])))
            s.sendall(body)
            data = s.recv(1024)
            s.close()
            # If ingest received your socket it will respond you 1.
            if data.decode('utf-8') == '1':
                # if everything is ok remove event from rabbitmq
                # Removal on rabbitmq has to do with acknowledgement
                await channel.basic_client_ack(envelope.delivery_tag)
                app.logger.info('Event Pushed back to Ingest')
            else:
                app.logger.warning('Connection with ingest broken. Event pushed back to queue')
        except ConnectionRefusedError:
            app.logger.info('Ingest Service Down. Event pushed back to queue')
