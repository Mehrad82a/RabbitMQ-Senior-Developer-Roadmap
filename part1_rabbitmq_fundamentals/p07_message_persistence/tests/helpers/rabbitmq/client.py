import time, pika
from collections.abc import Generator
from contextlib import contextmanager

from tests.helpers.settings import (
    RABBITMQ_HOST,
    RABBITMQ_PASS,
    RABBITMQ_PORT,
    RABBITMQ_RETRY_DELAY_SECONDS,
    RABBITMQ_SERVICE_NAME,
    RABBITMQ_START_TIMEOUT_SECONDS,
    RABBITMQ_USER,

)






class RabbitMQTestError(RuntimeError):
    """Raised when a RabbitMQ test operation fails."""



class RabbitMQTestClient:
    def create_connection(self) -> pika.BlockingConnection:
        credentials = pika.PlainCredentials(
            username=RABBITMQ_USER,
            password=RABBITMQ_PASS
        )

        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
        )

        return pika.BlockingConnection(parameters)



    @contextmanager
    def open_channel(self) -> Generator[pika.adapters.blocking_connection.BlockingChannel, None, None]:
        connection = None
        channel = None

        try:
            connection = self.create_connection()
            channel = connection.channel()
            yield channel

        finally:
            if channel and channel.is_open:
                channel.close()

            if connection and connection.is_open:
                connection.close()



    def wait_until_ready(self) -> None:
        deadline = (time.monotonic() + RABBITMQ_START_TIMEOUT_SECONDS)

        last_error: Exception | None = None

        while time.monotonic() < deadline:
            connection = None

            try:
                connection = self.create_connection()
                return

            except (
                pika.exceptions.AMQPConnectionError,
                pika.exceptions.AMQPError,
                OSError
            ) as exc:
                last_error = exc
                time.sleep(RABBITMQ_RETRY_DELAY_SECONDS)

            finally:
                if connection and connection.is_open:
                    connection.close()


        raise RabbitMQTestError(
            'RabbitMQ did not become ready within '
            f'{RABBITMQ_START_TIMEOUT_SECONDS} seconds.'
        ) from last_error







