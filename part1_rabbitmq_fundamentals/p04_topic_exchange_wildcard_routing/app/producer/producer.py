import json, pika

from app.core.rabbitmq import RabbitMQConnection
from app.core.logger import logger


rabbitmq = RabbitMQConnection()

exchange_name = 'topic_events'
exchange_type = 'topic'


def publish(event: dict) -> bool:
    try:
        routing_key = event.get('routing_key')

        channel = rabbitmq.connect()

        # Declare a direct exchange
        channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=True,
        )

        data = json.dumps(event)

        channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=data,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        logger.info(f"[Producer] Published event successfully | Event: '{event}'")
        return True

    except Exception as e:
        logger.error(f'[Producer] Publish data failed: {e}')
        return False



