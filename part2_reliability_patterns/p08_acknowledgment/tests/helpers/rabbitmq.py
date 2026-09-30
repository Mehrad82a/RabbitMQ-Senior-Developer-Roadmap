import json
import time
from collections.abc import Mapping
from dataclasses import dataclass


import pika
from pika.adapters.blocking_connection import BlockingChannel

from app.core.config import settings



@dataclass(frozen=True, slots=True)
class RabbitMQDelivery:
    """
    Represents one message retrieved from RabbitMQ during an integration test.
    """

    method: pika.spec.Basic.GetOk
    properties: pika.BasicProperties
    body: bytes

    @property
    def delivery_tag(self) -> int:
        return self.method.delivery_tag

    @property
    def redelivered(self) -> bool:
        return bool(self.method.redelivered)


    def json(self) -> dict[str, object]:
        payload = json.loads(self.body.decode('utf-8'))

        if not isinstance(payload, dict):
            raise ValueError('RabbitMQ message body must contain a JSON object.')
        return payload






class RabbitMQTestClient:
    """
    Small RabbitMQ client dedicated to integration tests.
    """

    def __init__(
            self,
            *,
            host: str | None = None,
            port: int | None = None,
    ) -> None:

        self._host = host or settings.test_rabbitmq_host
        self._port = port or settings.test_rabbitmq_port
        self._connection: pika.BlockingConnection | None = None
        self._channel: BlockingChannel | None = None


    def __enter__(self) -> 'RabbitMQTestClient':
        self.connect()
        return self


    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: object | None
    ) -> None:
        self.close()


    @property
    def channel(self) -> BlockingChannel:
        """
        Return the open test channel.
        """

        if self._channel is None or not self._channel.is_open:
            raise RuntimeError('RabbitMQ test channel is not available.')

        return self._channel


    def connect(self) -> None:
        """
        Open a dedicated RabbitMQ connection and channel.
        """

        if (
            self._connection is not None
            and self._connection.is_open
            and self._channel is not None
            and self._channel.is_open
        ):
            return

        credentials = pika.PlainCredentials(
            settings.rabbitmq_user,
            settings.rabbitmq_pass,
        )

        parameters = pika.ConnectionParameters(
            host=self._host,
            port=self._port,
            credentials=credentials,
            heartbeat=settings.heartbeat,
            blocked_connection_timeout=settings.blocked_connection_timeout,
            connection_attempts=1,
            socket_timeout=settings.socket_timeout,
        )

        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()



    def close(self) -> None:
        """
        Close the connection.
        """

        try:
            if self._connection is not None and self._connection.is_open:
                self._connection.close()
        finally:
            self._channel = None
            self._connection = None


    def declare_queue(self, queue_name: str) -> None:
        """
        Declare a durable test queue.
        """

        self.channel.queue_declare(
            queue=self._validate_queue_name(queue_name),
            durable=True,
        )




    def purge_queue(self, queue_name: str) -> None:
        """
        Remove all ready messages from a test queue.
        """
        self.channel.queue_purge(
            queue=self._validate_queue_name(queue_name),
        )


    def delete_queue(self, queue_name: str) -> None:
        """
        Delete a test queue and its remaining messages.
        """

        self.channel.queue_delete(
            queue=self._validate_queue_name(queue_name),
        )



    def publish(
            self,
            *,
            queue_name: str,
            message: Mapping[str, object],
    ) -> None:

        """
        Publish a persistent JSON message directly to a test queue.
        """

        validated_queue_name = self._validate_queue_name(queue_name)

        body = json.dumps(
            dict(message),
            ensure_ascii=False,
            separators=(',', ':'),
        ).encode('utf-8')

        self.channel.basic_publish(
            exchange='',
            routing_key=validated_queue_name,
            body=body,
            properties=pika.BasicProperties(
                content_type='application/json',
                content_encoding='utf-8',
                delivery_mode=2,
                type='ack_experiment_task',
            ),
            mandatory=True,
        )



    def get(
        self,
        *,
        queue_name: str,
        auto_ack: bool = False,
    ) -> RabbitMQDelivery | None:
        """
        Retrieve one message without starting a consuming loop.

        Returns None when the queue has no ready message.
        """


        method, properties, body = self.channel.basic_get(
            queue=self._validate_queue_name(queue_name),
            auto_ack=auto_ack,
        )

        if method is None:
            return None

        if properties is None or body is None:
            raise RuntimeError('RabbitMQ returned an incomplete delivery.')

        return RabbitMQDelivery(
            method=method,
            properties=properties,
            body=body,
        )



    def acknowledge(self, delivery: RabbitMQDelivery) -> None:
        """
        Acknowledge a successfully processed delivery.
        """

        self.channel.basic_ack(
            delivery_tag=delivery.delivery_tag,
        )


    def negatively_acknowledge(
        self,
        delivery: RabbitMQDelivery,
        *,
        requeue: bool,
    ) -> None:
        """
        Negatively acknowledge a delivery with an explicit requeue decision.
        """

        self.channel.basic_nack(
            delivery_tag=delivery.delivery_tag,
            requeue=requeue,
        )


    def reject(
        self,
        delivery: RabbitMQDelivery,
        *,
        requeue: bool,
    ) -> None:
        """
        Reject one delivery with an explicit requeue decision.
        """

        self.channel.basic_reject(
            delivery_tag=delivery.delivery_tag,
            requeue=requeue,
        )


    def message_count(self, queue_name: str) -> int:
        """
        Return the number of ready messages currently present in the queue.
        """

        result = self.channel.queue_declare(
            queue=self._validate_queue_name(queue_name),
            passive=True,
        )

        return result.method.message_count



    def wait_for_message_count(
            self,
            *,
            queue_name: str,
            expected_count: int,
            timeout_seconds: float = 5.0,
            poll_interval: float = 0.05,
    ) -> None:
        """
        Wait until a queue reaches the expected ready-message count.
        """

        if expected_count < 0:
            raise ValueError('Expected message count cannot be negative.')

        if timeout_seconds <= 0:
            raise ValueError('Timeout must be greater than zero.')

        if poll_interval <= 0:
            raise ValueError('Polling interval must be greater than zero.')

        deadline = time.monotonic() + timeout_seconds
        last_count = self.message_count(queue_name)

        while last_count != expected_count:
            if time.monotonic() >= deadline:
                raise AssertionError(
                    f'Queue <{queue_name}> did not reach the expected '
                    f'message count. Expected: <{expected_count}> | '
                    f'Actual: <{last_count}>.'
                )

            time.sleep(poll_interval)
            last_count = self.message_count(queue_name)



    @staticmethod
    def _validate_queue_name(queue_name: str) -> str:
        if not isinstance(queue_name, str) or not queue_name.strip():
            raise ValueError('Queue name must be a non-empty string.')

        return queue_name.strip()


