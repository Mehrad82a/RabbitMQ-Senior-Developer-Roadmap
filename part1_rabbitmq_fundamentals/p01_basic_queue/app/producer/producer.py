import json, pika
from app.core.rabbitmq import RabbitMQConnection
from app.core.logger import logger

rabbitmq = RabbitMQConnection()


queue_name = 'tasks'

def publish(task: dict):
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

    logger.info(f'[x] Task published successfully: {task}')



