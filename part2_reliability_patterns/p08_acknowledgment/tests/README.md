# P08 Tests

This directory contains the unit and integration tests for P08. The tests examine RabbitMQ acknowledgment behavior and the differences between automatic and manual acknowledgments.

Unit tests use mocks and fakes and do not require a real RabbitMQ broker. Integration tests connect to a real RabbitMQ broker.

## Directory Structure

```text
tests/
├── README.md
├── __init__.py
├── conftest.py
├── fakes/
│   ├── __init__.py
│   └── task_processors.py
├── helpers/
│   ├── __init__.py
│   └── rabbitmq.py
├── integration/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_successful_ack.py
│   ├── test_unacked_message_requeue.py
│   ├── test_nack_with_requeue.py
│   ├── test_reject_without_requeue.py
│   └── test_auto_ack_message_loss.py
└── unit/
    ├── __init__.py
    ├── test_task_processor.py
    ├── test_task_handler.py
    ├── test_manual_ack_consumer.py
    └── test_auto_ack_consumer.py
```

## Test Support Files

### `tests/conftest.py`

Provides general pytest fixtures that can be used by unit tests and other tests. Pytest loads this file automatically; it is not a test module itself.

Fixtures include:

- `task_factory`: Creates a valid task and allows individual fields to be overridden.
- `successful_processor`: Provides a fake processor that succeeds.
- `transient_processor`: Provides a fake processor that raises a temporary failure.
- `permanent_processor`: Provides a fake processor that raises a permanent failure.
- `handler_factory`: Creates a `TaskHandler` with an injected processor.
- `channel_mock`: Creates a strict mock for a RabbitMQ channel.
- Delivery, JSON body, and message property factories.

### `tests/fakes/task_processors.py`

Defines fake processors used by unit tests:

- `SuccessfulTaskProcessor`: Simulates successful processing.
- `TemporarilyFailingTaskProcessor`: Simulates a temporary failure, such as a timeout.
- `PermanentlyFailingTaskProcessor`: Simulates a permanent business validation failure.

These fakes are test-only components and do not belong in the production `app/` directory.

### `tests/helpers/rabbitmq.py`

Provides helper utilities for integration tests that use a real RabbitMQ broker:

- `RabbitMQTestClient`: Manages the test connection and channel.
- `RabbitMQDelivery`: Holds metadata and content for a received message.
- Declares, purges, and deletes test queues.
- Publishes JSON messages.
- Retrieves messages with automatic or manual acknowledgment.
- Sends ACK, NACK, and Reject commands.
- Counts ready messages and waits for an expected count.

### `tests/integration/conftest.py`

Defines fixtures used by integration tests:

- `rabbitmq_client`: Creates a RabbitMQ test client for each test.
- `queue_name`: Generates a unique queue name for each test.
- `test_queue`: Declares a queue before the test and deletes it afterward.

Pytest automatically makes these fixtures available to tests in `tests/integration/`.

The `__init__.py` files make directories importable as Python packages. They do not run tests.

## Unit Tests

Unit tests do not start or connect to a real RabbitMQ broker. They use mocks and fake processors.

### `test_task_processor.py`

Tests `DefaultTaskProcessor` behavior:

- Processes a valid task.
- Trims whitespace from the beginning and end of `task_id` and `task_name`.
- Rejects invalid required fields.
- Rejects a negative processing duration.

Run this test:

```bash
pytest tests/unit/test_task_processor.py -v
```

### `test_task_handler.py`

Tests `TaskHandler` behavior:

- Returns the result from a successful processor.
- Converts `InvalidTaskError` to `PermanentProcessingError`.
- Converts `TimeoutError` and `ConnectionError` to `TransientProcessingError`.
- Propagates known processing errors unchanged.
- Rejects an empty handler name.

Run this test:

```bash
pytest tests/unit/test_task_handler.py -v
```

### `test_manual_ack_consumer.py`

Tests the acknowledgment decisions made by `ManualAckConsumer`:

- Registers the consumer with `auto_ack=False`.
- Sends `basic_ack` after successful processing.
- Sends `basic_nack(requeue=True)` for a temporary failure on the first delivery.
- Sends `basic_reject(requeue=False)` for a temporary failure on redelivery.
- Rejects permanent failures and malformed messages.

Run this test:

```bash
pytest tests/unit/test_manual_ack_consumer.py -v
```

### `test_auto_ack_consumer.py`

Tests `AutoAckConsumer` behavior:

- Registers the consumer with `auto_ack=True`.
- Verifies that the consumer does not send manual ACK, NACK, or Reject commands.
- Covers successful processing, temporary failures, permanent failures, and malformed messages.

Run this test:

```bash
pytest tests/unit/test_auto_ack_consumer.py -v
```

Run all unit tests:

```bash
pytest tests/unit -v
```

## Integration Tests

Integration tests require a reachable RabbitMQ broker. Before running them, start RabbitMQ and configure the connection credentials in `.env`.

For tests running on the host machine, the test connection settings usually need to be:

```env
RABBITMQ_TEST_HOST=localhost
RABBITMQ_TEST_PORT=5672
```

### `test_successful_ack.py`

Retrieves a message with `auto_ack=False`, acknowledges it, closes the connection, and reconnects to verify that the message was not requeued.

```bash
pytest tests/integration/test_successful_ack.py -v
```

### `test_unacked_message_requeue.py`

Retrieves a message without acknowledging it, closes the connection, and verifies that RabbitMQ makes the message available again with `redelivered=True`.

```bash
pytest tests/integration/test_unacked_message_requeue.py -v
```

### `test_nack_with_requeue.py`

Returns a message to the queue with `basic_nack(requeue=True)`. The test verifies that the message is delivered again with `redelivered=True`, then acknowledges the second delivery.

```bash
pytest tests/integration/test_nack_with_requeue.py -v
```

### `test_reject_without_requeue.py`

Rejects a message with `basic_reject(requeue=False)` and verifies that it is no longer available in the queue. Since the test queue has no dead-letter exchange configured, RabbitMQ discards the message.

```bash
pytest tests/integration/test_reject_without_requeue.py -v
```

### `test_auto_ack_message_loss.py`

Retrieves a message with `auto_ack=True`, closes the connection without running business logic, and verifies that RabbitMQ does not return the message to the queue.

This test demonstrates broker behavior using `basic_get(auto_ack=True)`. It does not terminate a running worker process.

```bash
pytest tests/integration/test_auto_ack_message_loss.py -v
```

Run all integration tests:

```bash
pytest tests/integration -v
```

Run all tests:

```bash
pytest -v
```

## Running Tests with Docker

Check the status of the services first:

```bash
docker compose ps
```

If RabbitMQ or the `fastapi` service is not running, start them:

```bash
docker compose up -d rabbitmq fastapi
```

Run unit tests in the `fastapi` service:

```bash
docker compose exec fastapi pytest tests/unit -v
```

Run integration tests in the `fastapi` service:

```bash
docker compose exec fastapi pytest tests/integration -v
```

Run all tests in the `fastapi` service:

```bash
docker compose exec fastapi pytest -v
```

The service name `fastapi` must match the application service name in `docker-compose.yml`.

## Interpreting Test Results

- `PASSED`: The test succeeded and the expected behavior was observed.
- `FAILED`: An assertion did not match the observed behavior. Review the traceback.
- `ERROR`: The test stopped before reaching its assertions because of an environment or setup problem, such as RabbitMQ being unavailable or connection settings being incomplete.
- `ModuleNotFoundError`: A required dependency, such as `pytest` or `pika`, is not installed in the active environment.

## Unit Tests vs. Integration Tests

Unit tests verify the decisions made by application code. For example, they check whether `ManualAckConsumer` calls `basic_nack(requeue=True)` for a temporary failure.

Integration tests verify the behavior of a real RabbitMQ broker. For example, they check whether the broker delivers a NACKed message again and sets `redelivered=True`.

## Acknowledgment Notes

With manual acknowledgment, a message remains unacknowledged until RabbitMQ receives an ACK, NACK, or Reject from the consumer. If the channel or connection closes before the message is settled, RabbitMQ makes the unacknowledged message available again.

With automatic acknowledgment, RabbitMQ considers a message acknowledged as soon as it delivers it. If processing fails after delivery, the message may be lost and will not be returned to the queue.