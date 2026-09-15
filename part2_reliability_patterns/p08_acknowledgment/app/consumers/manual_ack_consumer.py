"""
Consumes with auto_ack=False, so this process decides when a message dies.

Acknowledgement matrix:

    success                        -> basic_ack
    transient, first delivery      -> basic_nack(requeue=True)
    transient, already redelivered -> basic_reject(requeue=False)
    permanent                      -> basic_reject(requeue=False)

Until one of those is sent, the message stays unacked and the broker holds
it. If this process disappears first, the broker requeues the delivery and
another consumer receives it with redelivered=True.

The redelivered check is the whole reason this class is more than an ack
call: nacking a message that always fails puts it straight back at the head
of the queue, and the consumer spins on it forever. Allowing exactly one
retry keeps genuinely transient failures recoverable while a permanently
broken task leaves the queue on its second attempt.

Note that manual ack is not exactly-once delivery. A crash after the work
is done but before the ack arrives causes a redelivery of work that already
happened, so handlers still have to tolerate being run twice.
"""



import pika
from app.core.config import settings
from app.core.logger import get_logger
from app.consumers.base_consumer import BaseConsumer
from app.core.rabbitmq import RabbitMQConnection
from app.services.task_handler import TaskHandler


logger = get_logger(__name__)


class ManualAckConsumer(BaseConsumer):

    AUTO_ACK = False

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
    def _on_success(
        self,
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        *,
        task_id: str,
    ) -> None:

        channel.basic_ack(delivery_tag=method.delivery_tag)

        logger.info(
            f'[{self.consumer_name}] Acknowledged: task_id=<{task_id}> | '
            f'delivery_tag=<{method.delivery_tag}> | action=<basic_ack>'
        )



    def _on_transient_failure(
        self,
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        *,
        task_id: str,
    ) -> None:

        if method.redelivered:
            channel.basic_reject(
                delivery_tag=method.delivery_tag,
                requeue=False
            )
            logger.error(
                f'[{self.consumer_name}] Rejected (transient) after one retry: '
                f'task_id=<{task_id}> | delivery_tag=<{method.delivery_tag}> | '
                f'action=<basic_reject requeue=False> | '
                f'note=<retry budget exhausted, requeue loop prevented>'
            )
            return


        channel.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=True
        )
        logger.warning(
            f'[{self.consumer_name}] Requeued (transient) for one retry: '
            f'task_id=<{task_id}> | delivery_tag=<{method.delivery_tag}> | '
            f'action=<basic_nack requeue=True>'
        )




    def _on_permanent_failure(
        self,
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        *,
        task_id: str,
    ) -> None:

        channel.basic_reject(
            delivery_tag=method.delivery_tag,
            requeue=False
        )
        logger.error(
            f'[{self.consumer_name}] Rejected permanently: task_id=<{task_id}> | '
            f'delivery_tag=<{method.delivery_tag}> | '
            f'action=<basic_reject requeue=False> | note=<dropped, no DLQ yet>'
        )