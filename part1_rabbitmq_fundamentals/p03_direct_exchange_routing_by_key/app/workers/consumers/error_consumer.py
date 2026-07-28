import sys

from app.services.handlers.error_handler import ErrorHandler
from app.workers.base_consumer import BaseDirectConsumer



class ErrorConsumer(BaseDirectConsumer):

    queue_name = 'error_logs'
    routing_key =  'error'

    def __init__(self):
        super().__init__(handler=ErrorHandler())



if __name__ == '__main__':

    consumer = ErrorConsumer()

    try:
        consumer.start()

    except KeyboardInterrupt:
        consumer.rabbitmq.close()
        sys.exit(0)


