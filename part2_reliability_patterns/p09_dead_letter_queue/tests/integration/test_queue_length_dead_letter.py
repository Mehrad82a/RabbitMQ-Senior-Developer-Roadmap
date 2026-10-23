"""
Scenario: queue length limit.

When the source queue reaches its maximum length, RabbitMQ drops the oldest
message and routes it to the DLQ with x-death reason maxlen.
"""

from tests.helpers.rabbitmq import (
    RabbitMQTestClient,
    build_test_topology,
)


def test_message_dropped_by_queue_length_limit_is_dead_lettered(
        rabbitmq_client: RabbitMQTestClient,
) -> None:

    topology = build_test_topology()

    rabbitmq_client.declare_topology(
        topology,
        task_queue_arguments={
            'x-max-length': 1,
            'x-overflow': 'drop-head',
        },
    )

    try:
        first_body = b'{"task_id":"first-task"}'
        second_body =  b'{"task_id":"second-task"}'

        rabbitmq_client.publish(
            exchange=topology.task_exchange,
            routing_key=topology.task_routing_key,
            body=first_body,
        )

        rabbitmq_client.publish(
            exchange=topology.task_exchange,
            routing_key=topology.task_routing_key,
            body=second_body,
        )

        dead_letter = rabbitmq_client.wait_for_message(topology.dead_letter_queue)

        assert dead_letter is not None

        dead_method, dead_properties, dead_body = dead_letter

        assert dead_body == first_body

        x_death = rabbitmq_client.get_x_death(dead_properties)

        assert x_death['reason'] == 'maxlen'
        assert x_death['queue'] == topology.task_queue

        rabbitmq_client.channel.basic_ack(delivery_tag=dead_method.delivery_tag)

        remaining_delivery = rabbitmq_client.wait_for_message(
            topology.task_queue,
        )

        assert remaining_delivery is not None

        remaining_method, _, remaining_body = remaining_delivery

        assert remaining_body == second_body

        remaining_method.channel.basic_ack(delivery_tag=remaining_method.delivery_tag)


    finally:
        rabbitmq_client.delete_topology(topology)



