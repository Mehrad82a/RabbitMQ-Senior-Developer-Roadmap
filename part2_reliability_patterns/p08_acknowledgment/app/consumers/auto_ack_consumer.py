"""
Consumes with auto_ack=True, where the broker acknowledges on delivery.

RabbitMQ considers the message handled the moment it is written to the
socket, before this process has even parsed it. The message is therefore
already gone by the time any of the hooks below run, which is why none of
them can talk to the broker:

    success            -> nothing to confirm, the broker never waited
    transient failure  -> no redelivery is possible, the work is lost
    permanent failure  -> indistinguishable from success to the broker

This class exists to make that loss observable: the same payloads that the
manual consumer recovers from disappear here, and the logs show it.
"""


import pika
from app.core.config import settings
from app.core.logger import get_logger
from app.consumers.base_consumer import BaseConsumer
from app.core.rabbitmq import RabbitMQConnection
from app.services.task_handler import TaskHandler


logger = get_logger(__name__)


class AutoAckConsumer(BaseConsumer):

    AUTO_ACK = True

    def __init__(
            self,
            *,
            queue_name: str,
            handler: TaskHandler | None = None,
            rabbitmq: RabbitMQConnection | None = None,
            prefetch_count: int | None = None,
    ) -> None:

        super().__init__(
            queue_name=queue_name or settings.auto_ack_queue,
            handler=handler,
            rabbitmq=rabbitmq,
            prefetch_count=prefetch_count
        )



    # =========================================
    # Acknowledgement hooks
    # =========================================
    """
    Every hook is deliberately a no-op. Calling basic_ack / basic_nack here
    would raise a channel error, because the delivery_tag was already settled
    by the broker when it sent the message.
    """
    def _on_success(
        self,
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        *,
        task_id: str,
    ) -> None:
        logger.info(
            f'[{self.consumer_name}] Task finished: task_id={task_id} | '
            f'delivery_tag=<{method.delivery_tag}> | '
            f'note=<already acknowledged on delivery>'
        )



    """
    The retryable case is where auto ack hurts most: the failure is
    recoverable, but the message no longer exists to be retried.
    """
    def _on_transient_failure(
        self,
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        *,
        task_id: str,
    ) -> None:
        logger.error(
            f'[{self.consumer_name}] Task lost after a retryable failure: '
            f'task_id=<{task_id}> | delivery_tag=<{method.delivery_tag}> | '
            f'note=<no redelivery possible with auto_ack>'
        )



    """
    Dropping the message happens to be the right outcome here, but it is
    luck rather than a decision: the broker discarded it either way.
    """
    def _on_permanent_failure(
        self,
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        *,
        task_id: str,
    ) -> None:
        logger.error(
            f'[{self.consumer_name}] Task dropped after a permanent failure: '
            f'task_id=<{task_id}> | delivery_tag=<{method.delivery_tag}> | '
            f'note=<discarded by the broker, not by this consumer>'
        )
