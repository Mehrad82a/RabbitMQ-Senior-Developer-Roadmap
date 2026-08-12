import sys

from app.consumers.base_consumer import BaseHeadersConsumer
from app.services.handlers.hr_handler import HRHandler


class HRConsumer(BaseHeadersConsumer):
    queue_name = 'hr_events'

    biding_arguments = {
        'x-match': 'all',
        'department': 'hr',
    }

    def __init__(self):
        super().__init__(handler=HRHandler())


if __name__ == '__main__':

    consumer = HRConsumer()

    try:
        consumer.start()

    except KeyboardInterrupt:
        consumer.rabbitmq.close()
        sys.exit(0)

