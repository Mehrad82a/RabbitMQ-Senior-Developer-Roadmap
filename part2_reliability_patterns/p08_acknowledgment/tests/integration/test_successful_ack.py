"""
Scenario 01: Successful Manual Acknowledgment

Configuration:
    auto_ack = False
    processing_result = success

Expected state before receiving the message:
    - The message is published successfully.
    - The queue contains one ready message.

Expected state after receiving the message:
    - The message is delivered with redelivered=False.
    - The message remains unacknowledged until basic_ack is called.

Expected state after acknowledgment:
    - RabbitMQ permanently removes the message.
    - Closing and reopening the connection does not requeue the message.
    - The queue contains no ready message.

Reason:
    With manual acknowledgment, RabbitMQ keeps the delivery in the
    unacknowledged state until the consumer explicitly sends basic_ack.
    Once basic_ack is received on the same channel, RabbitMQ is allowed
    to permanently remove the message.

Expected result:
    message_received = True
    redelivered = False
    message_available_after_ack = False

Note:
    This is an integration test. It publishes a real message to RabbitMQ,
    retrieves it with auto_ack=False, acknowledges it, reconnects, and
    verifies that the message is no longer available.
"""



from collections.abc import Callable

from tests.helpers.rabbitmq import RabbitMQTestClient



def test_successful_ack_removes_message_from_queue(
        rabbitmq_client: RabbitMQTestClient,
        test_queue: str,
        task_factory: Callable[..., dict[str, object]],
) -> None:

    task = task_factory()

    rabbitmq_client.publish(
        queue_name=test_queue,
        message=task,
    )

    rabbitmq_client.wait_for_message_count(
        queue_name=test_queue,
        expected_count=1,
    )

    delivery = rabbitmq_client.get(
        queue_name=test_queue,
        auto_ack=False,
    )

    assert delivery is not None
    assert delivery.json() == task
    assert delivery.redelivered is False

    rabbitmq_client.acknowledge(delivery)

    rabbitmq_client.close()
    rabbitmq_client.connect()

    assert rabbitmq_client.get(
        queue_name=test_queue,
        auto_ack=False,
    ) is None



