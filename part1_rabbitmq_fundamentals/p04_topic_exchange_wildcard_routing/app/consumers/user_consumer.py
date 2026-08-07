import sys

from app.consumers.base_consumer import BaseTopicConsumer
from app.services.handlers.user_handler import UserHandler




class UserConsumer(BaseTopicConsumer):

    queue_name = 'user_events'
    binding_key = 'user.#'

    def __init__(self):
        super().__init__(handler=UserHandler())


if __name__ == '__main__':

    consumer = UserConsumer()

    try:
        consumer.start()

    except KeyboardInterrupt:
        consumer.rabbitmq.close()
        sys.exit(0)

