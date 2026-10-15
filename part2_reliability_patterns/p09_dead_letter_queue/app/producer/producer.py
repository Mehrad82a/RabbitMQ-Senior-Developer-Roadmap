import json
import time
import pika
from collections.abc import Mapping

from app.core.config import Settings, settings
from app.core.logger import get_logger
from app.core.rabbitmq import RabbitMQConnection, RabbitMQConnectionError
from app.core.topology import RabbitMQTopology

from app.producer.producer import exchange_type

logger = get_logger(__name__)


class ProducerPublishError(Exception):
    """
    Raised when a task cannot be published to RabbitMQ.
    """




class Producer:
    """
    Publish persistent task messages to the main task exchange.
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


    def publish(self, *, task: Mapping[str, object]) -> None:
        """
        Publish a task and wait for the broker's confirmation.

        This Producer owns its RabbitMQConnection and closes it after each
        publish attempt. A new Producer should be created per API request.
        """

        task_id = self._get_task_id(task)
        body = self._serialize_task(task)

        try:
            channel = self._rabbitmq.connect()

            self._topology.declare(channel)

            channel.confirm_delivery()

            channel.basic_publish(
                exchange_type=self._settings.task_exchange,
                routing_key=self._settings.task_routing_key,
                body=body,
                properties=pika.BasicProperties(
                    content_type='application/json',
                    content_encoding='utf-8',
                    delivery_mode=2,
                    type=self.MESSAGE_TYPE,
                    message_id=task_id,
                    timestamp=int(time.time()),
                ),
                mandatory=True,
            )


        except (RabbitMQConnectionError, pika.exceptions.AMQPError, OSError) as exc:
            logger.exception(
                '[Producer] Task publish failed: '
                f'task_id=<{task_id}> | '
                f'exchange=<{self._settings.task_exchange}> | '
                f'routing_key=<{self._settings.task_routing_key}>'
            )

            raise ProducerPublishError(
                'The task could not be published to RabbitMQ.'
            ) from exc


        finally:
            self._rabbitmq.close()


        logger.info(
            '[Producer] Task published: '
            f'task_id=<{task_id}> | '
            f'exchange=<{self._settings.task_exchange}> | '
            f'routing_key=<{self._settings.task_routing_key}>'
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
