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
        self._channel: (
                pika.adapters.blocking_connection.BlockingChannel | None
        ) = None

    def start(self) -> None:
        try:
            self._channel = self._rabbitmq.connect()

            self._declare_queues()
            self._register_consumers()

            logger.info(f'[{self.__class__.__name__}] Consumer started and waiting for messages on queue:]')

            self._channel.start_consuming()



        except KeyboardInterrupt:
            logger.info(f'[{self.__class__.__name__}] Consumer interrupted.')
            self.stop()


        except (pika.exceptions.AMQPError, RuntimeError):
            logger.exception(f'[{self.__class__.__name__}] Failed to start consumer.')
            raise



    def stop(self) -> None:
        logger.info(f'[{self.__class__.__name__}] Stopping consumer.')

        self._rabbitmq.close()

        logger.info(f'[{self.__class__.__name__}] Consumer stopped.')


    def _declare_queues(self) -> None:
        if self._channel is None:
            raise RuntimeError('Consumer channel is not available.')

        queues = (
            (settings.non_durable_transient_queue, False),
            (settings.non_durable_persistent_queue, False),
            (settings.durable_transient_queue, True),
            (settings.durable_persistent_queue, True),
        )

        for queue_name, durable in queues:
            self._channel.queue_declare(
                queue=queue_name,
                durable=durable,
            )

            logger.info(
                f'[{self.__class__.__name__}] '
                f'Queue declared: queue=<{queue_name}> | durable=<{durable}>'
            )



    def _register_consumers(self) -> None:
        if self._channel is None:
            raise RuntimeError('Consumer channel is not available.')

        queue_names = (
            (
                settings.non_durable_transient_queue,
                settings.non_durable_persistent_queue,
                settings.durable_transient_queue,
                settings.durable_persistent_queue,
            )
        )
        for queue_name in queue_names:
            self._channel.basic_consume(
                queue=queue_name,
                on_message_callback=self._callback,
                auto_ack=False,
            )

            logger.info(
                f'[{self.__class__.__name__}] '
                f'Consumer registered on queue: <{queue_name}>'
            )


    def _callback(
            self,
            channel: pika.adapters.blocking_connection.BlockingChannel,
            method: pika.spec.Basic.Deliver,
            properties: pika.spec.BasicProperties,
            body: bytes,
    ) -> None:

        try:
            message = self._deserialize_message(body)
            message_id = message.get('message_id')

            logger.info(
                f'[{self.__class__.__name__}] '
                f'Message received: message_id=<{message_id}> '
                f'Queue: <{method.routing_key}>'
            )

        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            logger.exception(
                f'[{self.__class__.__name__}] '
                f'Invalid message received: delivery_tag=<{method.delivery_tag}>'
            )

            channel.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=False,
            )
            return


        try:
            logger.info(
                f'[{self.__class__.__name__}] '
                f'Message processing started for message=<{message_id}>'
            )

            result = self._handler.process(message)
            logger.info(f'[{self.__class__.__name__}] Result: {result}')

            channel.basic_ack(
                delivery_tag=method.delivery_tag
            )

            logger.info(
                f'[{self.__class__.__name__}] '
                f'Message with message_id=<{message_id}> acknowledged successfully'
            )


        except PersistenceHandlingError as exc:
            logger.exception(
                f'[{self.__class__.__name__}] '
                f'Message with message_id=<{message_id}> not acknowledged | Error: {exc}'
            )

            channel.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=False,
            )


        except Exception as exc:
            logger.exception(
                f'[{self.__class__.__name__}] '
                f'Unexpected processing failure for message=<{message_id}> | Error: {exc}'
            )

            channel.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=True,
            )


    @staticmethod
    def _deserialize_message(body: bytes) -> dict[str, object]:
        decoded_message = body.decode('utf-8')
        message = json.loads(decoded_message)

        if not isinstance(message, dict):
            raise ValueError('Message body must contain a Json object')


        return message