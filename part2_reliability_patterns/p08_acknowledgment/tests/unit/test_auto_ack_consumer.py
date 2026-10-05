"""
Unit Test Group: Automatic Acknowledgment Consumer

Component under test:
    AutoAckConsumer

Acknowledgment behavior:
    successful processing
        -> no manual broker command

    transient failure
        -> no basic_nack and no requeue

    permanent failure
        -> no basic_reject

    malformed message
        -> no manual broker command

Expected behavior:
    RabbitMQ considers the message acknowledged as soon as it delivers
    it because the consumer is registered with auto_ack=True.

    The consumer must never send basic_ack, basic_nack, or basic_reject.
    If processing fails after delivery, the message cannot be recovered
    by this consumer.

Expected comparison result:
    manual_ack_sent = False
    nack_sent = False
    reject_sent = False
    redelivery_possible = False

Note:
    These are unit tests. They verify that AutoAckConsumer does not send
    manual acknowledgment commands. Actual message loss is verified later
    through a RabbitMQ integration test.
"""


from collections.abc import Callable, Mapping
from unittest.mock import MagicMock

import pika

from app.consumers.auto_ack_consumer import AutoAckConsumer
from app.services.contracts import TaskProcessor
from app.services.task_handler import TaskHandler
from tests.fakes.task_processors import (
    PermanentlyFailingTaskProcessor,
    SuccessfulTaskProcessor,
    TemporarilyFailingTaskProcessor,
)



def build_auto_consumer(
        processor: TaskProcessor,
        handler_factory: Callable[[TaskProcessor], TaskHandler],
) -> AutoAckConsumer:

    return AutoAckConsumer(
        queue_name='test.auto.queue',
        handler=handler_factory(processor),
    )



def assert_no_manual_acknowledgment(
    channel_mock: MagicMock,
) -> None:
    channel_mock.basic_ack.assert_not_called()
    channel_mock.basic_nack.assert_not_called()
    channel_mock.basic_reject.assert_not_called()



def test_start_registers_consumer_with_auto_ack(
    channel_mock: MagicMock,
) -> None:

    rabbitmq_mock = MagicMock()
    rabbitmq_mock.connect.return_value = channel_mock

    consumer = AutoAckConsumer(
        queue_name='test.auto.queue',
        rabbitmq=rabbitmq_mock,
    )

    consumer.start()

    channel_mock.queue_declare.assert_called_once_with(
        queue='test.auto.queue',
        durable=True,
    )

    channel_mock.basic_qos.assert_called_once_with(
        prefetch_count=1,
    )

    channel_mock.basic_consume.assert_called_once_with(
        queue='test.auto.queue',
        on_message_callback=consumer._callback,
        auto_ack=True,
    )

    channel_mock.start_consuming.assert_called_once_with()




def test_successful_processing_sends_no_manual_acknowledgment(
    task_factory: Callable[..., dict[str, object]],
    message_body_factory: Callable[[Mapping[str, object]], bytes],
    delivery_method_factory: Callable[..., pika.spec.Basic.Deliver],
    message_properties: pika.BasicProperties,
    channel_mock: MagicMock,
    successful_processor: SuccessfulTaskProcessor,
    handler_factory: Callable[[TaskProcessor], TaskHandler],
) -> None:

    task = task_factory()
    method = delivery_method_factory(
        delivery_tag=21,
        redelivered=False,
    )

    consumer = build_auto_consumer(
        successful_processor,
        handler_factory
    )

    consumer._callback(
        channel_mock,
        method,
        message_properties,
        message_body_factory(task),
    )

    assert_no_manual_acknowledgment(channel_mock)




def test_transient_failure_sends_no_manual_acknowledgment(
    task_factory: Callable[..., dict[str, object]],
    message_body_factory: Callable[[Mapping[str, object]], bytes],
    delivery_method_factory: Callable[..., pika.spec.Basic.Deliver],
    message_properties: pika.BasicProperties,
    channel_mock: MagicMock,
    transient_processor: TemporarilyFailingTaskProcessor,
    handler_factory: Callable[[TaskProcessor], TaskHandler],
) -> None:

    task = task_factory()
    method = delivery_method_factory(
        delivery_tag=22,
        redelivered=False,
    )

    consumer = build_auto_consumer(
        transient_processor,
        handler_factory
    )

    consumer._callback(
        channel_mock,
        method,
        message_properties,
        message_body_factory(task),
    )

    assert_no_manual_acknowledgment(channel_mock)




def test_permanent_failure_sends_no_manual_acknowledgment(
    task_factory: Callable[..., dict[str, object]],
    message_body_factory: Callable[[Mapping[str, object]], bytes],
    delivery_method_factory: Callable[..., pika.spec.Basic.Deliver],
    message_properties: pika.BasicProperties,
    channel_mock: MagicMock,
    permanent_processor: PermanentlyFailingTaskProcessor,
    handler_factory: Callable[[TaskProcessor], TaskHandler],
) -> None:

    task = task_factory()
    method = delivery_method_factory(
        delivery_tag=23,
        redelivered=False,
    )

    consumer = build_auto_consumer(
        permanent_processor,
        handler_factory
    )


    consumer._callback(
        channel_mock,
        method,
        message_properties,
        message_body_factory(task),
    )

    assert_no_manual_acknowledgment(channel_mock)



def test_malformed_message_sends_no_manual_acknowledgment(
    delivery_method_factory: Callable[..., pika.spec.Basic.Deliver],
    message_properties: pika.BasicProperties,
    channel_mock: MagicMock,
    successful_processor: SuccessfulTaskProcessor,
    handler_factory: Callable[[TaskProcessor], TaskHandler],
) -> None:

    method = delivery_method_factory(
        delivery_tag=24,
        redelivered=False,
    )

    consumer = build_auto_consumer(
        successful_processor,
        handler_factory
    )

    consumer._callback(
        channel_mock,
        method,
        message_properties,
        b'invalid-json',
    )

    assert_no_manual_acknowledgment(channel_mock)


