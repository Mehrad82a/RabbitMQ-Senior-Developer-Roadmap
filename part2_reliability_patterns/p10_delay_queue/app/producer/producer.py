import json
import time
import pika
from collections.abc import Mapping

from app.core.config import Settings, settings
from app.core.logger import get_logger
from app.core.rabbitmq import RabbitMQConnection, RabbitMQConnectionError
from app.core.topology import RabbitMQTopology


logger = get_logger(__name__)


class ProducerPublishError(Exception):
    """
    Raised when a task cannot be published to RabbitMQ.
    """


class Producer:
    """
    Publish persistent task messages to the main task exchange or delay exchange.
    """

    MESSAGE_TYPE = 'task'

    def __init__(
            self,
            *,
            rabbitmq: RabbitMQConnection | None = None,
            topology: RabbitMQTopology | None = None,
            config: Settings | None = None,
    ) -> None:

        self._settings = config if config is not None else settings
        self._rabbitmq = rabbitmq if rabbitmq is not None else RabbitMQConnection(config=self._settings)
        self._topology = topology if topology is not None else RabbitMQTopology(config=self._settings)



    def publish(
            self,
            *,
            task: Mapping[str, object],
            delay_seconds: int = 0,
    ) -> None:
        """
        Publish a task and wait for the broker's confirmation.

        When delay_seconds is 0, the task is routed directly to the main task
        exchange. When delay_seconds is greater than 0, the task is routed to
        the delay exchange with a per-message millisecond expiration.

        This Producer owns its RabbitMQConnection and closes it after each
        publish attempt. A new Producer should be created per API request.
        """

        task_id = self._get_task_id(task)
        validated_delay = self._validate_delay_seconds(delay_seconds)
        body = self._serialize_task(task)
        exchange, routing_key, expiration = self._resolve_destination(
            validated_delay
        )

        try:
            channel = self._rabbitmq.connect()

            self._topology.declare(channel)

            channel.confirm_delivery()

            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=body,
                properties=pika.BasicProperties(
                    content_type='application/json',
                    content_encoding='utf-8',
                    delivery_mode=2,
                    type=self.MESSAGE_TYPE,
                    message_id=task_id,
                    timestamp=int(time.time()),
                    expiration=expiration,
                ),
                mandatory=True,
            )

        except (
            RabbitMQConnectionError,
            pika.exceptions.AMQPError,
            OSError,
        ) as exc:
            logger.exception(
                '[Producer] Task publish failed: '
                f'task_id=<{task_id}> | '
                f'exchange=<{exchange}> | '
                f'routing_key=<{routing_key}> | '
                f'delay_seconds=<{validated_delay}>'
            )

            raise ProducerPublishError(
                'The task could not be published to RabbitMQ.'
            ) from exc

        finally:
            self._rabbitmq.close()

        logger.info(
            '[Producer] Task published: '
            f'task_id=<{task_id}> | '
            f'exchange=<{exchange}> | '
            f'routing_key=<{routing_key}> | '
            f'delay_seconds=<{validated_delay}> | '
            f'expiration_ms=<{expiration}>'
        )


    def _validate_delay_seconds(self, delay_seconds: int) -> int:
        if isinstance(delay_seconds, bool) or not isinstance(delay_seconds, int):
            raise ValueError('Delay seconds must be an integer.')

        if delay_seconds < 0:
            raise ValueError('Delay seconds cannot be negative.')

        max_delay = self._settings.max_delay_seconds
        if delay_seconds > max_delay:
            raise ValueError(
                f'Delay seconds cannot exceed {max_delay} seconds.'
            )

        return delay_seconds


    def _resolve_destination(
            self,
            delay_seconds: int,
    ) -> tuple[str, str, str | None]:
        if delay_seconds == 0:
            return (
                self._settings.task_exchange,
                self._settings.task_routing_key,
                None,
            )

        expiration_ms = str(delay_seconds * 1000)

        return (
            self._settings.delay_exchange,
            self._settings.delay_routing_key,
            expiration_ms,
        )



    @staticmethod
    def _get_task_id(task: Mapping[str, object]) -> str:
        value = task.get('task_id')

        if not isinstance(value, str) or not value.strip():
            raise ValueError('Task must contain a non-empty string task_id.')

        return value.strip()



    @staticmethod
    def _serialize_task(task: Mapping[str, object]) -> bytes:
        try:
            return json.dumps(
                dict(task),
                ensure_ascii=False,
                allow_nan=False,
                separators=(',', ':'),
            ).encode('utf-8')

        except (TypeError, ValueError) as exc:
            raise ProducerPublishError(
                'Task contains values that cannot be serialized to JSON.'
            ) from exc



