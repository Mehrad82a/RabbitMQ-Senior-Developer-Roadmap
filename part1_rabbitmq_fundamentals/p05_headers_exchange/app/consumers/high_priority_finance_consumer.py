import sys

from app.consumers.base_consumer import BaseHeadersConsumer
from app.services.handlers.high_priority_finance_handler import HighPriorityFinanceHandler



class HighPriorityFinanceConsumer(BaseHeadersConsumer):

    queue_name = 'high_priority_finance_events'

    biding_arguments = {
        'x-match': 'all',
        'department': 'finance',
        'priority': 'high',
    }

    def __init__(self):
        super().__init__(handler=HighPriorityFinanceHandler())


if __name__ == '__main__':

    consumer = HighPriorityFinanceConsumer()

    try:
        consumer.start()

    except KeyboardInterrupt:
        consumer.rabbitmq.close()
        sys.exit(0)

