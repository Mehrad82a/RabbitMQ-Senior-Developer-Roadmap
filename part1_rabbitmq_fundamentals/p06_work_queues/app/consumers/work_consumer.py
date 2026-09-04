import pika, json


from app.core.logger import logger
from app.core.rabbitmq import RabbitMQConnection
from app.consumers.base_consumer import BaseConsumer
from app.services.handlers.base_handler import BaseHandler



class WorkConsumer(BaseConsumer):
    def __init__(
            self,
            queue_name: str,
            handler: BaseHandler,
            rabbitmq: RabbitMQConnection | None = None
    ) -> None:

        super().__init__(
            queue_name=queue_name,
            rabbitmq=rabbitmq,
        )

        self._handler = handler


    def _callback(
            self,
            channel: pika.adapters.blocking_connection.BlockingChannel,
            method: pika.spec.Basic.Deliver,
            properties: pika.spec.BasicProperties,
            body: bytes
    ) -> None:


        try:
            task = self._deserialize_message(body)
            logger.info(f"[{self.__class__.__name__}] Task Received: task_id<{task.get('task_id')}>")


        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            logger.exception(f'Invalid message received: delivery_tag={method.delivery_tag}')

            channel.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=False,
            )
            return



        try:
            logger.info(f"[{self.__class__.__name__}] Task Processing started for task:<{task.get('task_id')}>")

            result = self._handler.process(task)

            logger.info(f'[{self.__class__.__name__}] Result: {result}')
            channel.basic_ack(
                delivery_tag=method.delivery_tag
            )

            logger.info(f"[{self.__class__.__name__}] Task with task_id={task.get('task_id')} acknowledged successfully")


        except Exception as e:
            logger.exception(f"[{self.__class__.__name__}] Task with task_id={task.get('task_id')} not acknowledged | Error: {e}")

            channel.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=True,
            )


    @staticmethod
    def _deserialize_message(body: bytes) -> dict[str, object]:
        message = body.decode('utf-8')
        task = json.loads(message)

        if not isinstance(task, dict):
            raise ValueError('Message body must contain a JSON object')

        return task







