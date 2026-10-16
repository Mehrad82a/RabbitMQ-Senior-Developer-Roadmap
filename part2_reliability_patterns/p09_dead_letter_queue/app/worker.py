import signal
import pika
from types import FrameType

from app.consumers.task_consumer import TaskConsumer
from app.core.logger import get_logger
from app.core.rabbitmq import RabbitMQConnectionError


logger = get_logger(__name__)



def main() -> int:
    consumer = TaskConsumer()

    def handle_shutdown(
            signal_number: int,
            _frame: FrameType | None,
    ) -> None:

        logger.info(
            f'[worker] Shutdown requested: signal=<{signal.Signals(signal_number).name}>'
        )

        consumer.stop()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    logger.info('[worker] Starting task consumer.')


    try:
        consumer.start()

    except KeyboardInterrupt:
        logger.info('[worker] Interrupted.')
        consumer.stop()

    except (RabbitMQConnectionError, pika.exceptions.AMQPError, OSError):
        logger.exception('[worker] RabbitMQ connection or consumption failed.')
        return 1

    except Exception:
        logger.exception('[worker] Unexpected worker failure.')
        return 1

    logger.info('[worker] Stopped cleanly.')
    return 0



if __name__ == '__main__':
    raise SystemExit(main())

