"""
Scenario 02: Unacknowledged Message Is Requeued After Connection Loss

Configuration:
    auto_ack = False
    acknowledgment = not sent
    consumer_connection = closed

Expected state before the connection closes:
    - The message is published successfully.
    - The message is retrieved with auto_ack=False.
    - The delivery remains unacknowledged.

Expected state after the connection closes:
    - RabbitMQ requeues the unacknowledged message.
    - The queue contains one ready message.

Expected state after reconnecting:
    - The message can be received again.
    - The redelivered flag is True.
    - The message can then be acknowledged.

Reason:
    RabbitMQ tracks manual-acknowledgment deliveries as unacknowledged
    until it receives an ACK, NACK, or Reject. If the channel or connection
    closes first, RabbitMQ requeues those deliveries so they can be
    processed again.

Expected result:
    message_received_before_disconnect = True
    message_requeued_after_disconnect = True
    redelivered_after_reconnect = True

Note:
    This is an integration test. It uses a real RabbitMQ connection,
    deliberately closes the connection while a delivery is unacknowledged,
    reconnects, and verifies redelivery.
"""


from collections.abc import Callable

from tests.helpers.rabbitmq import RabbitMQTestClient


def test_unacked_message_is_requeued_after_connection_closes(
        rabbitmq_client: RabbitMQTestClient,
        test_queue: str,
        task_factory: Callable[..., dict[str, object]],
) -> None:

    task = task_factory()

    rabbitmq_client.publish(
        queue_name=test_queue,
        message=task
    )

    rabbitmq_client.wait_for_message_count(
        queue_name=test_queue,
        expected_count=1,
    )

    first_delivery = rabbitmq_client.get(
        queue_name=test_queue,
        auto_ack=False,
    )

    assert first_delivery is not None
    assert first_delivery.json() == task
    assert first_delivery.redelivered is False

    rabbitmq_client.close()
    rabbitmq_client.connect()


    rabbitmq_client.wait_for_message_count(
        queue_name=test_queue,
        expected_count=1,
    )

    redelivered_message = rabbitmq_client.get(
        queue_name=test_queue,
        auto_ack=False,
    )


    assert redelivered_message is not None
    assert redelivered_message.json() == task
    assert redelivered_message.redelivered is True

    rabbitmq_client.acknowledge(redelivered_message)