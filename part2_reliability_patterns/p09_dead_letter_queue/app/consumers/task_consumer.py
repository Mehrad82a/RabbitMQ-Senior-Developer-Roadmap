import json
import pika
from collections.abc import Mapping

from pika.adapters.blocking_connection import BlockingChannel

from app.core.config import Settings, settings
from app.core.logger import get_logger
from app.core.rabbitmq import RabbitMQConnection
from app.core.topology import RabbitMQTopology
from app.services.exceptions import (
    PermanentProcessingError,
    TransientProcessingError,
)
from app.services.task_handler import TaskHandler


logger = get_logger(__name__)




class TaskConsumer:
    """
    Consume tasks with manual acknowledgments.
    """

    def __init__(
            self,
            *,
            handler: TaskHandler | None = None,
            rabbitmq: RabbitMQConnection | None = None,
            topology: RabbitMQTopology | None = None,
            config: Settings | None = None,
    ) -> None:

        self._settings = config if config is not None else settings
        self._handler = handler if handler is not None else TaskHandler()
        self._rabbitmq = rabbitmq if rabbitmq is not None else RabbitMQConnection(config=self._settings)
        self._topology = topology if topology is not None else RabbitMQTopology(config=self._settings)
        self._channel: BlockingChannel | None = None



    def start(self) -> None:
        """Declare topology and consume until stopped."""

        try:
            channel = self._rabbitmq.connect()
            self._channel = channel

            self._topology.declare(channel)

            channel.basic_qos(
                prefetch_count=self._settings.prefetch_count,
            )

            channel.basic_consume(
                queue=self._settings.task_queue,
                on_message_callback=self._callback,
                auto_ack=False,
            )

            logger.info(f'[TaskConsumer] Waiting for tasks: queue=<{self._settings.task_queue}>')

            channel.start_consuming()

        finally:
            self._channel = None
            self._rabbitmq.close()




    def stop(self) -> None:
        """Stop consuming; start() will close the connection."""

        channel = self._channel

        if channel is not None and channel.is_open and channel.is_consuming:
            channel.stop_consuming()



    def _callback(
            self,
            channel: BlockingChannel,
            method: pika.spec.Basic.Deliver,
            properties: pika.BasicProperties,
            body: bytes,
    ) -> None:
        delivery_tag = method.delivery_tag

        try:
            task = self._deserialize(body)

        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            logger.exception(
                f'[TaskConsumer] Invalid message: '
                f'delivery_tag=<{delivery_tag}> | message_id=<{properties.message_id}>'
            )

            self._reject(
                channel,
                delivery_tag,
                reason='invalid_message',
            )
            return

        task_id = self._task_id(task)


        try:
            result = self._handler.process(task)

        except TransientProcessingError:
            if method.redelivered:
                logger.exception(f'[TaskConsumer] Transient failure on redelivery: task_id=<{task_id}>')

                self._reject(
                    channel,
                    delivery_tag,
                    reason='transient_failure_on_redelivery',
                )

            else:
                logger.warning(
                    f'[TaskConsumer] Transient failure; requeueing: '
                    f'task_id=<{task_id}>',
                    exc_info=True,
                )
                channel.basic_nack(
                    delivery_tag=delivery_tag,
                    requeue=True,
                )
            return


        except PermanentProcessingError:
            logger.exception(
                f'[TaskConsumer] Permanent failure: task_id=<{task_id}>'
            )
            self._reject(
                channel,
                delivery_tag,
                reason='permanent_failure',
            )
            return


        except Exception:
            logger.exception(
                f'[TaskConsumer] Unexpected processing failure: '
                f'task_id=<{task_id}>'
            )
            self._reject(
                channel,
                delivery_tag,
                reason='unexpected_failure',
            )
            return

        channel.basic_ack(delivery_tag=delivery_tag)
        logger.info(
            f'[TaskConsumer] Task acknowledged: '
            f'task_id=<{task_id}> | result=<{result}>'
        )



    @staticmethod
    def _deserialize(body: bytes) -> dict[str, object]:
        task = json.loads(body.decode('utf-8'))

        if not isinstance(task, dict):
            raise ValueError('Task body must be a JSON object.')

        return task



    @staticmethod
    def _task_id(task: Mapping[str, object]) -> str:
        value = task.get('task_id')

        if isinstance(value, str) and value.strip():
            return value.strip()

        return 'unknown'



    @staticmethod
    def _reject(
            channel: BlockingChannel,
            delivery_tag: int,
            *,
            reason: str
    ) -> None:
        channel.basic_reject(
            delivery_tag=delivery_tag,
            requeue=False,
        )

        logger.error(
            f'[TaskConsumer] Message rejected: '
            f'delivery_tag=<{delivery_tag}> | reason=<{reason}>',
        )



