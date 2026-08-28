import pika, time

from app.core.config import settings
from app.core.logger import logger


class RabbitMQConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initializes configuration only, not the connection
            cls._instance._initialized = False
        return cls._instance


    def __init__(self):
        if self._initialized:
            return


        self.connection = None
        self.channel = None
        self._initialized = True


    def _create_parameters(self):
        credentials = pika.PlainCredentials(
            settings.rabbitmq_user,
            settings.rabbitmq_pass,
        )

        return pika.ConnectionParameters(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            credentials=credentials,
            heartbeat=settings.heartbeat,
            blocked_connection_timeout=settings.blocked_connection_timeout,
            connection_attempts=settings.connection_attempts,
            retry_delay=settings.retry_delay,
            socket_timeout=settings.socket_timeout,
        )


    def connect(self):
        if (
            self.connection
            and self.connection.is_open
            and self.channel
            and self.channel.is_open
        ):
            return self.channel

        params = self._create_parameters()

        for attempt in range(1, 11):
            try:
                logger.info(f'Connecting to RabbitMQ (attempt {attempt}/10)')

                self.connection = pika.BlockingConnection(params)
                self.channel = self.connection.channel()
                logger.info('Connected to RabbitMQ successfully.')
                return self.channel

            except pika.exceptions.AMQPConnectionError as e:
                logger.warning(f'RabbitMQ connection failed: {e}')
                time.sleep(5)
        raise RuntimeError('Failed to connect to RabbitMQ after 10 attempts')


    def close(self):
        if self.connection and self.connection.is_open:
            logger.info('Closing RabbitMQ connection.')
            self.connection.close()
