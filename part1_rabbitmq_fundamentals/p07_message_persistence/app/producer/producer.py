import json, pika
from app.core.logger import logger
from collections.abc import Mapping
from app.core.rabbitmq import RabbitMQConnection



class ProducerPublishError(Exception):
    """Raised when a message cannot be published to RabbitMQ."""



class Producer:

    def __init__(self, rabbitmq: RabbitMQConnection | None = None) -> None:

        self._rabbitmq = rabbitmq or RabbitMQConnection()


    def publish(
            self,*,
            message: Mapping[str, object],
            queue_name: str,
            queue_durable: bool,
            message_persistent: bool,
            publisher_confirm: bool
    ) -> bool | None:

        if not queue_name.strip():
            raise ValueError('Queue name cannot be empty')

        data = self._serialize_message(message)
        message_id = self._get_message_id(message)

        channel = None

        try:
            self._rabbitmq.connect()

            connection = self._rabbitmq.connection
            if not connection or not connection.is_open:
                raise ProducerPublishError('RabbitMQ connection is not available')

            channel = connection.channel()

            channel.queue_declare(
                queue=queue_name,
                durable=queue_durable,
            )

            if publisher_confirm:
                channel.confirm_delivery()
                logger.info(f'Publisher confirmation enabled: queue={queue_name}')

            channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=data,
                properties=pika.BasicProperties(
                    content_type='application/json',
                    content_encoding='utf-8',
                    delivery_mode=2 if message_persistent else 1,
                    type='persistence_experiment',
                    message_id=message_id,

                ),
                mandatory=publisher_confirm,
            )

            broker_confirmed = True if publisher_confirm else None

            logger.info(f'Message published successfully: message_id={message_id}'
                        f'on queue={queue_name}'
                        f'queue_durable={queue_durable} - message_persistent={message_persistent} - publisher_confirm={broker_confirmed}'
            )

            return broker_confirmed



        except pika.exceptions.NackError as exc:
            logger.exception(f'Message rejected by RabbitMQ: message_id={message_id} queue={queue_name}')
            raise ProducerPublishError('RabbitMQ negatively acknowledged the message.') from exc



        except pika.exceptions.UnroutableError as exc:
            logger.exception(f'Message was not routed: message_id={message_id} queue={queue_name}')
            raise ProducerPublishError(
                'The message could not be routed to the target queue.') from exc



        except pika.exceptions.AMQPError as exc:
            logger.exception(f'Failed to publish message: {message_id} on queue: {queue_name}')
            raise ProducerPublishError('The RabbitMQ publish operation failed.') from exc


        finally:
            if channel and channel.is_open:
                channel.close()




    @staticmethod
    def _serialize_message(message: Mapping[str, object]) -> bytes:
        if not message:
            raise ValueError('Message cannot be empty')

        try:
            return json.dumps(
                dict(message),
                ensure_ascii=False,
                separators=(',', ':'),
            ).encode('utf-8')

        except (TypeError, ValueError) as exc:
            raise ProducerPublishError('Message contains values that cannot be serialized to JSON') from exc



    @staticmethod
    def _get_message_id(message: Mapping[str, object]) -> str | None:
        message_id = message.get('message_id')

        if message_id is None:
            return 'unknown'

        return str(message_id)









