import pika
from abc import ABC, abstractmethod

from app.core.logger import logger
from app.core.rabbitmq import RabbitMQConnection




class BaseConsumer(ABC):

    def __init__(self, queue_name: str, rabbitmq: RabbitMQConnection | None = None) -> None:

        if not queue_name.strip():
            raise ValueError('Queue name cannot be empty')

        self._queue_name = queue_name
        self._rabbitmq = rabbitmq or RabbitMQConnection()


    def start(self) -> None:
        try:
            channel = self._rabbitmq.connect()

            self._declare_queue(channel)
            self._configure_qos(channel)

            channel.basic_consume(
                queue=self._queue_name,
                on_message_callback=self._callback,
                auto_ack=False,
            )

            logger.info(f'Consumer started and waiting for messages on queue: {self._queue_name}')

            channel.start_consuming()


        except KeyboardInterrupt:
            logger.info(f'Consumer interrupted: queue: {self._queue_name}')
            self.stop()


        except (pika.exceptions.AMQPError, RuntimeError):
            logger.exception(f'Failed to start consumer on queue: {self._queue_name}')
            raise



    def stop(self) -> None:
        logger.info(f'Stopping consumer on queue: {self._queue_name}')
        self._rabbitmq.close()



    def _declare_queue(self, channel: pika.adapters.blocking_connection.BlockingChannel) -> None:
        channel.queue_declare(
            queue=self._queue_name,
            durable=True,
        )


    @staticmethod
    def _configure_qos(channel: pika.adapters.blocking_connection.BlockingChannel) -> None:
        channel.basic_qos(prefetch_count=1)



    @abstractmethod
    def _callback(
            self,
            channel: pika.adapters.blocking_connection.BlockingChannel,
            method: pika.spec.Basic.Deliver,
            properties: pika.spec.BasicProperties,
            body: bytes
    ) -> None:
        pass