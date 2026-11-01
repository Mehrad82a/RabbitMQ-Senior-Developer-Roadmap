"""
Scenario: permanent failure.

Rejecting a message without requeue moves it to the dead-letter queue.
"""

import json

from tests.helpers.rabbitmq import RabbitMQTestClient, TestTopology



def test_rejected_message_is_routed_to_dead_letter_queue(
        rabbitmq_client: RabbitMQTestClient,
        topology: TestTopology,
) -> None:

    task = {
        'task_id': 'permanent-failure-task-123',
        'task_name': 'generate-report',
    }

    rabbitmq_client.publish(
        exchange=topology.task_exchange,
        routing_key=topology.task_routing_key,
        body=json.dumps(task).encode('utf-8'),
    )

    delivery = rabbitmq_client.wait_for_message(topology.task_queue)

    assert delivery is not None


    method, _, _ = delivery

    rabbitmq_client.channel.basic_reject(
        delivery_tag=method.delivery_tag,
        requeue=False,
    )

    dead_letter = rabbitmq_client.wait_for_message(topology.dead_letter_queue)

    assert dead_letter is not None

    dead_method, dead_properties, dead_body = dead_letter

    assert json.loads(dead_body) == task

    x_death = rabbitmq_client.get_x_death(dead_properties)

    assert x_death['reason'] == 'rejected'
    assert x_death['queue'] == topology.task_queue

    rabbitmq_client.channel.basic_ack(delivery_tag=dead_method.delivery_tag)




