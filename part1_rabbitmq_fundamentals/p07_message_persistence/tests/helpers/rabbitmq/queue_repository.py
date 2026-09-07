from dataclasses import dataclass
import pika

from tests.helpers.rabbitmq.client import RabbitMQTestClient, RabbitMQTestError


@dataclass
class QueueState:
    exists: bool
    message_count: int


class RabbitMQQueueRepository:
    def __init__(self, client: RabbitMQTestClient) -> None:
        self._client = client


    def inspect(self, queue_name: str) -> QueueState:
        if not queue_name.strip():
            raise ValueError("queue name cannot be empty")

        try:
            with self._client.open_channel() as channel:
                declaration = channel.queue_declare(
                    queue=queue_name,
                    passive=True,
                )

                return QueueState(
                    exists=True,
                    message_count=declaration.method.message_count,
                )

        except pika.exceptions.ChannelClosedByBroker as exc:
            if exc.reply_code == 404:
                return QueueState(
                    exists=False,
                    message_count=0,
                )

            raise RabbitMQTestError(
                f'RabbitMQ rejected queue inspection: {queue_name}.'
            ) from exc


        except pika.exceptions.AMQPError as exc:
            raise RabbitMQTestError(
                f'Failed to inspect queue: {queue_name}.'
            ) from exc


    def delete_if_exists(self, queue_name: str) -> None:
        try:
            with self._client.open_channel() as channel:
                channel.queue_delete(
                    queue=queue_name,
                    if_unused=False,
                    if_empty=False,
                )


        except pika.exceptions.ChannelClosedByBroker as exc:
            if exc.reply_code != 404:
                raise RabbitMQTestError(
                    f'Failed to delete test queue: {queue_name}.'
                ) from exc


        except pika.exceptions.AMQPError as exc:
            raise RabbitMQTestError(
                f'Failed to delete test queue: {queue_name}.'
            ) from exc


