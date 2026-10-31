import os
import time
from dataclasses import dataclass
from uuid import uuid4

import pika
from pika.adapters.blocking_connection import BlockingChannel

from app.core.config import settings


@dataclass(frozen=True)
class TestTopology:
    task_exchange: str
    task_queue: str
    task_routing_key: str
    dead_letter_exchange: str
    dead_letter_queue: str
    dead_letter_routing_key: str



def build_test_topology() -> TestTopology:
    prefix = f'p09.test.{uuid4().hex}'

    return TestTopology(
        task_exchange=f'{prefix}.exchange',
        task_queue=f'{prefix}.queue',
        task_routing_key=f'{prefix}.process',
        dead_letter_exchange=f'{prefix}.dlx',
        dead_letter_queue=f'{prefix}.dlq',
        dead_letter_routing_key=f'{prefix}.failed',
    )




class RabbitMQTestClient:
    """RabbitMQ client used by P09 integration tests."""


    def __init__(
            self,
            *,
            host: str | None = None,
            port: int | None = None,
    ) -> None:

        self._host = host or settings.rabbitmq_test_host
        self._port = port or settings.rabbitmq_test_port
        self._connection: pika.BlockingConnection | None = None
        self._channel: BlockingChannel | None = None


    @property
    def channel(self) -> BlockingChannel:
        if self._channel is None or not self._channel.is_open:
            raise RuntimeError('RabbitMQ test channel is not available.')

        return self._channel


    def connect(self) -> None:
        credentials = pika.PlainCredentials(
            settings.rabbitmq_user,
            settings.rabbitmq_pass,
        )

        parameters = pika.ConnectionParameters(
            host=self._host,
            port=self._port,
            virtual_host=os.getenv('RABBITMQ_VIRTUAL_HOST', '/'),
            credentials=credentials,
            heartbeat=settings.heartbeat,
            blocked_connection_timeout=settings.blocked_connection_timeout,
            socket_timeout=settings.socket_timeout,
        )

        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()



    def close(self) -> None:
        connection = self._connection

        self._connection = None
        self._channel = None

        if connection is not None and connection.is_open:
            connection.close()



    def declare_topology(
            self,
            topology: TestTopology,
            *,
            task_queue_arguments: dict[str, object] | None = None,
    ) -> None:

        queue_arguments = {
            'x-dead-letter-exchange': topology.dead_letter_exchange,
            'x-dead-letter-routing-key': (
                topology.dead_letter_routing_key
            ),
            **(task_queue_arguments or {}),
        }

        self.channel.exchange_declare(
            exchange=topology.dead_letter_exchange,
            exchange_type='direct',
            durable=False,
            auto_delete=True,
        )

        self.channel.queue_declare(
            queue=topology.dead_letter_queue,
            durable=False,
            exclusive=False,
            auto_delete=True,
        )

        self.channel.queue_bind(
            queue=topology.dead_letter_queue,
            exchange=topology.dead_letter_exchange,
            routing_key=topology.dead_letter_routing_key,
        )

        # -----------------

        self.channel.exchange_declare(
                    exchange=topology.task_exchange,
                    exchange_type='direct',
                    durable=False,
                    auto_delete=True,
                )

        self.channel.queue_declare(
            queue=topology.task_queue,
            durable=False,
            exclusive=False,
            auto_delete=True,
            arguments=queue_arguments,
        )

        self.channel.queue_bind(
            queue=topology.task_queue,
            exchange=topology.task_exchange,
            routing_key=topology.task_routing_key,
        )



    def delete_topology(self, topology: TestTopology) -> None:
        if self._channel is None or not self._channel.is_open:
            return

        for queue_name in (
            topology.task_queue,
            topology.dead_letter_queue,
        ):
            try:
                self.channel.queue_delete(queue=queue_name)

            except pika.exceptions.AMQPError:
                pass


        for exchange_name in (
            topology.task_exchange,
            topology.dead_letter_exchange,
        ):
            try:
                self.channel.exchange_delete(exchange=exchange_name)

            except pika.exceptions.AMQPError:
                pass



    def publish(
            self,
            *,
            exchange: str,
            routing_key: str,
            body: bytes,
            properties: pika.BasicProperties | None = None,
    ) -> None:

        self.channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=body,
            properties=properties
                       or pika.BasicProperties(
                content_type='application/json',
                delivery_mode=2,
            ),
        )



    def wait_for_message(
            self,
            queue_name: str,
            *,
            timeout: float = 5.0
    ) -> tuple[
        pika.spec.Basic.GetOk,
        pika.BasicProperties,
        bytes,
    ] | None:

        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            method, property, body = self.channel.basic_get(queue=queue_name, auto_ack=False)

            if method is not None:
                return method, property, body

            time.sleep(0.05)

        return None



    @staticmethod
    def get_x_death(
            properties: pika.BasicProperties,
    ) -> dict[str, object]:

        headers = properties.headers or {}
        x_death = headers.get('x-death')

        if not isinstance(x_death, list) or not x_death:
            raise AssertionError('Expected RabbitMQ to add an x-death header.')

        latest_death = x_death[0]

        if not isinstance(latest_death, dict):
            raise AssertionError('Expected x-death to contain a header dictionary.')

        return latest_death

