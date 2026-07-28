import sys
from app.workers.base_consumer import BaseDirectConsumer
from app.services.handlers.info_handler import InfoHandler



class InfoConsumer(BaseDirectConsumer):

    queue_name = 'info_logs'
    routing_key = 'info'

    def __init__(self):
        super().__init__(handler=InfoHandler())


if __name__ == '__main__':

    consumer = InfoConsumer()

    try:
        consumer.start()

    except KeyboardInterrupt:
        consumer.rabbitmq.close()
        sys.exit(0)



