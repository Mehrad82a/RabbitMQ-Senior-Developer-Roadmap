import json, pika
from rabbitmq_connection import RabbitMQConnection


queue_name = 'tasks'

def send_to_queue(data: dict):
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.connect()

    channel.queue_declare(queue=queue_name, durable=True)

    task = json.dumps(data)

    channel.basic_publish(
        exchange='',
        routing_key='tasks',
        body=task,
        properties=pika.BasicProperties(delivery_mode=2),
    )

    print(f'[x] Sent task: {task}')



