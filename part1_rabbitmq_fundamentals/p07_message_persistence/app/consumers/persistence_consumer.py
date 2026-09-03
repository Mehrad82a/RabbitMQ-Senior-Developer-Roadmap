import pika, json

from app.core.config import settings
from app.core.logger import logger
from app.core.rabbitmq import RabbitMQConnection

from app.services.handlers.persistence_handler import PersistenceHandlingError, PersistenceHandler





class PersistenceConsumer:
    def __init__(
            self,
            handler: PersistenceHandler,
            rabbitmq: RabbitMQConnection | None = None
    ) -> None:
        self._handler = handler
        self._rabbitmq = rabbitmq or RabbitMQConnection()
        self._channel = (
                pika.adapters.blocking_connection.BlockingChannel | None
        ) = None

    def start(self) -> None:
        try:
            self._channel = self._rabbitmq.connect()

            sel


        except KeyboardInterrupt:
            pass

        except (pika.exceptions.AMQPError, RuntimeError):
            pass


    def _declare_queues(self) -> None:
        pass


    def _register_consumers(self) -> None:
        pass


    def _callback(
            self,
            channel: pika.adapters.blocking_connection.BlockingChannel,
            method: pika.spec.Basic.Deliver,
            properties: pika.spec.BasicProperties,
            body: bytes,
    ) -> None:
        




