import pika, json
from typing import Dict, Any
from rabbitmq_connection import RabbitMQConnection


def broadcast_event(routing_key: str, message: Dict[str, Any]):
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.connect()


    # Declare a direct exchange
    channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

    message_json = json.dumps(message)

    channel.basic_publish(exchange='topic_events', routing_key=routing_key, body=message_json)
    print(f"[x] '{routing_key}': {message_json}")


