from collections.abc import Iterator
from uuid import uuid4
import pytest

from tests.helpers.rabbitmq import RabbitMQTestClient




@pytest.fixture
def rabbitmq_client() -> Iterator[RabbitMQTestClient]:
    """
    Provide an isolated RabbitMQ client for one integration test.
    """

    client = RabbitMQTestClient()
    client.connect()

    try:
        yield client

    finally:
        client.close()



@pytest.fixture
def queue_name(request: pytest.FixtureRequest) -> str:
    """
    Create a unique queue name for each integration-test scenario.
    """
    scenario_name = request.node.name.strip().lower().replace('_', '-')

    return f'p08.test.{scenario_name}.{uuid4()}'



@pytest.fixture
def test_queue(
        rabbitmq_client: RabbitMQTestClient,
        queue_name: str,
) -> Iterator[str]:
    """
    Declare an isolated queue and delete it after the test.
    """

    rabbitmq_client.declare_queue(queue_name)

    try:
        yield queue_name

    finally:
        rabbitmq_client.connect()
        rabbitmq_client.delete_queue(queue_name)
