import sys

from app.workers.base_consumer import BaseTopicConsumer
from app.services.handlers.order_handler import OrderHandler



class OrderConsumer(BaseTopicConsumer):

    queue_name = 'order_events'
    binding_key = 'order.#'

    def __init__(self):
        super().__init__(handler=OrderHandler())



if __name__ == '__main__':

    consumer = OrderConsumer()

    try:
        consumer.start()

    except KeyboardInterrupt:
        consumer.rabbitmq.close()
        sys.exit(0)



