"""
Scenario: transient failure followed by success.

The first delivery is NACKed with requeue=True. RabbitMQ redelivers it, then
the second delivery is acknowledged and never reaches the DLQ.
"""

import json

from tests.helpers.rabbitmq import RabbitMQTestClient, TestTopology




def test_requeued_task_can_be_processed_successfully(
        rabbitmq_client: RabbitMQTestClient,
        topology: TestTopology,
) -> None:

    task = {
        'task_id': 'transient-recovery-task-123',
        'task_name': 'generate-report',
    }

    rabbitmq_client.publish(
        exchange=topology.task_exchange,
        routing_key=topology.task_routing_key,
        body=json.dumps(task).encode('utf-8'),
    )

    first_delivery = rabbitmq_client.wait_for_message(topology.task_queue)

    assert first_delivery is not None

    first_method, _, _ = first_delivery

    assert first_method.redelivered is False

    rabbitmq_client.channel.basic_nack(
        delivery_tag=first_method.delivery_tag,
        requeue=True,
    )



    second_delivery = rabbitmq_client.wait_for_message(topology.task_queue)

    assert second_delivery is not None

    second_method, _, second_body = second_delivery

    assert second_method.redelivered is True
    assert json.loads(second_body) == task


    rabbitmq_client.channel.basic_ack(delivery_tag=second_method.delivery_tag)

    assert (
            rabbitmq_client.wait_for_message(
                topology.dead_letter_queue,
                timeout=0.3,
            )
            is None
        )