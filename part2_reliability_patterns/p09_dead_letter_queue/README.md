# Day 9 — Dead Letter Queue

> Route messages that cannot be processed successfully to a Dead Letter Queue instead of silently discarding them or requeueing them forever.

---

# 🎯 Goal

This project demonstrates how RabbitMQ handles messages that cannot remain in their original queue.

P09 builds on the acknowledgment behavior introduced in P08 and adds:

- A Dead Letter Exchange.
- A Dead Letter Queue.
- Broker-managed dead-letter routing.
- Dead-letter policies.
- Failure classification.
- Controlled handling of transient and permanent failures.
- Dead-letter metadata through the `x-death` header.
- Dead-lettering caused by rejection, expiration, and queue-length limits.

The application publishes tasks to a main exchange and queue:

```text
tasks.exchange
    |
    | routing_key=tasks.process
    v
tasks.queue
```

Messages that cannot be processed are routed to the dead-letter topology:

```text
tasks.dlx
    |
    | routing_key=tasks.failed
    v
tasks.dlq
```

---

# 🧠 What You Will Learn

- Understand what a Dead Letter Exchange is.
- Understand what a Dead Letter Queue is.
- Configure dead-letter routing using a RabbitMQ policy.
- Understand why broker policies are preferred over hardcoded queue arguments for production topology.
- Route rejected messages to a DLQ.
- Observe dead-lettering caused by message expiration.
- Observe dead-lettering caused by queue-length limits.
- Inspect the RabbitMQ `x-death` header.
- Distinguish transient failures from permanent failures.
- Requeue a transient failure only once.
- Prevent infinite requeue loops.
- Use Publisher Confirms when publishing tasks.
- Understand the difference between application-level decisions and broker-level dead-letter behavior.
- Test application decisions with Unit Tests.
- Test real RabbitMQ dead-letter behavior with Integration Tests.

---

# 🏗️ Architecture

```text
                              Client
                                |
                                v
                           FastAPI API
                                |
                                v
                           TaskService
                                |
                                v
                             Producer
                                |
                                v
                         tasks.exchange
                                |
                  routing_key=tasks.process
                                |
                                v
                           tasks.queue
                                |
                                v
                          TaskConsumer
                                |
                                v
                           TaskHandler
                                |
                                v
                    DefaultTaskProcessor
                                |
                +---------------+---------------+
                |               |               |
                v               v               v
             Success       Transient         Permanent
                            Failure            Failure
                |               |               |
                v               v               v
           basic_ack      First delivery:    basic_reject
                          basic_nack          requeue=False
                          requeue=True             |
                                |                  |
                                v                  |
                           Redelivery              |
                                |                  |
                                v                  |
                          Failure again            |
                                |                  |
                                v                  |
                          basic_reject             |
                          requeue=False            |
                                |                  |
                                +--------+---------+
                                         |
                                         v
                                     tasks.dlx
                                         |
                             routing_key=tasks.failed
                                         |
                                         v
                                     tasks.dlq
```

Docker Compose starts four services:

```text
rabbitmq
rabbitmq_setup
fastapi
worker
```

The `rabbitmq_setup` service is a one-time initialization container. It imports the RabbitMQ definitions containing the dead-letter policy and then exits successfully.

---

# 📁 Project Structure

```text
p09_dead_letter_queue/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── consumers/
│   │   ├── __init__.py
│   │   └── task_consumer.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logger.py
│   │   ├── rabbitmq.py
│   │   └── topology.py
│   ├── producer/
│   │   ├── __init__.py
│   │   └── producer.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── contracts.py
│   │   ├── exceptions.py
│   │   ├── task_handler.py
│   │   ├── task_processor.py
│   │   └── task_service.py
│   ├── __init__.py
│   ├── main.py
│   └── worker.py
├── rabbitmq/
│   └── definitions.json
├── tests/
│   ├── README.md
│   ├── __init__.py
│   ├── conftest.py
│   ├── fakes/
│   │   ├── __init__.py
│   │   └── task_processors.py
│   ├── helpers/
│   │   ├── __init__.py
│   │   └── rabbitmq.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_expired_message_dead_letter.py
│   │   ├── test_invalid_message_dead_letter.py
│   │   ├── test_permanent_failure_dead_letter.py
│   │   ├── test_queue_length_dead_letter.py
│   │   ├── test_repeated_failure_dead_letter.py
│   │   ├── test_successful_processing.py
│   │   └── test_transient_failure_recovery.py
│   └── unit/
│       ├── __init__.py
│       ├── test_producer.py
│       ├── test_task_consumer.py
│       ├── test_task_handler.py
│       ├── test_task_processor.py
│       ├── test_task_service.py
│       └── test_topology.py
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── rabbitmq.conf
├── requirements.txt
└── README.md
```

---

# 🚀 Quick Start

## 1. Open the P09 Directory

From the repository root:

```bash
cd part2_reliability_patterns/p09_dead_letter_queue
```

## 2. Create the Environment File

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux or macOS:

```bash
cp .env.example .env
```

Set the RabbitMQ username and password in `.env`.

The application credentials must match the default RabbitMQ credentials:

```env
RABBITMQ_USER=your_rabbitmq_username
RABBITMQ_PASS=your_rabbitmq_password

RABBITMQ_DEFAULT_USER=your_rabbitmq_username
RABBITMQ_DEFAULT_PASS=your_rabbitmq_password
```

Do not commit `.env` or real credentials to Git.

The main environment settings are:

```env
# RabbitMQ Connection
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=your_rabbitmq_username
RABBITMQ_PASS=your_rabbitmq_password
RABBITMQ_VIRTUAL_HOST=/

# RabbitMQ Default Credentials
RABBITMQ_DEFAULT_USER=your_rabbitmq_username
RABBITMQ_DEFAULT_PASS=your_rabbitmq_password
RABBITMQ_DEFAULT_VHOST=/

# Main Task Topology
TASK_EXCHANGE=tasks.exchange
TASK_QUEUE=tasks.queue
TASK_ROUTING_KEY=tasks.process

# Dead-Letter Topology
DEAD_LETTER_EXCHANGE=tasks.dlx
DEAD_LETTER_QUEUE=tasks.dlq
DEAD_LETTER_ROUTING_KEY=tasks.failed

# Consumer
PREFETCH_COUNT=1

# Test Connection
RABBITMQ_TEST_HOST=localhost
RABBITMQ_TEST_PORT=5672
```

Application containers connect to RabbitMQ through:

```env
RABBITMQ_HOST=rabbitmq
```

Tests executed directly on the host connect through:

```env
RABBITMQ_TEST_HOST=localhost
```

## 3. Check the RabbitMQ Files

Docker Compose mounts the RabbitMQ configuration file:

```yaml
- ./rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf:ro
```

It also mounts the definitions file into the setup container:

```yaml
- ./rabbitmq/definitions.json:/etc/rabbitmq/definitions.json:ro
```

Make sure both paths exist as files before starting the services:

```text
rabbitmq.conf
rabbitmq/definitions.json
```

## 4. Start the Services

```bash
docker compose up --build -d
```

Check the service status:

```bash
docker compose ps -a
```

The expected state is:

```text
rabbitmq       running and healthy
rabbitmq_setup exited successfully with code 0
fastapi        running
worker         running
```

The `rabbitmq_setup` service is expected to exit after importing the definitions.

## 5. View Logs

```bash
docker compose logs -f rabbitmq
docker compose logs rabbitmq_setup
docker compose logs -f fastapi
docker compose logs -f worker
```

---

# 🌐 Access the Services

| Service | Address |
|---|---|
| FastAPI | `http://localhost:8000` |
| Swagger UI | `http://localhost:8000/docs` |
| RabbitMQ Management | `http://localhost:15672` |
| RabbitMQ AMQP | `localhost:5672` |

Sign in to the RabbitMQ Management interface using the credentials configured in `.env`.

---

# 📬 Publish a Task

Open Swagger UI:

```text
http://localhost:8000/docs
```

Use:

```text
POST /tasks/create
```

## Request Schema

The request body accepts one field:

- `task_name`: required, 1–200 characters, and cannot be blank.

Example:

```json
{
  "task_name": "generate-report"
}
```

The client does not send a processing outcome, failure type, acknowledgment mode, exchange name, routing key, or queue name.

Business processing behavior belongs inside the application rather than being selected by the API client.

## Example Response

The API returns `202 Accepted` after successfully publishing the task:

```json
{
  "task_id": "generated-uuid",
  "task_name": "generate-report",
  "created_at": "2026-10-17T10:00:00+00:00",
  "queue_name": "tasks.queue",
  "status": "queued"
}
```

`202 Accepted` means RabbitMQ accepted the published task. It does not mean the worker has completed processing it.

## Published Message

The message body contains:

```json
{
  "task_id": "generated-uuid",
  "task_name": "generate-report",
  "created_at": "2026-10-17T10:00:00+00:00"
}
```

The Producer also adds RabbitMQ message properties:

```text
content_type=application/json
content_encoding=utf-8
delivery_mode=2
type=task
message_id=<task_id>
timestamp=<unix-timestamp>
```

---

# 🔄 Message Flow

```text
POST /tasks/create
        |
        v
TaskRequest validation
        |
        v
TaskService creates task_id and created_at
        |
        v
Producer serializes the task
        |
        v
Producer declares the topology
        |
        v
Publisher Confirms enabled
        |
        v
Publish to tasks.exchange
        |
        v
tasks.process routing key
        |
        v
tasks.queue
        |
        v
TaskConsumer
        |
        v
TaskHandler
        |
        v
DefaultTaskProcessor
        |
        +------ success -----------------> basic_ack
        |
        +------ first transient failure -> basic_nack(requeue=True)
        |
        +------ repeated transient ------> basic_reject(requeue=False)
        |
        +------ permanent failure -------> basic_reject(requeue=False)
        |
        +------ malformed message -------> basic_reject(requeue=False)
        |
        +------ unexpected failure ------> basic_reject(requeue=False)
                                                 |
                                                 v
                                             tasks.dlx
                                                 |
                                                 v
                                             tasks.dlq
```

---

# ☠️ Dead Letter Exchange and Dead Letter Queue

## Dead Letter Exchange

A Dead Letter Exchange is a normal RabbitMQ exchange used as the destination for messages that can no longer remain in their source queue.

This project uses:

```text
tasks.dlx
```

It is declared as a durable direct exchange.

## Dead Letter Queue

A Dead Letter Queue stores messages routed through the Dead Letter Exchange.

This project uses:

```text
tasks.dlq
```

The queue is bound to `tasks.dlx` using:

```text
tasks.failed
```

## Dead-Letter Topology

```text
tasks.dlx
    |
    | routing_key=tasks.failed
    v
tasks.dlq
```

The application declares the DLX, DLQ, and binding in:

```text
app/core/topology.py
```

The main queue receives its dead-letter configuration from the RabbitMQ policy imported from:

```text
rabbitmq/definitions.json
```

---

# 📜 RabbitMQ Dead-Letter Policy

The project configures the source queue using a RabbitMQ policy:

```json
{
  "vhost": "/",
  "name": "tasks-dead-letter-policy",
  "pattern": "^tasks\\.queue$",
  "apply-to": "queues",
  "definition": {
    "dead-letter-exchange": "tasks.dlx",
    "dead-letter-routing-key": "tasks.failed"
  },
  "priority": 10
}
```

The policy applies to:

```text
tasks.queue
```

It configures:

```text
dead-letter-exchange     = tasks.dlx
dead-letter-routing-key  = tasks.failed
```

The application intentionally does not hardcode these arguments in the production `queue_declare` call.

This allows operators to update dead-letter behavior through broker configuration without changing and redeploying application code.

The policy is imported by the one-time Compose service:

```text
rabbitmq_setup
```

Command:

```bash
rabbitmqctl --node rabbit@rabbitmq import_definitions /etc/rabbitmq/definitions.json
```

---

# 📌 When RabbitMQ Dead-Letters a Message

RabbitMQ can dead-letter a message when:

- A consumer rejects it using `basic_reject(requeue=False)`.
- A consumer negatively acknowledges it using `basic_nack(requeue=False)`.
- The message expires because of a TTL.
- The source queue exceeds its configured length limit.
- A quorum queue exceeds its configured delivery limit.

This project demonstrates the first four behaviors through application code and Integration Tests.

---

# 📨 ACK, NACK, Reject, and DLQ Behavior

## Successful Processing

After successful business processing:

```python
channel.basic_ack(
    delivery_tag=delivery_tag,
)
```

Result:

```text
Message is removed from tasks.queue
Message is not routed to tasks.dlq
```

## First Transient Failure

A temporary failure on the first delivery uses:

```python
channel.basic_nack(
    delivery_tag=delivery_tag,
    requeue=True,
)
```

Result:

```text
Message returns to tasks.queue
RabbitMQ redelivers it
redelivered=True
```

The message is not dead-lettered because it was requeued.

## Repeated Transient Failure

If the same message fails again after redelivery:

```python
channel.basic_reject(
    delivery_tag=delivery_tag,
    requeue=False,
)
```

Result:

```text
Message leaves tasks.queue
RabbitMQ routes it through tasks.dlx
Message becomes available in tasks.dlq
```

This prevents an infinite immediate requeue loop.

## Permanent Failure

A permanent business failure uses:

```python
channel.basic_reject(
    delivery_tag=delivery_tag,
    requeue=False,
)
```

The message is routed to the DLQ because retrying the same invalid task is not expected to succeed.

## Invalid Message

Malformed JSON or a body that is not a JSON object is rejected without requeueing.

Examples:

```text
not-valid-json
```

```json
["this", "is", "not", "a", "task", "object"]
```

The original message bytes are preserved in the DLQ.

## Unexpected Failure

An unexpected processing exception is logged and rejected without requeueing.

This avoids keeping a poison message in an uncontrolled requeue loop.

## Decision Summary

| Processing result | Consumer decision | Broker result |
|---|---|---|
| Success | `basic_ack` | Message removed |
| First transient failure | `basic_nack(requeue=True)` | Message redelivered |
| Transient failure after redelivery | `basic_reject(requeue=False)` | Message sent to DLQ |
| Permanent failure | `basic_reject(requeue=False)` | Message sent to DLQ |
| Invalid message | `basic_reject(requeue=False)` | Message sent to DLQ |
| Unexpected failure | `basic_reject(requeue=False)` | Message sent to DLQ |

---

# 🔁 Preventing Requeue Loops

Repeatedly using:

```python
basic_nack(requeue=True)
```

can create an immediate requeue loop:

```text
Message delivered
      |
      v
Processing fails
      |
      v
Message requeued
      |
      v
Message delivered again
      |
      v
Processing fails again
```

Such a loop can consume CPU, network bandwidth, worker capacity, and broker resources.

P09 uses a simple educational rule:

```text
Transient failure and redelivered=False
    → basic_nack(requeue=True)

Transient failure and redelivered=True
    → basic_reject(requeue=False)
    → DLQ
```

This is not a complete retry architecture. It provides one immediate retry and then moves the message to the DLQ.

A later production-oriented design can introduce delayed retry queues and explicit retry counters.

---

# 🏷️ The `redelivered` Flag

RabbitMQ sets:

```text
redelivered=True
```

when a message has previously been delivered and returned to its queue.

The Task Consumer uses this value to distinguish:

```text
First temporary failure
```

from:

```text
Temporary failure after redelivery
```

The flag is useful for this educational one-retry flow, but it is not a complete retry counter.

---

# 🧾 The `x-death` Header

RabbitMQ adds an `x-death` header when it dead-letters a message.

The header contains information such as:

- The dead-letter reason.
- The source queue.
- The number of dead-letter events.
- The exchange from which the message was routed.
- The routing keys associated with the message.
- The time of the dead-letter event.

Example reasons demonstrated in this project:

```text
rejected
expired
maxlen
```

Integration Tests inspect:

```python
x_death['reason']
x_death['queue']
```

Examples:

```text
reason=rejected
queue=<test-source-queue>
```

```text
reason=expired
queue=<test-source-queue>
```

```text
reason=maxlen
queue=<test-source-queue>
```

The `x-death` header is broker-generated metadata. The application does not create it manually.

---

# ⏳ Message Expiration

A message can be dead-lettered after expiring in its source queue.

The expiration Integration Test declares a test queue with:

```python
{
    'x-message-ttl': 100,
}
```

When the message expires, RabbitMQ moves it to the test DLQ and adds:

```text
x-death reason=expired
```

The production `tasks.queue` does not currently configure a TTL. TTL is used only by the isolated Integration Test to demonstrate broker behavior.

---

# 📏 Queue-Length Limit

RabbitMQ can dead-letter messages when a queue exceeds its maximum length.

The queue-length Integration Test declares a source queue with:

```python
{
    'x-max-length': 1,
    'x-overflow': 'drop-head',
}
```

The test publishes two messages:

```text
First message  → oldest message
Second message → remains in the source queue
```

Because the queue can hold only one message, RabbitMQ removes the oldest message and routes it to the DLQ.

The generated `x-death` reason is:

```text
maxlen
```

The production `tasks.queue` does not currently configure a maximum queue length. This behavior is demonstrated only in the isolated Integration Test.

---

# ✅ Publisher Confirms

The Producer enables Publisher Confirms before publishing:

```python
channel.confirm_delivery()
```

It also publishes using:

```python
mandatory=True
```

The message is persistent:

```python
delivery_mode=2
```

Publisher Confirms allow the Producer to detect broker-level publishing failures instead of assuming that every publish operation succeeded.

The publishing flow is:

```text
Serialize task
      |
      v
Open RabbitMQ connection
      |
      v
Declare topology
      |
      v
Enable Publisher Confirms
      |
      v
Publish persistent message
      |
      v
Wait for broker confirmation
      |
      v
Close Producer connection
```

Publisher Confirms do not mean the worker processed the task. They confirm publishing at the broker level.

---

# ⚖️ Prefetch

The Task Consumer configures:

```python
channel.basic_qos(
    prefetch_count=1,
)
```

With manual acknowledgments, this limits the consumer to one unacknowledged delivery at a time.

RabbitMQ waits for the current message to be ACKed, NACKed, or rejected before delivering another message to that consumer.

This prevents one worker from accumulating many unacknowledged messages.

---

# 🧪 Tests

The P09 test suite is divided into Unit Tests and Integration Tests.

- Unit Tests verify application decisions using mocks and fake processors.
- Integration Tests verify real dead-letter behavior using RabbitMQ.

See [tests/README.md](tests/README.md) for the detailed test directory guide and per-file commands.

## Install Test Dependencies

```bash
pip install -r requirements.txt
```

## Run Unit Tests

From the P09 project directory:

```bash
pytest tests/unit -v
```

Run an individual Unit Test file:

```bash
pytest tests/unit/test_task_processor.py -v
pytest tests/unit/test_task_handler.py -v
pytest tests/unit/test_topology.py -v
pytest tests/unit/test_producer.py -v
pytest tests/unit/test_task_service.py -v
pytest tests/unit/test_task_consumer.py -v
```

Unit Tests do not require a running RabbitMQ broker.

## Run Integration Tests from the Host

Make sure `.env` contains:

```env
RABBITMQ_TEST_HOST=localhost
RABBITMQ_TEST_PORT=5672
```

Start RabbitMQ and import the policy:

```bash
docker compose up -d rabbitmq rabbitmq_setup
```

Run all Integration Tests:

```bash
pytest tests/integration -v
```

Run an individual Integration Test file:

```bash
pytest tests/integration/test_successful_processing.py -v
pytest tests/integration/test_permanent_failure_dead_letter.py -v
pytest tests/integration/test_transient_failure_recovery.py -v
pytest tests/integration/test_repeated_failure_dead_letter.py -v
pytest tests/integration/test_invalid_message_dead_letter.py -v
pytest tests/integration/test_expired_message_dead_letter.py -v
pytest tests/integration/test_queue_length_dead_letter.py -v
```

## Run All Tests

```bash
pytest -v
```

## Run Tests in Docker

Start the required services:

```bash
docker compose up -d rabbitmq rabbitmq_setup fastapi
```

Run Unit Tests:

```bash
docker compose exec fastapi pytest tests/unit -v
```

When Integration Tests run inside Docker, the RabbitMQ test host must be the Compose service name:

Windows PowerShell:

```powershell
docker compose exec `
  -e RABBITMQ_TEST_HOST=rabbitmq `
  fastapi pytest tests/integration -v
```

Run all tests inside Docker:

```powershell
docker compose exec `
  -e RABBITMQ_TEST_HOST=rabbitmq `
  fastapi pytest -v
```

Linux or macOS:

```bash
docker compose exec -e RABBITMQ_TEST_HOST=rabbitmq fastapi pytest tests/integration -v
docker compose exec -e RABBITMQ_TEST_HOST=rabbitmq fastapi pytest -v
```

---

# 📋 Integration Scenario Summary

## Scenario 01 — Successful Processing

File:

```text
tests/integration/test_successful_processing.py
```

Flow:

```text
Publish message
    ↓
Receive from main queue
    ↓
basic_ack
    ↓
DLQ remains empty
```

Expected result:

```text
The acknowledged message is not dead-lettered.
```

## Scenario 02 — Permanent Failure

File:

```text
tests/integration/test_permanent_failure_dead_letter.py
```

Flow:

```text
Publish message
    ↓
Receive from main queue
    ↓
basic_reject(requeue=False)
    ↓
Message reaches DLQ
```

Expected metadata:

```text
x-death reason=rejected
```

## Scenario 03 — Transient Failure Recovery

File:

```text
tests/integration/test_transient_failure_recovery.py
```

Flow:

```text
First delivery
    ↓
basic_nack(requeue=True)
    ↓
Second delivery with redelivered=True
    ↓
basic_ack
```

Expected result:

```text
The task is processed after redelivery and does not reach the DLQ.
```

## Scenario 04 — Repeated Transient Failure

File:

```text
tests/integration/test_repeated_failure_dead_letter.py
```

Flow:

```text
First delivery
    ↓
basic_nack(requeue=True)
    ↓
Second delivery
    ↓
basic_reject(requeue=False)
    ↓
Message reaches DLQ
```

Expected metadata:

```text
x-death reason=rejected
```

## Scenario 05 — Invalid Message

File:

```text
tests/integration/test_invalid_message_dead_letter.py
```

The test publishes malformed JSON, rejects it without requeueing, and verifies that RabbitMQ preserves the original message bytes in the DLQ.

Expected result:

```text
Original bytes are preserved
x-death reason=rejected
```

## Scenario 06 — Expired Message

File:

```text
tests/integration/test_expired_message_dead_letter.py
```

The test declares a temporary source queue with a message TTL.

Expected result:

```text
Expired message reaches the DLQ
x-death reason=expired
```

## Scenario 07 — Queue-Length Overflow

File:

```text
tests/integration/test_queue_length_dead_letter.py
```

The test declares a temporary source queue with a maximum length of one and publishes two messages.

Expected result:

```text
Oldest message reaches the DLQ
Newest message remains in the source queue
x-death reason=maxlen
```

---

# 🧩 Application Components

## API

Files:

```text
app/api/routes.py
app/api/schemas.py
```

The API:

- Accepts a task name.
- Validates the request using Pydantic.
- Calls `TaskService`.
- Returns `202 Accepted` after publishing.
- Returns `503 Service Unavailable` when publishing fails.

The API does not accept failure simulation fields.

## Task Service

File:

```text
app/services/task_service.py
```

The service:

- Validates and normalizes the task name.
- Generates a UUID task ID.
- Generates a UTC creation timestamp.
- Builds the task message.
- Calls the Producer.
- Converts Producer failures into `TaskPublishError`.
- Returns task and queue information to the API.

## Producer

File:

```text
app/producer/producer.py
```

The Producer:

- Validates `task_id`.
- Serializes the task as compact UTF-8 JSON.
- Declares the RabbitMQ topology.
- Enables Publisher Confirms.
- Publishes persistent messages.
- Uses `mandatory=True`.
- Adds message metadata.
- Converts RabbitMQ failures into `ProducerPublishError`.
- Closes its connection after every publish attempt.

## RabbitMQ Topology

File:

```text
app/core/topology.py
```

The topology component declares:

- The durable main task exchange.
- The durable main task queue.
- The main queue binding.
- The durable Dead Letter Exchange.
- The durable Dead Letter Queue.
- The dead-letter queue binding.

The DLX settings for the main queue come from the broker policy rather than hardcoded queue arguments.

## Task Consumer

File:

```text
app/consumers/task_consumer.py
```

The consumer:

- Opens a RabbitMQ connection.
- Declares the topology.
- Configures `prefetch_count`.
- Registers with `auto_ack=False`.
- Deserializes message bodies.
- Calls the Task Handler.
- ACKs successful tasks.
- Requeues a first transient failure.
- Rejects repeated transient failures.
- Rejects permanent failures.
- Rejects malformed messages.
- Rejects unexpected failures.
- Logs every processing decision.

## Task Handler

File:

```text
app/services/task_handler.py
```

The handler converts processor-level failures into application-level classifications:

```text
InvalidTaskError
    → PermanentProcessingError

TimeoutError or ConnectionError
    → TransientProcessingError
```

The consumer uses these classifications to choose ACK, NACK, or Reject behavior.

## Task Processor

File:

```text
app/services/task_processor.py
```

`DefaultTaskProcessor`:

- Validates `task_id`.
- Validates `task_name`.
- Normalizes surrounding whitespace.
- Simulates processing time.
- Returns a successful processing result.

Temporary and permanent failures are simulated by test-only fakes under:

```text
tests/fakes/task_processors.py
```

## RabbitMQ Connection

File:

```text
app/core/rabbitmq.py
```

The connection component:

- Creates RabbitMQ connection parameters.
- Uses configured credentials and virtual host.
- Reuses an open channel.
- Opens a new channel when necessary.
- Converts connection failures into `RabbitMQConnectionError`.
- Performs best-effort cleanup.

## Worker Entry Point

File:

```text
app/worker.py
```

The worker:

- Creates `TaskConsumer`.
- Registers `SIGINT` and `SIGTERM` handlers.
- Starts consuming.
- Stops cleanly when shutdown is requested.
- Returns a non-zero exit code after connection or unexpected failures.

---

# 🐳 Docker Compose Services

## `rabbitmq`

Runs RabbitMQ with the Management plugin.

Published ports:

```text
5672  → AMQP
15672 → Management UI
```

The named volume:

```text
rabbitmq_data
```

stores broker data.

## `rabbitmq_setup`

Waits for RabbitMQ to become healthy and imports:

```text
rabbitmq/definitions.json
```

This service creates the dead-letter policy and then exits.

An exit code of `0` is expected.

## `fastapi`

Runs the FastAPI application:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

It waits for:

```text
rabbitmq          healthy
rabbitmq_setup    completed successfully
```

## `worker`

Runs:

```bash
python -m app.worker
```

It also waits for RabbitMQ and the setup service before consuming messages.

---

# 🔎 Observe the Application

## Check Services

```bash
docker compose ps -a
```

## Follow Worker Logs

```bash
docker compose logs -f worker
```

## Follow API Logs

```bash
docker compose logs -f fastapi
```

## Check the Setup Result

```bash
docker compose logs rabbitmq_setup
```

## Open RabbitMQ Management

```text
http://localhost:15672
```

Inspect:

```text
Exchanges:
- tasks.exchange
- tasks.dlx

Queues:
- tasks.queue
- tasks.dlq

Policy:
- tasks-dead-letter-policy
```

Publish a task through Swagger and observe:

- The task entering `tasks.queue`.
- The worker receiving the task.
- The worker acknowledgment logs.
- Failed messages entering `tasks.dlq`.
- The `x-death` header on dead-lettered messages.

---

# 🛑 Stop the Services

Stop and remove containers while preserving broker data:

```bash
docker compose down
```

Stop containers and remove the RabbitMQ named volume:

```bash
docker compose down -v
```

Use `down -v` only when you intentionally want to remove persisted RabbitMQ data, queues, messages, and imported definitions.

---

# 📝 Scope and Limitations

This project focuses on Dead Letter Exchanges and Dead Letter Queues.

It does not implement:

- Delayed retries.
- Retry queues with TTL-based delays.
- Exponential backoff.
- A configurable retry counter.
- A parking-lot queue.
- Automatic DLQ replay.
- A DLQ administration API.
- Message deduplication.
- Exactly-once processing.
- Production metrics or alerting.
- A real external business dependency.
- Automated recovery of failed business operations.
- End-to-end Integration Tests that start the real application worker.

Integration Tests communicate directly with RabbitMQ to isolate and verify broker behavior.

Unit Tests verify application decisions using mocks and fake processors.

---

# 🔜 Next Step

The next reliability pattern can extend this project with retry exchanges, retry queues, delayed redelivery, retry counters, and controlled backoff before a message is finally routed to a DLQ.

---

# 📝 Author

**Mehrad Abbasi**

GitHub:

https://github.com/Mehrad82a

---

# 📄 License

This project is licensed under the MIT License. See the [LICENSE](../../LICENSE) file for details.