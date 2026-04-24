import pika, json
from rabbitmq_connection import RabbitMQConnection



def publish_event(data: dict):
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.connect()

    channel.exchange_declare(exchange='logs', exchange_type='fanout')

    event = json.dumps(data)

    channel.basic_publish(
        exchange='logs',
        routing_key='',
        body=event
    )

    print(f'[x] Sent event: {event}')