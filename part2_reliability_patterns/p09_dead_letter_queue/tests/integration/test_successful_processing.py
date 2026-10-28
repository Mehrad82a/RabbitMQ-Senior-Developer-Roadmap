"""
Scenario: successful processing.

A consumer acknowledges the message after successful processing. The task is
removed from the main queue and no message reaches the DLQ.
"""

import json

from tests.helpers.rabbitmq import RabbitMQTestClient, TestTopology




def test_acknowledged_message_is_not_dead_lettered(
        rabbitmq_client: RabbitMQTestClient,
        topology: TestTopology,
) -> None:

    task = {
        'task_id': 'successful-task-123',
        'task_name': 'generate-report',
    }

    rabbitmq_client.publish(
        exchange=topology.task_exchange,
        routing_key=topology.task_routing_key,
        body=json.dumps(task).encode('utf-8'),
    )

    delivery = rabbitmq_client.wait_for_message(topology.task_queue)

    assert delivery is not None

    method, _, body = delivery

    assert json.loads(body) == task

    rabbitmq_client.channel.basic_ack(delivery_tag=method.delivery_tag)

    assert (
        rabbitmq_client.wait_for_message(
            topology.dead_letter_queue,
            timeout=0.3,
        )
        is None
    )




