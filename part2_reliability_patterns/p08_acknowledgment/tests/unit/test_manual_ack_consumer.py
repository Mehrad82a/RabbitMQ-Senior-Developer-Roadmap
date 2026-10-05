"""
Unit Test Group: Manual Acknowledgment Consumer

Component under test:
    ManualAckConsumer

Acknowledgment matrix:
    successful processing
        -> basic_ack

    transient failure on first delivery
        -> basic_nack(requeue=True)

    transient failure on redelivery
        -> basic_reject(requeue=False)

    permanent failure
        -> basic_reject(requeue=False)

    malformed message
        -> basic_reject(requeue=False)

Expected behavior:
    - Successful messages are acknowledged.
    - A temporary failure receives one requeue opportunity.
    - A redelivered temporary failure is rejected to prevent an
      infinite requeue loop.
    - Permanently invalid messages are rejected without requeueing.
    - The consumer is registered with auto_ack=False.

Note:
    These are unit tests. RabbitMQ is not started. The BlockingChannel
    is replaced with a strict mock and only broker commands are verified.
"""


from collections.abc import Callable, Mapping
from unittest.mock import MagicMock
import pika


from app.consumers.manual_ack_consumer import ManualAckConsumer
from app.services.contracts import TaskProcessor
from app.services.task_handler import TaskHandler
from tests.fakes.task_processors import (
    PermanentlyFailingTaskProcessor,
    SuccessfulTaskProcessor,
    TemporarilyFailingTaskProcessor,
)




def build_manual_consumer(
        processor: TaskProcessor,
        handler_factory: Callable[[TaskProcessor], TaskHandler],
) -> ManualAckConsumer:

    return ManualAckConsumer(
        queue_name='test.manual.queue',
        handler=handler_factory(processor),
    )



def test_start_registers_consumer_with_manual_ack(
        channel_mock: MagicMock,
) -> None:

    rabbitmq_mock = MagicMock()
    rabbitmq_mock.connect.return_value = channel_mock

    consumer = ManualAckConsumer(
        queue_name='test.manual.queue',
        rabbitmq=rabbitmq_mock,
    )

    consumer.start()

    channel_mock.queue_declare.assert_called_once_with(
        queue='test.manual.queue',
        durable=True,
    )

    channel_mock.basic_qos.assert_called_once_with(
        prefetch_count=1,
    )

    channel_mock.basic_consume.assert_called_once_with(
        queue='test.manual.queue',
        on_message_callback=consumer._callback,
        auto_ack=False,
    )

    channel_mock.start_consuming.assert_called_once_with()





def test_successful_processing_sends_basic_ack(
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
        delivery_tag=11,
        redelivered=False,
    )

    consumer = build_manual_consumer(
        successful_processor,
        handler_factory,
    )

    consumer._callback(
        channel_mock,
        method,
        message_properties,
        message_body_factory(task),
    )

    channel_mock.basic_ack.assert_called_once_with(
        delivery_tag=11,
    )

    channel_mock.basic_nack.assert_not_called()
    channel_mock.basic_reject.assert_not_called()





def test_first_transient_failure_is_requeued(
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
        delivery_tag=12,
        redelivered=False,
    )

    consumer = build_manual_consumer(
        transient_processor,
        handler_factory,
    )

    consumer._callback(
        channel_mock,
        method,
        message_properties,
        message_body_factory(task),
    )

    channel_mock.basic_nack.assert_called_once_with(
        delivery_tag=12,
        requeue=True,
    )

    channel_mock.basic_ack.assert_not_called()
    channel_mock.basic_reject.assert_not_called()





def test_redelivered_transient_failure_is_rejected(
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
        delivery_tag=13,
        redelivered=True,
    )


    consumer = build_manual_consumer(
        transient_processor,
        handler_factory,
    )

    consumer._callback(
        channel_mock,
        method,
        message_properties,
        message_body_factory(task),
    )

    channel_mock.basic_reject.assert_called_once_with(
        delivery_tag=13,
        requeue=False,
    )

    channel_mock.basic_ack.assert_not_called()
    channel_mock.basic_nack.assert_not_called()




def test_permanent_failure_is_rejected_without_requeue(
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
        delivery_tag=14,
        redelivered=False,
    )

    consumer = build_manual_consumer(
        permanent_processor,
        handler_factory,
    )

    consumer._callback(
        channel_mock,
        method,
        message_properties,
        message_body_factory(task),
    )

    channel_mock.basic_reject.assert_called_once_with(
        delivery_tag=14,
        requeue=False,
    )


    channel_mock.basic_ack.assert_not_called()
    channel_mock.basic_nack.assert_not_called()



def test_malformed_message_is_rejected_without_requeue(
    delivery_method_factory: Callable[..., pika.spec.Basic.Deliver],
    message_properties: pika.BasicProperties,
    channel_mock: MagicMock,
    successful_processor: SuccessfulTaskProcessor,
    handler_factory: Callable[[TaskProcessor], TaskHandler],
) -> None:

    method = delivery_method_factory(
        delivery_tag=15,
        redelivered=False,
    )

    consumer = build_manual_consumer(
        successful_processor,
        handler_factory,
    )

    consumer._callback(
        channel_mock,
        method,
        message_properties,
        b'invalid-json',
    )

    channel_mock.basic_reject.assert_called_once_with(
        delivery_tag=15,
        requeue=False,
    )

    channel_mock.basic_ack.assert_not_called()
    channel_mock.basic_nack.assert_not_called()