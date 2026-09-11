import json
import time

import pika

from collections.abc import Mapping, Iterator
from contextlib import contextmanager
from pika.adapters.blocking_connection import BlockingChannel


from app.core.logger import logger
from app.core.rabbitmq import RabbitMQConnection



class ProducerPublishError(Exception):
    """Raised when a task cannot be published to RabbitMQ."""



class Producer:
    """
    Publishes task messages to a queue through the default exchange.
    """

    MESSAGE_TYPE = 'ack_experiment_task'


    def __init__(self, rabbitmq: RabbitMQConnection | None = None) -> None:
        self._rabbitmq = rabbitmq or RabbitMQConnection()


    def publish(
            self, *, task: Mapping[str, object], queue_name: str) -> None:


        queue_name = self._validate_queue_name(queue_name)
        data = self._serialize_task(task)
        task_id = self._get_task_id(task)


        try:
            with self._channel() as channel:
                channel.queue_declare(
                    queue=queue_name,
                    durable=True,
                )

                channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=data,
                    properties=pika.BasicProperties(
                        content_type='application/json',
                        content_encoding='utf-8',
                        delivery_mode=2,
                        type=self.MESSAGE_TYPE,
                        message_id=task_id,
                        timestamp=int(time.time()),
                    ),
                )


            logger.info(f'Task published successfully: task_id=<{task_id}> | queue=<{queue_name}>')


        except pika.exceptions.AMQPError as exc:
            logger.exception(f'Failed to publish task: {task_id} on queue: {queue_name}')
            raise ProducerPublishError('The RabbitMQ publish operation failed.') from exc



    @contextmanager
    def _channel(self) -> Iterator[BlockingChannel]:
        """
        Yields a dedicated channel on the shared connection and always closes
        it, so a failed publish can never leak a channel.
        """
        self._rabbitmq.connect()

        connection = self._rabbitmq.connection
        if not connection or not connection.is_open:
            raise ProducerPublishError('RabbitMQ connection is not available')

        channel = connection.channel()

        try:
            yield channel

        finally:
            if channel.is_open:
                channel.close()





    @staticmethod
    def _validate_queue_name(queue_name: str) -> str:
        cleaned = queue_name.strip()

        if not cleaned:
            raise ValueError('Queue name cannot be empty')

        return cleaned



    @staticmethod
    def _serialize_task(task: Mapping[str, object]) -> bytes:
        if not task:
            raise ValueError('Task cannot be empty')

        try:
            return json.dumps(
                dict(task),
                ensure_ascii=False,
                separators=(',', ':'),
            ).encode('utf-8')

        except (TypeError, ValueError) as exc:
            raise ProducerPublishError(
                'Task contains values that cannot be serialized to JSON'
            ) from exc



    @staticmethod
    def _get_task_id(task: Mapping[str, object]) -> str:
        task_id = task.get('task_id')

        if task_id is None or str(task_id).strip():
            raise ValueError('Task must contain a non-empty "task_id"')

        return str(task_id).strip()









