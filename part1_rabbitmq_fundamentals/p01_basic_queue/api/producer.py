import json, pika
from part1_rabbitmq_fundamentals.p01_basic_queue.api.rabbitmq_connection import RabbitMQConnection



rabbitmq = RabbitMQConnection()
connection = rabbitmq.get_connection()
channel = rabbitmq.get_channel()

queue_name = 'tasks'

def send_to_queue(data: dict):
    channel.queue_declare(queue=queue_name, durable=True)

    message = json.dumps(data)

    channel.basic_publish(
        exchange='',
        routing_key='tasks',
        body=message,
        properties=pika.BasicProperties(delivery_mode=2),
    )

    print(f' [x] Sent message: {message}')
    connection.close()



