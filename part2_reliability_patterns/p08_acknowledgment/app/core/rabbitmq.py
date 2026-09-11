import pika
import time

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)



class RabbitMQConnectionError(Exception):
    """
    Raised when a usable RabbitMQ connection cannot be established.
    """


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
            connection_attempts=1,
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

        max_attempts = settings.connection_attempts

        last_error: Exception | None = None

        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f'Connecting to RabbitMQ (attempt {attempt}/{max_attempts})')

                self.connection = pika.BlockingConnection(params)
                self.channel = self.connection.channel()
                logger.info('Connected to RabbitMQ successfully.')
                return self.channel

            except pika.exceptions.AMQPConnectionError as exc:
                last_error = exc
                logger.warning(f'RabbitMQ connection failed (attempt {attempt}/{max_attempts}): {exc}')

                if attempt < max_attempts:
                    time.sleep(settings.retry_delay)

        raise RabbitMQConnectionError(
            f'Failed to connect to RabbitMQ after {max_attempts} attempts'
        ) from last_error


    def close(self):
        if self.connection and self.connection.is_open:
            logger.info('Closing RabbitMQ connection.')
            self.connection.close()
