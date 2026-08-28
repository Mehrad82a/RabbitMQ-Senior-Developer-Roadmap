import os, sys

from app.consumers.work_consumer import WorkConsumer
from app.core.config import settings
from app.core.logger import logger
from app.services.handlers.task_handler import TaskHandler



def get_handler_name() -> str:
    handler_name = os.getenv('HANDLER_NAME')

    if not handler_name or not handler_name.strip():
        raise RuntimeError('HANDLER_NAME environment variable is required')

    return handler_name.strip()



def main() -> None:
    handler_name = get_handler_name()

    logger.info(f'Starting worker {handler_name} on queue <{settings.work_queue_name}>')

    handler = TaskHandler(
        handler_name=handler_name,
    )

    consumer = WorkConsumer(
        queue_name=settings.work_queue_name,
        handler=handler,
    )

    consumer.start()


if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        sys.exit(0)