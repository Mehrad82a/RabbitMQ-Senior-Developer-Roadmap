import pika, json
from rabbitmq_connection import RabbitMQConnection



def publish_message(level: str, body: str):
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.connect()

    # Declare a direct exchange
    channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

    message = json.dumps({'level': level, 'body': body})

    channel.basic_publish(exchange='direct_logs', routing_key=level, body=message)
    print(f"[x] '{level}': {body}")



