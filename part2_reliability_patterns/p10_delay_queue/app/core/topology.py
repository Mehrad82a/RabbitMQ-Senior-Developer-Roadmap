from pika.adapters.blocking_connection import BlockingChannel

from app.core.config import Settings, settings
from app.core.logger import get_logger


logger = get_logger(__name__)


class RabbitMQTopology:
    """
    Declare the dead-letter, main task, and delay topologies.

    Dead-letter routing for both the main task queue and the delay queue
    is managed by the broker policies imported from rabbitmq/definitions.json.
    """

    def __init__(self, *, config: Settings | None = None) -> None:
        self._settings = config if config is not None else settings
        self._validate_topology_names()


    def _validate_topology_names(self) -> None:
        queue_names = (
            self._settings.task_queue,
            self._settings.delay_queue,
            self._settings.dead_letter_queue,
        )

        if len(set(queue_names)) != len(queue_names):
            raise ValueError(
                'The task queue, delay queue, and dead-letter queue must be different.'
            )

        exchange_names = (
            self._settings.task_exchange,
            self._settings.delay_exchange,
            self._settings.dead_letter_exchange,
        )

        if len(set(exchange_names)) != len(exchange_names):
            raise ValueError(
                'The task exchange, delay exchange, and dead-letter exchange must be different.'
            )


    def declare(self, channel: BlockingChannel) -> None:
        """
        Declare exchanges, queues, and bindings using an open channel.

        Destinations are declared before the queues that route into them:
        1. Dead-letter topology (final destination for rejected tasks)
        2. Main task topology (destination for expired delay-queue tasks)
        3. Delay topology (holding queue for scheduled tasks)
        """

        if not channel.is_open:
            raise RuntimeError(
                'An open RabbitMQ channel is required to declare topology.'
            )

        self._declare_dead_letter_topology(channel)
        self._declare_task_topology(channel)
        self._declare_delay_topology(channel)

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


    def _declare_delay_topology(self, channel: BlockingChannel) -> None:
        channel.exchange_declare(
            exchange=self._settings.delay_exchange,
            exchange_type='direct',
            durable=True,
        )

        # Delay DLX and fallback TTL are supplied by the broker policy, not here.
        channel.queue_declare(
            queue=self._settings.delay_queue,
            durable=True,
            exclusive=False,
            auto_delete=False,
        )

        channel.queue_bind(
            queue=self._settings.delay_queue,
            exchange=self._settings.delay_exchange,
            routing_key=self._settings.delay_routing_key,
        )

        logger.info(
            '[RabbitMQTopology] Delay destination declared: '
            f'exchange=<{self._settings.delay_exchange}> | '
            f'queue=<{self._settings.delay_queue}> | '
            f'routing_key=<{self._settings.delay_routing_key}>'
        )