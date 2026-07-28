import sys


from app.workers.base_consumer import BaseDirectConsumer
from app.services.handlers.warning_handler import WarningHandler


class WarningConsumer(BaseDirectConsumer):

    queue_name = 'warning_logs'
    routing_key = 'warning'


    def __init__(self):
        super().__init__(handler=WarningHandler())


if __name__ == '__main__':

    consumer = WarningConsumer()

    try:
        consumer.start()

    except KeyboardInterrupt:
        consumer.rabbitmq.close()
        sys.exit(0)

