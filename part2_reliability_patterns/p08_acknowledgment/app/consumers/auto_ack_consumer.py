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



logger = get_logger(__name__)


class AutoAckConsumer(BaseConsumer):

    AUTO_ACK = True
    DEFAULT_QUEUE_NAME = settings.auto_ack_queue



    # =========================================
    # Acknowledgement hooks
    # =========================================
    def _on_success(
        self,
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        *,
        task_id: str,
    ) -> None:
        """
        Log successful processing.

        No acknowledgment is sent because RabbitMQ already considered the
        message acknowledged when it delivered it to this consumer.
        """

        logger.info(
            f'[{self.consumer_name}] Task finished: task_id={task_id} | '
            f'delivery_tag=<{method.delivery_tag}> | '
            f'note=<already acknowledged on delivery>'
        )




    def _on_transient_failure(
        self,
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        *,
        task_id: str,
    ) -> None:
        """
        Log that a retryable message was lost.

        Requeueing is impossible because RabbitMQ has already removed the
        message from the queue.
        """

        logger.error(
            f'[{self.consumer_name}] Task lost after a retryable failure: '
            f'task_id=<{task_id}> | delivery_tag=<{method.delivery_tag}> | '
            f'note=<no redelivery possible with auto_ack>'
        )


    def _on_permanent_failure(
        self,
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        *,
        task_id: str,
    ) -> None:
        """
        Log that a permanently failing message was already discarded.

        Dropping the message is appropriate for a permanent failure, but with
        auto-ack this was RabbitMQ's automatic behavior rather than an explicit
        consumer decision.
        """

        logger.error(
            f'[{self.consumer_name}] Task dropped after a permanent failure: '
            f'task_id=<{task_id}> | delivery_tag=<{method.delivery_tag}> | '
            f'note=<discarded by the broker, not by this consumer>'
        )
