import json
from abc import ABC
from typing import Any


from app.core.logger import logger
from app.core.rabbitmq import RabbitMQConnection
from app.services.handlers.base_handler import BaseHandler



class BaseHeadersConsumer(ABC):

    exchange_name = 'events'
    exchange_type = 'headers'

    queue_name = ''
    binding_arguments: dict[str, Any] = {}

    def __init__(self, handler: BaseHandler):
        self.rabbitmq = RabbitMQConnection()
        self.handler = handler

    def callback(self, ch, method, properties, body):

        try:
            data = json.loads(body)

            logger.info(f'[{self.__class__.__name__}] Received {data}')

            result = self.handler.process(data)
            logger.info(f'[{self.__class__.__name__}] Result: {result}')

            ch.basic_ack(
                delivery_tag=method.delivery_tag,
            )

            logger.info(f'[{self.__class__.__name__}] Event acknowledged successfully')


        except Exception as e:
            logger.exception(f'[{self.__class__.__name__}] Event not acknowledged | Error: {e}]')

            ch.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=True,
            )


    def start(self):
        channel = self.rabbitmq.connect()

        channel.exchange_declare(
            exchange=self.exchange_name,
            exchange_type=self.exchange_type,
            durable=True,
        )

        channel.queue_declare(
            queue=self.queue_name,
            durable=True,
        )

        channel.queue_bind(
            exchange=self.exchange_name,
            queue=self.queue_name,
            arguments=self.binding_arguments,
        )

        channel.basic_qos(prefetch_count=1)

        channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.callback,
        )

        logger.info(f'[{self.__class__.__name__}] Waiting for events on queue: {self.queue_name}')

        channel.start_consuming()



