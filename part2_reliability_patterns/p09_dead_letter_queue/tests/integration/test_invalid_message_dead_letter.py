"""
Scenario: invalid message.

A Consumer would reject malformed JSON without requeue. This test verifies
that RabbitMQ preserves the original bytes in the DLQ.
"""

from tests.helpers.rabbitmq import RabbitMQTestClient, TestTopology



def test_invalid_message_is_preserved_in_dead_letter_queue(
        rabbitmq_client: RabbitMQTestClient,
        topology: TestTopology,
) -> None:

    invalid_body = b'not-valid-json'

    rabbitmq_client.publish(
        exchange=topology.task_exchange,
        routing_key=topology.task_routing_key,
        body=invalid_body,
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

    assert dead_body == invalid_body

    x_death = rabbitmq_client.get_x_death(dead_properties)

    assert x_death['reason'] == 'rejected'
    assert x_death['queue'] == topology.task_queue

    rabbitmq_client.channel.basic_ack(
        delivery_tag=dead_method.delivery_tag,
    )









