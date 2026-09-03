import json, pika
from app.core.logger import logger
from collections.abc import Mapping
from app.core.rabbitmq import RabbitMQConnection




class Producer:

    def __init__(self, queue_name: str, rabbitmq: RabbitMQConnection | None = None) -> None:

        if not queue_name.strip():
            raise ValueError('Queue name cannot be empty')

        self._queue_name = queue_name
        self._rabbitmq = rabbitmq or RabbitMQConnection()



    def publish(self, task: Mapping[str, object]) -> None:

        data = self._serialize_task(task)

        try:
            channel = self._rabbitmq.connect()

            self._declare_queue(channel)

            channel.basic_publish(
                exchange='',
                routing_key=self._queue_name,
                body=data,
                properties=pika.BasicProperties(
                    content_type='application/json',
                    content_encoding='utf-8',
                    delivery_mode=2,
                    type='work_task',
                    message_id=self._get_task_id(task),
                ),
            )

            logger.info(
                'Task published successfully: task_id=%s queue=%s',
                task.get('task_id', 'unknown'),
                self._queue_name,
            )

        except pika.exceptions.AMQPError:
            logger.exception(
                'Failed to publish task: task_id=%s queue=%s',
                task.get('task_id', 'unknown'),
                self._queue_name,
            )
            raise



    def _declare_queue(self, channel: pika.adapters.blocking_connection.BlockingChannel) -> None:
        channel.queue_declare(
            queue=self._queue_name,
            durable=True,
        )


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
            raise ValueError('Task message must contain JSON-serializable values') from exc



    @staticmethod
    def _get_task_id(task: Mapping[str, object]) -> str | None:
        task_id = task.get('task_id')

        if task_id is None:
            return None

        return str(task_id)

