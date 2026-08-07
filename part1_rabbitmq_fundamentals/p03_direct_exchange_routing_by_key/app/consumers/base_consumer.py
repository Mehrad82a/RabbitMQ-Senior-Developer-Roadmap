import json
from abc import ABC, abstractmethod

from app.core.logger import logger
from app.core.rabbitmq import RabbitMQConnection
from app.services.handlers.base_handler import BaseHandler

class BaseDirectConsumer(ABC):
    """
    Base RabbitMQ consumer

    This class implements the common workflow for all consumers:
        - Connect to RabbitMQ
        - Declare direct exchange
        - Declare queue
        - Bind queue
        - Consume messages
        - ACK / NACK messages

    Child classes only implement business logic.
    """

    exchange_name = 'direct_logs'
    exchange_type = 'direct'

    queue_name = ''
    routing_key = ''

    def __init__(self, handler: BaseHandler):
        self.rabbitmq = RabbitMQConnection()
        self.handler = handler


    def callback(self, ch, method, properties, body):

        try:
            data = json.loads(body)

            logger.info(f'[{self.__class__.__name__}] Received: {data}')

            result = self.handler.process(data)
            logger.info(f'[{self.__class__.__name__}] Result: {result}')

            ch.basic_ack(
                delivery_tag=method.delivery_tag,
            )

            logger.info(
                f'[{self.__class__.__name__}] Message acknowledged successfully'
            )

        except Exception as e:

            logger.exception(f'[{self.__class__.__name__}] Message not acknowledged | Error: {e}]')

            ch.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=True
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
            routing_key=self.routing_key,
        )

        channel.basic_qos(prefetch_count=1)

        channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.callback,
        )

        logger.info(f'[{self.__class__.__name__}] Waiting for messages on queue: {self.queue_name}')

        channel.start_consuming()
