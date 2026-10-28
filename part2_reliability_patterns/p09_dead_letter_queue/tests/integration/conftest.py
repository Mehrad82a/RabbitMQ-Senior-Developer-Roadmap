import pytest

from tests.helpers.rabbitmq import (
    RabbitMQTestClient,
    TestTopology,
    build_test_topology,
)

@pytest.fixture
def rabbitmq_client() -> RabbitMQTestClient:
    client = RabbitMQTestClient()

    try:
        client.connect()

    except Exception as exc:
        client.close()

        pytest.fail(f'Could not connect to RabbitMQ for integration tests: {exc}')


    try:
        yield client

    finally:
        client.close()


@pytest.fixture
def topology(rabbitmq_client: RabbitMQTestClient) -> TestTopology:

    declared_topology = build_test_topology()

    rabbitmq_client.declare_topology(declared_topology)

    try:
        yield declared_topology

    finally:
        rabbitmq_client.delete_topology(declared_topology)






