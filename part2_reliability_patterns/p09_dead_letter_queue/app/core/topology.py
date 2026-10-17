from pika.adapters.blocking_connection import BlockingChannel

from app.core.config import Settings, settings
from app.core.logger import get_logger


logger = get_logger(__name__)



class RabbitMQTopology:
    """
    Declare the main task topology and the dead-letter destination.

    The main queue's dead-letter configuration is managed by the broker
    policy imported from rabbitmq/definitions.json.
    """

    def __init__(self, *, config: Settings | None = None) -> None:
        self._settings = config if config is not None else settings

        if self._settings.task_queue == self._settings.dead_letter_queue:
            raise ValueError(
                'The task queue and dead-letter queue must be different.'
            )


    def declare(self, channel: BlockingChannel) -> None:
        """
        Declare exchanges, queues, and bindings using an open channel.

        The dead-letter destination is declared before the main task queue.
        """

        if not channel.is_open:
            raise RuntimeError(
                'An open RabbitMQ channel is required to declare topology.'
            )

        self._declare_dead_letter_topology(channel)
        self._declare_task_topology(channel)

        logger.info('[RabbitMQTopology] Topology is ready.')



    def _declare_dead_letter_topology(self, channel: BlockingChannel) -> None:
        channel.exchange_declare(
            exchange=self._settings.dead_letter_exchange,
            exchange_type='direct',
            durable=True,
        )

        channel.queue_declare(
            queue=self._settings.dead_letter_queue,
            durable=True,
            exclusive=False,
            auto_delete=False,
        )

        channel.queue_bind(
            queue=self._settings.dead_letter_queue,
            exchange=self._settings.dead_letter_exchange,
            routing_key=self._settings.dead_letter_routing_key,
        )

        logger.info(
            '[RabbitMQTopology] Dead-letter destination declared: '
            f'exchange=<{self._settings.dead_letter_exchange}> | '
            f'queue=<{self._settings.dead_letter_queue}> | '
            f'routing_key=<{self._settings.dead_letter_routing_key}>'
        )



    def _declare_task_topology(self, channel: BlockingChannel) -> None:
        channel.exchange_declare(
            exchange=self._settings.task_exchange,
            exchange_type='direct',
            durable=True,
        )


        # DLX arguments are supplied by the broker policy, not here.
        channel.queue_declare(
            queue=self._settings.task_queue,
            durable=True,
            exclusive=False,
            auto_delete=False,
        )

        channel.queue_bind(
            queue=self._settings.task_queue,
            exchange=self._settings.task_exchange,
            routing_key=self._settings.task_routing_key,
        )

        logger.info(
            '[RabbitMQTopology] Task destination declared: '
            f'exchange=<{self._settings.task_exchange}> | '
            f'queue=<{self._settings.task_queue}> | '
            f'routing_key=<{self._settings.task_routing_key}>'
        )