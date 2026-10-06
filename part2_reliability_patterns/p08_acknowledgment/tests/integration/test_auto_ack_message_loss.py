"""
Scenario 05: Message Is Lost After Auto ACK Delivery

Configuration:
    auto_ack = True
    consumer_processing = fails immediately after delivery

Expected state before delivery:
    - The message is published successfully.
    - The queue contains one ready message.

Expected state after delivery:
    - RabbitMQ considers the message acknowledged automatically.
    - The queue no longer contains the message.
    - No manual ACK is sent by the test.

Expected state after reconnecting:
    - The message is not returned to the queue.
    - A subsequent get returns no message.

Reason:
    With auto_ack=True, RabbitMQ acknowledges the message as soon as it
    delivers it. If the consumer fails after delivery but before completing
    business processing, RabbitMQ does not requeue the message.

Expected result:
    message_received = True
    message_available_after_processing_failure = False

Note:
    This integration test uses basic_get(auto_ack=True) to demonstrate the
    broker behavior. It simulates processing failure by stopping after
    delivery without running business logic; it does not terminate a live
    worker process.
"""

from collections.abc import Callable

from tests.helpers.rabbitmq import RabbitMQTestClient


def test_auto_ack_message_is_not_requeued_after_consumer_failure(
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
        auto_ack=True,
    )

    assert delivery is not None
    assert delivery.json() == task
    assert delivery.redelivered is False


    rabbitmq_client.close()
    rabbitmq_client.connect()

    assert rabbitmq_client.get(
        queue_name=test_queue,
        auto_ack=False,
    ) is None

