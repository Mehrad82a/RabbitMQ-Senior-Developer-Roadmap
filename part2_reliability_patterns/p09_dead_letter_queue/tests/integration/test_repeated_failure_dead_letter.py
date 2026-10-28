"""
Scenario: repeated transient failure.

The first failure requeues the task. The second failure rejects it without
requeue, so RabbitMQ transfers it to the DLQ.
"""

import json

from tests.helpers.rabbitmq import RabbitMQTestClient, TestTopology




def test_repeated_transient_failure_is_dead_lettered(
        rabbitmq_client: RabbitMQTestClient,
        topology: TestTopology,
) -> None:

    task = {
        'task_id': 'repeated-failure-task-123',
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

    rabbitmq_client.channel.basic_nack(
        delivery_tag=first_method.delivery_tag,
        requeue=True,
    )


    second_delivery = rabbitmq_client.wait_for_message(topology.task_queue)

    assert second_delivery is not None

    second_method, _, _ = second_delivery

    assert second_method.redelivered is True

    rabbitmq_client.channel.basic_reject(
        delivery_tag=second_method.delivery_tag,
        requeue=False,
    )

    dead_letter = rabbitmq_client.wait_for_message(topology.dead_letter_queue)

    assert dead_letter is not None

    dead_method, dead_properties, dead_body = dead_letter

    assert json.loads(dead_body) == task

    x_death = rabbitmq_client.get_x_death(dead_properties)

    assert x_death['reason'] == 'rejected'
    assert x_death['queue'] == topology.task_queue

    rabbitmq_client.channel.basic_ack(
            delivery_tag=dead_method.delivery_tag,
        )



