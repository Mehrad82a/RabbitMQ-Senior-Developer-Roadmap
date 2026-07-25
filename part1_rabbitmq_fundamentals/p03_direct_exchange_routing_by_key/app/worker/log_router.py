import sys, json
from app.core.logger import logger
from app.core.rabbitmq import RabbitMQConnection
from app.services.log_service import LogService



rabbitmq = RabbitMQConnection()
queue_name = 'router_logs'
routing_keys = ['info', 'warning', 'error']


def callback(ch, method, body):
    """
    Process a single RabbitMQ message.

    Parameters:
        ch: RabbitMQ channel
        method: delivery metadata
        body: leve & message (bytes)
    """
    try:
        data = json.loads(body)

        result = LogService.process_log(data)
        logger.info(f'Result: {result}')

        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info('Message acknowledged successfully')

    except Exception as e:
        logger.error(f'Message not acknowledged | Error: {e}')



def main():
    channel = rabbitmq.connect()

    channel.exchange_declare(
        exchange='direct_logs',
        exchange_type='direct',
        durable=True,
    )

    # Each worker connects to its direct queue
    channel.queue_declare(
        queue=queue_name,
        durable=True
    )

    # Bind queue to exchange
    for key in routing_keys:
        channel.queue_bind(
            exchange='direct_logs',
            queue=queue_name,
            routing_key=key
        )

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=lambda ch, method, properties, body: callback(ch, method, body)
    )

    logger.info(f"[ROUTER] Listening to all log levels on queue: '{queue_name}'...")
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