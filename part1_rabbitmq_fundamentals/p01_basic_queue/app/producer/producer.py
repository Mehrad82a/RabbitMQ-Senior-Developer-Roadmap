import json, pika
from app.core.rabbitmq import RabbitMQConnection
from app.core.logger import logger

rabbitmq = RabbitMQConnection()


queue_name = 'tasks'

def publish(task: dict):
    try:
        channel = rabbitmq.connect()

        channel.queue_declare(
            queue=queue_name,
            durable=True
        )

        task = json.dumps(task)

        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=task,
            properties=pika.BasicProperties(delivery_mode=2),
        )

        logger.info(f'[Producer] Task published successfully: {task}')
        return True

    except Exception as e:
        logger.error(f'[Producer] Task published failed: {e}')
        return False


