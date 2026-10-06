"""
Publisher Confirm Integration Tests

Purpose:
    Verify the result returned by the application Producer when Publisher
    Confirms are enabled or disabled.

Scenarios:
    1. Publisher Confirms enabled:
       - RabbitMQ confirms the publish.
       - Producer returns True.
       - The message is present in the queue.

    2. Publisher Confirms disabled:
       - Producer does not wait for a broker confirmation.
       - Producer returns None.
       - The message is still published to the queue.

Reason:
    Publisher Confirms tell the Producer whether RabbitMQ accepted
    responsibility for a published message. They do not confirm that a
    Consumer processed the message or that it will survive a broker restart.

Note:
    These are integration tests. They connect to a real RabbitMQ broker.
    The test queue is unique and is deleted after each test.
"""

from uuid import uuid4

import pytest

from tests.helpers.rabbitmq.client import RabbitMQTestClient
from tests.helpers.rabbitmq.queue_repository import RabbitMQQueueRepository
from tests.helpers.settings import (
    RABBITMQ_HOST as RABBITMQ_TEST_HOST,
    RABBITMQ_PASS,
    RABBITMQ_PORT as RABBITMQ_TEST_PORT,
    RABBITMQ_USER,
)


@pytest.mark.parametrize(
    ('publisher_confirm', 'expected_result'),
    [
        (True, True),
        (False, None),
    ],
)
def test_publisher_confirm_returns_expected_result(
    publisher_confirm: bool,
    expected_result: bool | None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify the Producer result with confirms both enabled and disabled.
    """


    monkeypatch.setenv('RABBITMQ_HOST', RABBITMQ_TEST_HOST)
    monkeypatch.setenv('RABBITMQ_PORT', str(RABBITMQ_TEST_PORT))
    monkeypatch.setenv('RABBITMQ_USER', RABBITMQ_USER)
    monkeypatch.setenv('RABBITMQ_PASS', RABBITMQ_PASS)

    from app.core.rabbitmq import RabbitMQConnection
    from app.producer.producer import Producer

    queue_name = f'p07.test.publisher-confirm.{uuid4().hex}'
    message = {
        'message_id': str(uuid4()),
        'content': 'Publisher confirm integration test',
    }

    rabbitmq = RabbitMQConnection()
    producer = Producer(rabbitmq=rabbitmq)
    queue_repository = RabbitMQQueueRepository(RabbitMQTestClient())

    try:
        broker_confirmed = producer.publish(
            message=message,
            queue_name=queue_name,
            queue_durable=True,
            message_persistent=True,
            publisher_confirm=publisher_confirm,
        )

        assert broker_confirmed is expected_result

        queue_state = queue_repository.inspect(queue_name)

        assert queue_state.exists is True
        assert queue_state.message_count == 1

    finally:
        queue_repository.delete_if_exists(queue_name)
        rabbitmq.close()