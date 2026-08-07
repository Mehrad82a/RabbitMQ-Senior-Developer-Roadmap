import json, pika
from app.core.rabbitmq import RabbitMQConnection
from app.core.logger import logger


rabbitmq = RabbitMQConnection()

exchange_name = 'notifications'
exchange_type = 'fanout'

def publish_event(event: dict) -> bool:
    try:
        channel = rabbitmq.connect()

        channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=True
        )

        event = json.dumps(event)

        channel.basic_publish(
            exchange=exchange_name,
            routing_key='',
            body=event,
            properties=pika.BasicProperties(delivery_mode=2)
        )

        logger.info(f'[Producer] Published event successfully: {event}')
        return True


    except Exception as e:
        logger.error(f'[Producer] Publish event failed: {e}')
        return False