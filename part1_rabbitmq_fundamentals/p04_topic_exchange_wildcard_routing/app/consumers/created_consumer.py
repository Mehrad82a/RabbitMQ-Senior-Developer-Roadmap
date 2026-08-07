import sys


from app.services.handlers.created_handler import CreatedHandler
from app.consumers.base_consumer import BaseTopicConsumer
from app.core.logger import handler


class CreatedConsumer(BaseTopicConsumer):

    queue_name = 'created_events'
    binding_key = '#.created'

    def __init__(self):
        super().__init__(handler=CreatedHandler())



if __name__ == '__main__':

    consumer = CreatedConsumer()

    try:
        consumer.start()

    except KeyboardInterrupt:
        consumer.rabbitmq.close()
        sys.exit(0)



