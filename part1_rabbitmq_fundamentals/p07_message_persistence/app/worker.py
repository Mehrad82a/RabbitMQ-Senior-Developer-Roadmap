import os, sys

from app.core.logger import logger
from app.consumers.persistence_consumer import PersistenceConsumer
from app.services.handlers.persistence_handler import PersistenceHandler


def get_handler_name() -> str:
    handler_name = os.getenv('HANDLER_NAME')

    if not handler_name or not handler_name.strip():
        raise RuntimeError('HANDLER_NAME environment variable is required')

    return handler_name.strip()


def main() -> None:
    handler_name = get_handler_name()

    logger.info(f'Starting persistence worker with handler {handler_name}')

    handler = PersistenceHandler(
        handler_name=handler_name,
    )

    consumer = PersistenceConsumer(
        handler=handler,
    )

    consumer.start()




if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        logger.info('Persistence worker interrupted.')
        sys.exit(0)

    except Exception:
        logger.exception('Persistence worker stopped unexpectedly.')
        sys.exit(1)




