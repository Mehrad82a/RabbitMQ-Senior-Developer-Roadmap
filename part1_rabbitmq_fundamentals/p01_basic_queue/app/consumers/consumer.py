import sys, json
from app.core.rabbitmq import RabbitMQConnection
from app.core.logger import logger
from app.services.task_service import TaskService


rabbitmq = RabbitMQConnection()


queue_name = 'tasks'


def callback(ch, method, body):
    """
    Process a single RabbitMQ message.

    Parameters:
        ch: RabbitMQ channel
        method: delivery metadata
        body: message body (bytes)
    """
    try:
        task = json.loads(body)

        result = TaskService.process_task(task)
        logger.info(f'Result: {result}')

        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info('Message acknowledged successfully')

    except Exception as e:
        logger.error(f'Message not acknowledged | Error: {e}')


def main():
    channel = rabbitmq.connect()

    channel.queue_declare(
        queue=queue_name,
        durable=True
    )

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=lambda ch, method, properties, body: callback(ch, method, body)
    )

    logger.info('waiting for message...')
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
