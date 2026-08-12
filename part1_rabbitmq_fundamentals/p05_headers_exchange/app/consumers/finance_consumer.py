import sys

from app.consumers.base_consumer import BaseHeadersConsumer
from app.services.handlers.finance_handler import FinanceHandler

from app.core.logger import handler


class FinanceConsumer(BaseHeadersConsumer):

    queue_name = 'finance_events'
    
    biding_arguments = {
        'x-match': 'all',
        'department': 'finance',
    }

    def __init__(self):
        super().__init__(handler=FinanceHandler())



if __name__ == '__main__':

    consumer = FinanceConsumer()

    try:
        consumer.start()

    except KeyboardInterrupt:
        consumer.rabbitmq.close()
        sys.exit(0)

