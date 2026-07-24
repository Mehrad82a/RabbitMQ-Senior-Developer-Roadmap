import sys, json
from app.core.rabbitmq import RabbitMQConnection
from app.core.logger import logger
from app.services.sms_service import process_sms_event



rabbitmq = RabbitMQConnection()


def callback(ch, method, body):
    """
    Process a single RabbitMQ message.

    Parameters:
        ch: RabbitMQ channel
        method: delivery metadata
        body: event (bytes)
    """
    try:
        event = json.loads(body)

        result = process_sms_event(event)
        logger.info(f'Result: {result}')

        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info('Event acknowledged successfully')



    except Exception as e:
        logger.error(f'Event not acknowledged | Error: {e}')


exchange_name = 'notifications'
queue_name = 'sms_notifications'

def main():
    channel = rabbitmq.connect()

    channel.exchange_declare(
        # exchange='logs',
        exchange=exchange_name,
        exchange_type='fanout',
        durable=True,
    )

    # Each subscriber gets a unique queue (by exclusive=True)
    result = channel.queue_declare(
        # queue='',
        # exclusive=True
        queue=queue_name,
        durable=True
    )

    # queue_name = result.method.queue

    # Bind queue to exchange
    channel.queue_bind(
        # exchange='logs',
        exchange=exchange_name,
        queue=queue_name
    )

    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=lambda ch, method, properties, body: callback(ch, method, body),
    )

    logger.info(f"[SMS Service] Waiting for events on queue: '{queue_name}'...")
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        logger.warning('Interrupted by user')
        rabbitmq.close()
        sys.exit(0)

    except Exception as e:
        logger.error(f'Unexpected error occurred: {e}')
        rabbitmq.close()
        sys.exit(1)
