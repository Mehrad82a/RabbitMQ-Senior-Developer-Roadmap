import json
import pika
from abc import ABC, abstractmethod
from collections.abc import Mapping


from app.core.logger import get_logger
from app.core.rabbitmq import RabbitMQConnection, RabbitMQConnectionError
from app.services.exceptions import PermanentProcessingError, TransientProcessingError
from app.services.task_handler import TaskHandler


logger = get_logger(__name__)


class BaseConsumer(ABC):

    AUTO_ACK: bool
    DEFAULT_PREFETCH_COUNT = 1

    def __init__(
            self,
            *,
            queue_name: str,
            handler: TaskHandler | None = None,
            rabbitmq: RabbitMQConnection | None = None,
            prefetch_count: int | None = None,
    ) -> None:

        if not queue_name or not queue_name.strip():
            raise ValueError('Queue name cannot be empty')

        if prefetch_count is not None and prefetch_count < 0:
            raise ValueError('Prefetch count cannot be negative')


        self._queue_name = queue_name.strip()
        self._handler = handler or TaskHandler(handler_name=self.consumer_name)
        self._rabbitmq = rabbitmq or RabbitMQConnection()
        self._prefetch_count = self.DEFAULT_PREFETCH_COUNT if prefetch_count is None else prefetch_count
        self._channel: pika.adapters.blocking_connection.BlockingChannel | None = None


    @property
    def consumer_name(self) -> str:
        return self.__class__.__name__


    @property
    def queue_name(self) -> str:
        return self._queue_name


    def start(self) -> None:
        try:
            self._channel = self._rabbitmq.connect()

            self._declare_queue()
            self._configure_qos()
            self._register_consumer()

            logger.info(
                f'[{self.consumer_name}] Waiting for messages: '
                f'queue=<{self._queue_name}> | auto_ack=<{self.AUTO_ACK}>'
            )

            self._channel.start_consuming()


        except KeyboardInterrupt:
            logger.info(f'[{self.consumer_name}] Interrupted by user.')
            self.stop()


        except (pika.exceptions.AMQPError, RabbitMQConnectionError) as exc:
            logger.exception(f'[{self.consumer_name}] Failed to start consumer: {exc}')
            raise



    def stop(self) -> None:
        logger.info(f'[{self.consumer_name}] Stopping consumer.')

        if self._channel is not None and self._channel.is_open:
            try:
                self._channel.stop_consuming()

            except pika.exceptions.AMQPError:
                logger.warning(f'[{self.consumer_name}] Channel already closed while stopping.')


        self._rabbitmq.close()
        logger.info(f'[{self.consumer_name}] Consumer stopped.')



    # =========================================
    # Topology
    # =========================================
    def _declare_queue(self) -> None:
        channel = self._require_channel()
        channel.queue_declare(
            queue=self._queue_name,
            durable=True,
        )
        logger.info(f'[{self.consumer_name}] Queue declared: queue=<{self._queue_name}>')


    def _configure_qos(self) -> None:
        channel = self._require_channel()
        channel.basic_qos(prefetch_count=self._prefetch_count)

        logger.info(
            f'[{self.consumer_name}] QoS configured: '
            f'prefetch_count=<{self._prefetch_count}> | '
            f'effective=<{not self.AUTO_ACK}>'
        )


    def _register_consumer(self) -> None:
        channel = self._require_channel()

        channel.basic_consume(
            queue=self._queue_name,
            on_message_callback=self._callback,
            auto_ack=self.AUTO_ACK,
        )
        logger.info(
            f'[{self.consumer_name}] Consumer registered: '
            f'queue=<{self._queue_name}> | auto_ack=<{self.AUTO_ACK}>'
        )


    def _require_channel(self) -> pika.adapters.blocking_connection.BlockingChannel:
        if self._channel is None:
            raise RuntimeError('Consumer channel is not available.')

        return self._channel



    # =========================================
    # Delivery pipeline
    # =========================================
    def _callback(
            self,
            channel: pika.adapters.blocking_connection.BlockingChannel,
            method: pika.spec.Basic.Deliver,
            properties: pika.spec.BasicProperties,
            body: bytes,
    ) -> None:
        delivery_tag = method.delivery_tag
        redelivered = bool(method.redelivered)

        logger.info(
            f'[{self.consumer_name}] Delivery received: '
            f'delivery_tag=<{delivery_tag}> | redelivered=<{redelivered}> | '
            f'queue=<{self._queue_name}>'
        )


        try:
            task = self._deserialize(body)

        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            logger.exception(
                f'[{self.consumer_name}] Malformed payload: '
                f'delivery_tag=<{delivery_tag}> | error={exc}'
            )
            self._on_permanent_failure(channel, method, task_id='unknown')
            return

        task_id = self._get_task_id(task)


        try:
            result = self._handler.process(task)

            logger.info(
                f'[{self.consumer_name}] Task processed: '
                f'task_id=<{task_id}> | result={result}'
            )

            self._on_success(channel, method, task_id=task_id)



        except TransientProcessingError as exc:
            logger.warning(
                f'[{self.consumer_name}] Transient failure: '
                f'task_id=<{task_id}> | redelivered=<{redelivered}> | error={exc}'
            )

            self._on_transient_failure(channel, method, task_id=task_id)


        except PermanentProcessingError as exc:
            logger.error(
                f'[{self.consumer_name}] Permanent failure: '
                f'task_id=<{task_id}> | error={exc}'
            )
            self._on_permanent_failure(channel, method, task_id=task_id)


        except Exception as exc:
            logger.exception(
                f'[{self.consumer_name}] Unexpected failure: '
                f'task_id=<{task_id}> | error={exc}'
            )
            self._on_permanent_failure(channel, method, task_id=task_id)


    # =========================================
    # Acknowledgement hooks (ack mode specific)
    # =========================================
    @abstractmethod
    def _on_success(
            self,
            channel: pika.adapters.blocking_connection.BlockingChannel,
            method: pika.spec.Basic.Deliver,
            *,
            task_id: str
    ) -> None:
        """Called after the handler finished without raising."""


    @abstractmethod
    def _on_transient_failure(
            self,
            channel: pika.adapters.blocking_connection.BlockingChannel,
            method: pika.spec.Basic.Deliver,
            *,
            task_id: str
    ) -> None:
        """Called for a failure that another attempt could recover from."""


    @abstractmethod
    def _on_permanent_failure(
            self,
            channel: pika.adapters.blocking_connection.BlockingChannel,
            method: pika.spec.Basic.Deliver,
            *,
            task_id: str
    ) -> None:
        """Called for a failure that no retry can fix."""


    # =========================================
    # Helpers
    # =========================================
    @staticmethod
    def _deserialize(body: bytes) -> dict[str, object]:
        task = json.loads(body.decode('utf-8'))

        if not isinstance(task, dict):
            raise ValueError('Task body must contain a JSON object.')

        return task



    @staticmethod
    def _get_task_id(task: Mapping[str, object]) -> str:
        task_id = task.get('task_id')

        if isinstance(task_id, str) and task_id.strip():
            return task_id.strip()

        return 'unknown'