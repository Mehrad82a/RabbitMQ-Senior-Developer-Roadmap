import signal
import sys
from types import FrameType


from app.consumers.auto_ack_consumer import AutoAckConsumer
from app.consumers.base_consumer import BaseConsumer
from app.consumers.manual_ack_consumer import ManualAckConsumer
from app.core.config import settings
from app.core.logger import get_logger
from app.core.rabbitmq import RabbitMQConnectionError



logger = get_logger(__name__)


CONSUMER_MODES: dict[str, type[BaseConsumer]] = {
    'auto': AutoAckConsumer,
    'manual': ManualAckConsumer,
}




def build_consumer(mode: str) -> BaseConsumer:
    normalized_mode = (mode or '').strip().lower()
    consumer_class = CONSUMER_MODES.get(normalized_mode)

    if consumer_class is None:
        supported_modes = ', '.join(sorted(CONSUMER_MODES))
        raise ValueError(f'Unsupported consumer mode: <{mode}>. Supported modes: {supported_modes}.')

    return consumer_class()





def register_signal_handlers(consumer: BaseConsumer) -> None:
    def handler_shutdown(signal_number: int, frame: FrameType | None) -> None:
        logger.info(
            f'[worker] Shutdown signal received: '
            f'signal=<{signal.Signals(signal_number).name}>'
        )
        consumer.stop()

    for signal_shutdown in (signal.SIGINT, signal.SIGTERM):
        signal.signal(signal_shutdown, handler_shutdown)




def main() -> None:
    mode = settings.consumer_mode

    try:
        consumer = build_consumer(mode)

    except ValueError:
        logger.exception('[worker] Invalid consumer configuration.')
        sys.exit(1)

    logger.info(
        f'[worker] Starting: mode=<{mode}> | '
        f'consumer=<{consumer.consumer_name}> | queue=<{consumer.queue_name}>'
    )


    register_signal_handlers(consumer)

    try:
        consumer.start()

    except RabbitMQConnectionError:
        logger.exception('[worker] Could not reach RabbitMQ.')
        sys.exit(1)

    except Exception:
        logger.exception('[worker] Consumer stopped with an unexpected error.')
        consumer.stop()
        sys.exit(1)

    logger.info('[worker] Exited cleanly.')




if __name__ == '__main__':
    main()







