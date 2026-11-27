# P09 Test Suite

This directory contains the Unit Tests and Integration Tests for P09.

The test suite verifies:

- Application task validation.
- Failure classification.
- Producer behavior.
- Consumer ACK, NACK, and Reject decisions.
- RabbitMQ topology declarations.
- Dead-letter routing.
- Transient failure recovery.
- Repeated failure handling.
- Invalid message preservation.
- Message expiration.
- Queue-length overflow.
- RabbitMQ `x-death` metadata.

Unit Tests use mocks and test fakes and do not require a running RabbitMQ broker.

Integration Tests connect to a real RabbitMQ broker and verify actual broker behavior.

---

# 📁 Directory Structure

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
│   ├── test_expired_message_dead_letter.py
│   ├── test_invalid_message_dead_letter.py
│   ├── test_permanent_failure_dead_letter.py
│   ├── test_queue_length_dead_letter.py
│   ├── test_repeated_failure_dead_letter.py
│   ├── test_successful_processing.py
│   └── test_transient_failure_recovery.py
└── unit/
    ├── __init__.py
    ├── test_producer.py
    ├── test_task_consumer.py
    ├── test_task_handler.py
    ├── test_task_processor.py
    ├── test_task_service.py
    └── test_topology.py
```

The `__init__.py` files make the test directories importable as Python packages. They are not test modules and are not executed directly.

---

# 🧰 Test Support Files

## `tests/conftest.py`

Provides the shared `task_factory` fixture.

The factory creates a valid task:

```python
{
    'task_id': 'task-123',
    'task_name': 'generate-report',
    'created_at': '2026-10-17T10:00:00+00:00',
}
```

Tests can override individual values:

```python
task = task_factory(
    task_id='custom-task-id',
    task_name='send-email',
)
```

This avoids duplicating task dictionaries across Unit Tests.

`conftest.py` is loaded automatically by pytest and is not executed as a standalone test file.

---

## `tests/fakes/task_processors.py`

Contains test-only Task Processor implementations.

### `SuccessfulTaskProcessor`

Returns a successful processing result.

Used to verify the normal `TaskHandler` flow.

### `TemporaryFailingTaskProcessor`

Raises:

```python
TimeoutError
```

It simulates a temporary external dependency failure, such as:

- A network timeout.
- An unavailable HTTP service.
- A temporary database connection failure.
- A temporary payment provider failure.

`TaskHandler` converts this failure into:

```python
TransientProcessingError
```

### `PermanentlyFailingTaskProcessor`

Raises:

```python
InvalidTaskError
```

It simulates an unrecoverable business or validation failure.

`TaskHandler` converts this failure into:

```python
PermanentProcessingError
```

These fakes belong only in the `tests/` directory. They are not part of the production application.

---

## `tests/helpers/rabbitmq.py`

Provides reusable RabbitMQ utilities for Integration Tests.

### `TestTopology`

A frozen dataclass containing isolated test topology names:

```text
task_exchange
task_queue
task_routing_key
dead_letter_exchange
dead_letter_queue
dead_letter_routing_key
```

### `build_test_topology`

Generates unique topology names using a UUID:

```text
p09.test.<uuid>.exchange
p09.test.<uuid>.queue
p09.test.<uuid>.process
p09.test.<uuid>.dlx
p09.test.<uuid>.dlq
p09.test.<uuid>.failed
```

Unique names prevent tests from interfering with each other or with the production topology.

### `RabbitMQTestClient`

Manages:

- RabbitMQ test connections.
- RabbitMQ test channels.
- Test topology declaration.
- Source queue DLX arguments.
- Message publishing.
- Message retrieval.
- Topology cleanup.
- `x-death` header extraction.

The helper declares temporary test queues using explicit dead-letter arguments:

```python
{
    'x-dead-letter-exchange': topology.dead_letter_exchange,
    'x-dead-letter-routing-key': topology.dead_letter_routing_key,
}
```

Production topology uses a RabbitMQ policy. Integration Tests use explicit arguments because every test generates unique queue names that do not match the production policy.

### `wait_for_message`

Polls a queue until:

- A message becomes available.
- The configured timeout expires.

Messages are retrieved with:

```python
auto_ack=False
```

Therefore, every received message must eventually be ACKed, NACKed, rejected, or released by closing the connection.

### `get_x_death`

Reads and validates RabbitMQ dead-letter metadata from:

```python
properties.headers['x-death']
```

It raises an assertion error when RabbitMQ did not add the expected metadata.

---

## `tests/integration/conftest.py`

Defines Integration Test fixtures.

### `rabbitmq_client`

For every test, this fixture:

1. Creates `RabbitMQTestClient`.
2. Connects to RabbitMQ.
3. Provides the connected client to the test.
4. Closes the connection during cleanup.

If RabbitMQ cannot be reached, the fixture fails the test with a connection message.

### `topology`

For every test using this fixture:

1. Generates unique exchange and queue names.
2. Declares a main test topology.
3. Declares a dead-letter test topology.
4. Provides the topology to the test.
5. Deletes the queues and exchanges afterward.

The expiration and queue-length tests create their own topology because they require additional queue arguments.

---

# 🧪 Unit Tests

Unit Tests verify application code in isolation.

They do not connect to RabbitMQ and should run quickly.

Run all Unit Tests:

```bash
pytest tests/unit -v
```

---

## `test_task_processor.py`

Tests:

```text
DefaultTaskProcessor
```

Covered behavior:

- Processes a valid task successfully.
- Returns the normalized task ID.
- Returns the normalized task name.
- Removes surrounding whitespace.
- Rejects a missing `task_id`.
- Rejects an empty `task_id`.
- Rejects a blank `task_id`.
- Rejects a non-string `task_id`.
- Rejects a missing `task_name`.
- Rejects an empty `task_name`.
- Rejects a blank `task_name`.
- Rejects a non-string `task_name`.
- Rejects a negative processing duration.

Expected invalid task exception:

```text
InvalidTaskError
```

Run:

```bash
pytest tests/unit/test_task_processor.py -v
```

---

## `test_task_handler.py`

Tests:

```text
TaskHandler
```

Covered behavior:

- Returns the result from a successful processor.
- Converts `TimeoutError` into `TransientProcessingError`.
- Converts `InvalidTaskError` into `PermanentProcessingError`.
- Rejects a blank handler name.
- Preserves useful task context in processing results and exceptions.

Failure classification:

```text
TimeoutError
    → TransientProcessingError

ConnectionError
    → TransientProcessingError

InvalidTaskError
    → PermanentProcessingError
```

Run:

```bash
pytest tests/unit/test_task_handler.py -v
```

---

## `test_topology.py`

Tests:

```text
RabbitMQTopology
```

The RabbitMQ channel is mocked. No broker connection is created.

Covered behavior:

- Declares the Dead Letter Exchange.
- Declares the Dead Letter Queue.
- Binds the DLQ using the dead-letter routing key.
- Declares the main task exchange.
- Declares the main task queue.
- Binds the main queue using the task routing key.
- Declares the dead-letter topology before the task topology.
- Requires an open RabbitMQ channel.
- Rejects using the same name for the main queue and DLQ.

The test intentionally verifies that production queue declaration does not contain hardcoded DLX arguments because the application uses a broker policy.

Run:

```bash
pytest tests/unit/test_topology.py -v
```

---

## `test_producer.py`

Tests:

```text
Producer
```

RabbitMQ connection and topology components are mocked.

Covered behavior:

- Connects to RabbitMQ.
- Declares the topology before publishing.
- Enables Publisher Confirms.
- Publishes to the configured task exchange.
- Uses the configured routing key.
- Uses `mandatory=True`.
- Publishes compact UTF-8 JSON.
- Publishes persistent messages using `delivery_mode=2`.
- Adds content type and content encoding.
- Adds message type and message ID.
- Closes the RabbitMQ connection after publishing.
- Wraps broker failures in `ProducerPublishError`.
- Rejects a missing or invalid `task_id`.
- Rejects non-serializable values.
- Avoids opening a RabbitMQ connection when local validation fails.

Run:

```bash
pytest tests/unit/test_producer.py -v
```

---

## `test_task_service.py`

Tests:

```text
TaskService
```

The Producer is replaced with a mock.

Covered behavior:

- Generates a UUID task ID.
- Generates an ISO-formatted timestamp.
- Normalizes the task name.
- Publishes the generated task.
- Returns the configured queue name.
- Returns the `queued` status.
- Converts `ProducerPublishError` into `TaskPublishError`.
- Rejects a blank task name.
- Does not call the Producer when task validation fails.

Run:

```bash
pytest tests/unit/test_task_service.py -v
```

---

## `test_task_consumer.py`

Tests:

```text
TaskConsumer
```

The Task Handler, RabbitMQ connection, topology, and channel are mocked.

Covered behavior:

- ACKs a successfully processed task.
- NACKs the first transient failure with `requeue=True`.
- Rejects a transient failure after redelivery.
- Rejects a permanent processing failure.
- Rejects malformed JSON.
- Does not call the Task Handler for malformed JSON.
- Rejects unexpected processing failures.
- Declares topology when starting.
- Configures the prefetch count.
- Registers the callback using `auto_ack=False`.
- Starts consuming.
- Closes the RabbitMQ connection.
- Stops an active channel.

Consumer decision rules:

```text
Success
    → basic_ack

Transient failure and redelivered=False
    → basic_nack(requeue=True)

Transient failure and redelivered=True
    → basic_reject(requeue=False)

Permanent failure
    → basic_reject(requeue=False)

Invalid message
    → basic_reject(requeue=False)

Unexpected failure
    → basic_reject(requeue=False)
```

Run:

```bash
pytest tests/unit/test_task_consumer.py -v
```

---

# 🔌 Integration Tests

Integration Tests require a running RabbitMQ broker.

They verify real broker behavior rather than mocked application calls.

Before running them, install dependencies:

```bash
pip install -r requirements.txt
```

Configure host-side test settings in `.env`:

```env
RABBITMQ_TEST_HOST=localhost
RABBITMQ_TEST_PORT=5672
RABBITMQ_USER=your_rabbitmq_username
RABBITMQ_PASS=your_rabbitmq_password
RABBITMQ_VIRTUAL_HOST=/
```

Start RabbitMQ:

```bash
docker compose up -d rabbitmq rabbitmq_setup
```

Run all Integration Tests:

```bash
pytest tests/integration -v
```

---

## `test_successful_processing.py`

Scenario:

```text
Successful processing
```

Flow:

```text
Publish message to the main exchange
    ↓
Retrieve message from the main queue
    ↓
Send basic_ack
    ↓
Verify DLQ remains empty
```

This verifies that an acknowledged message is removed normally and is not dead-lettered.

Run:

```bash
pytest tests/integration/test_successful_processing.py -v
```

---

## `test_permanent_failure_dead_letter.py`

Scenario:

```text
Permanent processing failure
```

Flow:

```text
Publish message
    ↓
Retrieve from main queue
    ↓
basic_reject(requeue=False)
    ↓
Retrieve from DLQ
    ↓
Validate body and x-death
```

Expected metadata:

```text
x-death reason=rejected
x-death queue=<source-queue>
```

Run:

```bash
pytest tests/integration/test_permanent_failure_dead_letter.py -v
```

---

## `test_transient_failure_recovery.py`

Scenario:

```text
Temporary failure followed by successful processing
```

Flow:

```text
First delivery
    ↓
basic_nack(requeue=True)
    ↓
Second delivery
    ↓
redelivered=True
    ↓
basic_ack
    ↓
DLQ remains empty
```

This verifies that a temporary failure can recover after one redelivery.

Run:

```bash
pytest tests/integration/test_transient_failure_recovery.py -v
```

---

## `test_repeated_failure_dead_letter.py`

Scenario:

```text
Temporary failure continues after redelivery
```

Flow:

```text
First delivery
    ↓
basic_nack(requeue=True)
    ↓
Second delivery with redelivered=True
    ↓
basic_reject(requeue=False)
    ↓
Message reaches DLQ
```

Expected metadata:

```text
x-death reason=rejected
x-death queue=<source-queue>
```

This scenario demonstrates how the application can prevent an infinite requeue loop.

Run:

```bash
pytest tests/integration/test_repeated_failure_dead_letter.py -v
```

---

## `test_invalid_message_dead_letter.py`

Scenario:

```text
Invalid message body
```

The test publishes:

```text
not-valid-json
```

It rejects the message without requeueing and verifies that the original bytes are preserved in the DLQ.

Expected metadata:

```text
x-death reason=rejected
x-death queue=<source-queue>
```

Run:

```bash
pytest tests/integration/test_invalid_message_dead_letter.py -v
```

---

## `test_expired_message_dead_letter.py`

Scenario:

```text
Message expiration
```

The test declares a temporary source queue with:

```python
{
    'x-message-ttl': 100,
}
```

Flow:

```text
Publish message
    ↓
Message waits in source queue
    ↓
TTL expires
    ↓
RabbitMQ dead-letters message
    ↓
Message reaches DLQ
```

Expected metadata:

```text
x-death reason=expired
x-death queue=<source-queue>
```

Run:

```bash
pytest tests/integration/test_expired_message_dead_letter.py -v
```

---

## `test_queue_length_dead_letter.py`

Scenario:

```text
Queue-length overflow
```

The test declares a temporary source queue with:

```python
{
    'x-max-length': 1,
    'x-overflow': 'drop-head',
}
```

It publishes two messages.

Expected behavior:

```text
First message  → dead-letter queue
Second message → remains in source queue
```

Expected metadata:

```text
x-death reason=maxlen
x-death queue=<source-queue>
```

Run:

```bash
pytest tests/integration/test_queue_length_dead_letter.py -v
```

---

# ▶️ Running the Test Suite

All commands should be executed from:

```text
part2_reliability_patterns/p09_dead_letter_queue
```

## Run All Unit Tests

```bash
pytest tests/unit -v
```

## Run All Integration Tests

```bash
pytest tests/integration -v
```

## Run All Tests

```bash
pytest -v
```

## Run One Test Function

Example:

```bash
pytest tests/integration/test_permanent_failure_dead_letter.py::test_rejected_message_is_routed_to_dead_letter_queue -v
```

## Show Print and Log Output

```bash
pytest -v -s
```

## Stop After the First Failure

```bash
pytest -x -v
```

## Show Shorter Tracebacks

```bash
pytest --tb=short -v
```

## Run the Last Failed Tests Again

```bash
pytest --lf -v
```

---

# 🐳 Running Tests with Docker

Check service status:

```bash
docker compose ps -a
```

Start RabbitMQ and the application container:

```bash
docker compose up -d rabbitmq rabbitmq_setup fastapi
```

## Run Unit Tests in Docker

```bash
docker compose exec fastapi pytest tests/unit -v
```

## Run Integration Tests in Docker

The `.env` file normally uses:

```env
RABBITMQ_TEST_HOST=localhost
```

That value is correct when pytest runs on the host.

Inside Docker, `localhost` refers to the FastAPI container itself. Override it with the RabbitMQ Compose service name.

Windows PowerShell:

```powershell
docker compose exec `
  -e RABBITMQ_TEST_HOST=rabbitmq `
  fastapi pytest tests/integration -v
```

Linux or macOS:

```bash
docker compose exec -e RABBITMQ_TEST_HOST=rabbitmq fastapi pytest tests/integration -v
```

## Run All Tests in Docker

Windows PowerShell:

```powershell
docker compose exec `
  -e RABBITMQ_TEST_HOST=rabbitmq `
  fastapi pytest -v
```

Linux or macOS:

```bash
docker compose exec -e RABBITMQ_TEST_HOST=rabbitmq fastapi pytest -v
```

---

# 📊 Interpreting Test Results

## `PASSED`

The expected behavior was observed.

Example:

```text
test_rejected_message_is_routed_to_dead_letter_queue PASSED
```

## `FAILED`

The test reached an assertion, but the actual behavior did not match the expected behavior.

Review:

- The assertion message.
- RabbitMQ queue state.
- Exchange and routing-key names.
- `x-death` metadata.
- ACK, NACK, or Reject calls.

## `ERROR`

The test could not reach its assertions because setup, import, fixture creation, or connection failed.

Common causes:

- RabbitMQ is not running.
- Credentials are incorrect.
- The virtual host is incorrect.
- The test hostname is incorrect.
- A dependency is missing.
- Queue declaration arguments conflict with an existing queue.

## `ModuleNotFoundError`

A Python dependency is not installed in the active environment.

Install the project requirements:

```bash
pip install -r requirements.txt
```

## RabbitMQ Connection Failure

For tests running on the host:

```env
RABBITMQ_TEST_HOST=localhost
```

For tests running inside Docker:

```env
RABBITMQ_TEST_HOST=rabbitmq
```

---

# 🧹 Test Isolation and Cleanup

Every standard Integration Test receives a unique topology.

Example:

```text
p09.test.<uuid>.exchange
p09.test.<uuid>.queue
p09.test.<uuid>.dlx
p09.test.<uuid>.dlq
```

This prevents:

- Message leakage between tests.
- Queue declaration conflicts.
- Tests consuming each other’s messages.
- Interference with the production `tasks.queue`.
- Interference with the production `tasks.dlq`.

After each test, the fixture deletes:

- The source queue.
- The dead-letter queue.
- The source exchange.
- The Dead Letter Exchange.

The RabbitMQ connection is then closed.

The expiration and queue-length tests create and delete their specialized topology inside `try/finally` blocks.

---

# ⚠️ Important Testing Notes

## Integration Tests Operate Directly on RabbitMQ

The Integration Tests do not start the real `TaskConsumer`.

They publish, retrieve, ACK, NACK, and Reject messages directly through `RabbitMQTestClient`.

This isolates RabbitMQ behavior from application behavior.

Application decisions are covered separately by Unit Tests.

## Unit Tests Do Not Prove Broker Behavior

A Unit Test can prove that the consumer called:

```python
basic_reject(
    delivery_tag=1,
    requeue=False,
)
```

It cannot prove that RabbitMQ routed the message to a DLQ.

That behavior requires an Integration Test with a real broker.

## Integration Tests Do Not Prove Business Logic

An Integration Test can prove that RabbitMQ routes a rejected message to a DLQ.

It does not prove that `TaskHandler` correctly classified a real business exception.

That behavior belongs in Unit Tests.

## Production Policy and Test Arguments Are Intentionally Different

Production uses:

```text
rabbitmq/definitions.json
```

to configure the DLX through a broker policy.

Integration Tests use queue arguments because test queues have unique UUID-based names and do not match:

```text
^tasks\.queue$
```

Both approaches exercise the same broker dead-letter behavior while keeping tests isolated.

---

# 🧠 Unit Tests vs. Integration Tests

Unit Tests answer questions such as:

```text
Did the consumer ACK a successful task?
Did it requeue the first transient failure?
Did it reject a repeated transient failure?
Did the handler classify the exception correctly?
Did the Producer enable Publisher Confirms?
```

Integration Tests answer questions such as:

```text
Did RabbitMQ route the rejected message to the DLQ?
Did RabbitMQ preserve the original body?
Did RabbitMQ add the x-death header?
Did an expired message reach the DLQ?
Did the oldest message reach the DLQ after max-length overflow?
```

Both layers are required because application decisions and RabbitMQ behavior are different responsibilities.

---

# ✅ Expected Complete Result

After installing dependencies and starting RabbitMQ:

```bash
pytest tests/unit -v
pytest tests/integration -v
```

The expected result is:

```text
All Unit Tests pass.
All Integration Tests pass.
No test topology remains after cleanup.
The production tasks.queue and tasks.dlq are not modified by the test suite.
```