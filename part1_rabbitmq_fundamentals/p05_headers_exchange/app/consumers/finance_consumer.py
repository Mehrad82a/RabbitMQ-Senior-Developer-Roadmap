import sys

from app.consumers.base_consumer import BaseHeadersConsumer
from app.services.handlers.finance_handler import FinanceHandler




class FinanceConsumer(BaseHeadersConsumer):

    queue_name = 'finance_events'
    
    binding_arguments = {
        'x-match': 'all',
        'department': 'finance',
        'priority': 'normal',
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

