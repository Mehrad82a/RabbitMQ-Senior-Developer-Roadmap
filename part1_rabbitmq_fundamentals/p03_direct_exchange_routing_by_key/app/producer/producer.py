import json

import pika

from app.core.rabbitmq import RabbitMQConnection
from app.core.logger import logger


rabbitmq = RabbitMQConnection()


def publish(payload: dict) -> bool:
    try:
        level = payload.get('level')
        message = payload.get('message')

        channel = rabbitmq.connect()

        # Declare a direct exchange
        channel.exchange_declare(
            exchange='direct_logs',
            exchange_type='direct',
            durable=True,
        )

        data = json.dumps(payload)

        channel.basic_publish(
            exchange='direct_logs',
            routing_key=level,
            body=data,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        logger.info(f"[Producer] Published data successfully | Data: '{level}'- {message}")
        return True

    except Exception as e:
        logger.error(f'[Producer] Publish data failed: {e}')
        return False



