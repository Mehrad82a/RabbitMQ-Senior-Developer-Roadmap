"""
Scenario 04: Reject Without Requeue

Configuration:
    auto_ack = False
    rejection = basic_reject
    requeue = False
    dead_letter_exchange = not configured

Expected state before rejection:
    - The message is published successfully.
    - The message is retrieved with auto_ack=False.
    - The delivery has redelivered=False.

Expected state after rejection:
    - RabbitMQ does not put the message back in the queue.
    - The queue has no ready messages.
    - A subsequent get returns no message.

Reason:
    basic_reject with requeue=False tells RabbitMQ not to return the
    delivery to its queue. Since this test queue has no dead-letter exchange
    configured, RabbitMQ discards the rejected message.

Expected result:
    message_requeued = False
    message_available_after_reject = False

Note:
    This is an integration test. It publishes a real message, retrieves it
    manually, rejects it with requeue=False, and verifies that it is no
    longer available.
"""

from collections.abc import Callable

from tests.helpers.rabbitmq import RabbitMQTestClient



def test_reject_without_requeue_removes_message_from_queue(
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


    rabbitmq_client.reject(
        delivery,
        requeue=False,
    )

    rabbitmq_client.wait_for_message_count(
        queue_name=test_queue,
        expected_count=0,
    )

    assert rabbitmq_client.get(
        queue_name=test_queue,
        auto_ack=False,
    ) is None





