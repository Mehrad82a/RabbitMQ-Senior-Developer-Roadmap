from tests.helpers.docker_compose import restart_service
from tests.helpers.rabbitmq.client import RabbitMQTestClient
from tests.helpers.rabbitmq.publisher import RabbitMQTestPublisher
from tests.helpers.rabbitmq.queue_repository import QueueState, RabbitMQQueueRepository
from tests.helpers.settings import RABBITMQ_SERVICE_NAME


class RabbitMQScenarioController:
    def __init__(self, client: RabbitMQTestClient | None = None) -> None:
        self._client = client or RabbitMQTestClient()
        self._publisher = RabbitMQTestPublisher(self._client)
        self._queues = RabbitMQQueueRepository(self._client)
        self._declared_queues: set[str] = set()


    def publish_message(self, *, queue_name: str, queue_durable: bool, message_persistent: bool, body: str) -> bool:
        self._declared_queues.add(queue_name)

        return self._publisher.publish(
            queue_name=queue_name,
            queue_durable=queue_durable,
            message_persistent=message_persistent,
            body=body,
        )


    def inspect_queue(self, *, queue_name: str) -> QueueState:
        return self._queues.inspect(queue_name=queue_name)


    def restart_rabbitmq(self) -> None:
        print('\nRestarting RabbitMQ container...')

        restart_service(RABBITMQ_SERVICE_NAME)
        self._client.wait_until_ready()

        print('RabbitMQ is ready again.')

    def cleanup(self) -> None:
        self._client.wait_until_ready()

        for queue_name in self._declared_queues:
            self._queues.delete_if_exists(queue_name)

        self._declared_queues.clear()


