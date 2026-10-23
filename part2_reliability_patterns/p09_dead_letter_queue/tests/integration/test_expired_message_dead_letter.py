"""
Scenario: expired message.

A message expires in its source queue and RabbitMQ sends it to the DLQ with
the x-death reason set to expired.
"""

from tests.helpers.rabbitmq import (
    RabbitMQTestClient,
    build_test_topology,
)




def test_expired_message_is_dead_lettered(
        rabbitmq_client: RabbitMQTestClient,
) -> None:

    topology = build_test_topology()

    rabbitmq_client.declare_topology(
        topology,
        task_queue_arguments={
            'x-message-ttl': 100,
        },
    )


    try:
        body = b'{"task_id":"expired-task-123"}'

        rabbitmq_client.publish(
            exchange=topology.task_exchange,
            routing_key=topology.task_routing_key,
            body=body,
        )

        dead_letter = rabbitmq_client.wait_for_message(
            topology.dead_letter_queue,
            timeout=5,
        )

        assert dead_letter is not None

        dead_method, dead_properties, dead_body = dead_letter

        assert dead_body == body

        assert dead_body == body

        x_death = rabbitmq_client.get_x_death(dead_properties)

        assert x_death['reason'] == 'expired'
        assert x_death['queue'] == topology.task_queue

        rabbitmq_client.channel.basic_ack(
            delivery_tag=dead_method.delivery_tag,
        )

    finally:
        rabbitmq_client.delete_topology(topology)






