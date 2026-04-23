import pika, json
from part1_rabbitmq_fundamentals.p02_pubsub_pattern_fanout_exchange.api.rabbitmq_connection import RabbitMQConnection



rabbitmq = RabbitMQConnection()
connection = rabbitmq.get_connection()
channel = rabbitmq.get_channel()


def publish_event(data: dict):
    channel.exchange_declare(exchange='logs', exchange_type='fanout')

    event = json.dumps(data)

    channel.basic_publish(
        exchange='logs',
        routing_key='',
        body=event
    )

    print(f'[x] Sent event: {event}')
    connection.close()