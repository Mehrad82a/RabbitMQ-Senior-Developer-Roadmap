import pika
from tests.helpers.rabbitmq.client import RabbitMQTestClient, RabbitMQTestError




class RabbitMQTestPublisher:
    def __init__(self, client: RabbitMQTestClient) -> None:
        self._client = client


    def publish(self, *, queue_name: str, queue_durable: bool, message_persistent: bool, body:str) -> bool:
        if not queue_name.strip():
            raise ValueError('Queue name cannot be empty')

        try:
            with self._client.open_channel() as channel:
                channel.queue_declare(
                    queue=queue_name,
                    durable=queue_durable,
                    exclusive=False,
                    auto_delete=False
                )

                channel.confirm_delivery()

                channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=body.encode('utf-8'),
                    properties=pika.BasicProperties(
                        content_type='text/plain',
                        content_encoding='utf-8',
                        delivery_mode=(2 if message_persistent else 1),
                    ),
                    mandatory=True,
                )

            return True


        except pika.exceptions.NackError as exc:
            raise RabbitMQTestError(
                'RabbitMQ negatively acknowledged the test message.'
            ) from exc


        except pika.exceptions.UnroutableError as exc:
            raise RabbitMQTestError(
                'The test message could not be routed.'
            ) from exc


        except pika.exceptions.AMQPError as exc:
            raise RabbitMQTestError(
                'The test message could not be published.'
            ) from exc








