import json, pika

from app.core.logger import logger
from app.core.rabbitmq import RabbitMQConnection



rabbitmq = RabbitMQConnection()

exchange_name = 'events'
exchange_type = 'headers'


def publish(event: dict) -> bool:
    try:
        channel = rabbitmq.connect()

        channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=True
        )

        data = json.dumps(event)
        headers = event.get('headers')

        channel.basic_publish(
            exchange=exchange_name,
            routing_key='',
            body=data,
            properties=pika.BasicProperties(
                delivery_mode=2,
                headers=headers
            )
        )

        logger.info(f"[Producer] Published event successfully | Headers: {headers} | Event: '{event}'")
        print('stage 3')
        return True

    except Exception as e:
        logger.error(f'[Producer] Publish data failed: {e}')
        return False