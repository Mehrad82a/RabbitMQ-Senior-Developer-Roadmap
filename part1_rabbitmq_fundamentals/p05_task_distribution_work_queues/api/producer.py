import json, pika

from rabbitmq_connection import RabbitMQConnection


def publish_task(task: dict):
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.connect()


    # Declare a durable queue
    channel.queue_declare(queue='work_queue', durable=True)

    message = json.dumps(task)

    # Publish persistent message
    channel.basic_publish(
        exchange='',
        routing_key='work_queue',
        body=message,
        properties=pika.BasicProperties(delivery_mode=2),
    )

    print(f'[x] Sent task: {task}')

