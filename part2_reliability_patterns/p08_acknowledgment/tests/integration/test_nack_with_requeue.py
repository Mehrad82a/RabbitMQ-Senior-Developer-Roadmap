"""
Scenario 03: NACK With Requeue

Configuration:
    auto_ack = False
    negative_acknowledgment = basic_nack
    requeue = True

Expected state before NACK:
    - The message is published successfully.
    - The message is retrieved with auto_ack=False.
    - The first delivery has redelivered=False.

Expected state after NACK:
    - RabbitMQ returns the message to the queue.
    - The queue contains one ready message.

Expected state after receiving it again:
    - The message body is unchanged.
    - The delivery has redelivered=True.
    - The second delivery can be acknowledged.

Reason:
    basic_nack with requeue=True tells RabbitMQ that the consumer did not
    complete processing and asks the broker to put the delivery back in the
    queue. RabbitMQ can then deliver it again.

Expected result:
    message_requeued = True
    redelivered_after_nack = True

Note:
    This is an integration test. It publishes a real message, retrieves it
    manually, sends basic_nack(requeue=True), receives the requeued message,
    and acknowledges the second delivery for cleanup.
"""


from collections.abc import Callable

from tests.helpers.rabbitmq import RabbitMQTestClient



def test_nack_with_requeue_returns_message_to_queue(
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


    rabbitmq_client.negatively_acknowledge(
        first_delivery,
        requeue=True,
    )


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




