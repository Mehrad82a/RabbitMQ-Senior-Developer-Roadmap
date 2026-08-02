import sys

from app.consumers.base_consumer import BaseTopicConsumer
from app.services.handlers.error_handler import ErrorHandler


class ErrorConsumer(BaseTopicConsumer):

    queue_name = 'error_events'
    binding_key = '#.error'

    def __init__(self):
        super().__init__(handler=ErrorHandler())


if __name__ == '__main__':

    consumer = ErrorConsumer()

    try:
        consumer.start()

    except KeyboardInterrupt:
        consumer.rabbitmq.close()
        sys.exit(0)



