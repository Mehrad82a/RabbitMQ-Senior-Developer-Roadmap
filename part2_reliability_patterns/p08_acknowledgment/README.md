# Day 8 — Message Acknowledgment

> Compare automatic and manual RabbitMQ acknowledgments and observe what happens to a delivered message when processing succeeds, fails, or the consumer connection closes.

---

# 🎯 Goal

This project demonstrates when RabbitMQ considers a delivered message complete and what happens when the consumer does not finish processing it.

The project compares two queues and two workers:

```text
ack.auto.queue
    └── AutoAckConsumer: auto_ack=True

ack.manual.queue
    └── ManualAckConsumer: auto_ack=False
```

The API publishes a task to one of these queues based on the `mode` in the request. Both workers run the same processing pipeline. Their acknowledgment behavior is the main difference.

---

# 🧠 What You Will Learn

- Understand `auto_ack=True` and `auto_ack=False`.
- Send a manual ACK only after successful processing.
- Understand the differences between `basic_ack`, `basic_nack`, and `basic_reject`.
- Observe the effect of `requeue=True` and `requeue=False`.
- See what happens to an unacknowledged delivery when its connection closes.
- Understand `delivery_tag` and `redelivered`.
- See how `prefetch_count` limits unacknowledged deliveries in Manual ACK mode.
- Recognize how repeated requeueing can create a requeue loop.
- Understand why manual acknowledgments do not provide exactly-once processing.
- Test application decisions with Unit Tests and broker behavior with Integration Tests.

---

# 🏗️ Architecture

```text
                          Client
                            |
                            v
                       FastAPI API
                            |
                            v
                       Task Service
                            |
                            v
                         Producer
                            |
                            v
                    RabbitMQ Default Exchange
                       /              \
                      /                \
                     v                  v
            ack.auto.queue       ack.manual.queue
                    |                   |
                    v                   v
          AutoAckConsumer       ManualAckConsumer
                    |                   |
                    +---------+---------+
                              |
                              v
                         BaseConsumer
                              |
                              v
                          TaskHandler
                              |
                              v
                     DefaultTaskProcessor
```

Docker Compose starts four services:

```text
rabbitmq
fastapi
auto_ack_worker
manual_ack_worker
```

Each worker receives a different `CONSUMER_MODE` environment value:

```text
auto_ack_worker   → CONSUMER_MODE=auto
manual_ack_worker → CONSUMER_MODE=manual
```

---

# 📁 Project Structure

```text
p08_acknowledgment/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── consumers/
│   │   ├── __init__.py
│   │   ├── auto_ack_consumer.py
│   │   ├── base_consumer.py
│   │   └── manual_ack_consumer.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── rabbitmq.py
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
│   │   ├── test_auto_ack_message_loss.py
│   │   ├── test_nack_with_requeue.py
│   │   ├── test_reject_without_requeue.py
│   │   ├── test_successful_ack.py
│   │   └── test_unacked_message_requeue.py
│   └── unit/
│       ├── __init__.py
│       ├── test_auto_ack_consumer.py
│       ├── test_manual_ack_consumer.py
│       ├── test_task_handler.py
│       └── test_task_processor.py
├── .env.example
├── .gitignore
├── .dockerignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# 🚀 Quick Start

## 1. Open the P08 Directory

From the repository root:

```bash
cd part2_reliability_patterns/p08_acknowledgment
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

Set the RabbitMQ username and password in `.env`. The values used for `RABBITMQ_USER` and `RABBITMQ_PASS` must match the RabbitMQ default credentials used by Docker Compose.

Do not commit `.env` or real credentials to Git.

The example file includes these main settings:

```env
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=your_rabbitmq_username
RABBITMQ_PASS=your_rabbitmq_password

RABBITMQ_DEFAULT_USER=your_rabbitmq_username
RABBITMQ_DEFAULT_PASS=your_rabbitmq_password

AUTO_ACK_QUEUE=ack.auto.queue
MANUAL_ACK_QUEUE=ack.manual.queue

RABBITMQ_TEST_HOST=localhost
RABBITMQ_TEST_PORT=5672
```

Application containers use `RABBITMQ_HOST=rabbitmq` to reach the broker on the Docker Compose network.

Tests launched from the host use `RABBITMQ_TEST_HOST=localhost` and the published AMQP port.

## 3. Check the RabbitMQ Configuration Mount

The Compose file mounts this path as a RabbitMQ configuration file:

```yaml
- ./rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf:ro
```

Make sure `rabbitmq.conf` exists as a file in the P08 project directory before starting Compose. Docker expects the host path to be a file because the container destination is a file.

## 4. Start the Services

```bash
docker compose up --build -d
```

Check their status:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f rabbitmq
docker compose logs -f fastapi
docker compose logs -f auto_ack_worker
docker compose logs -f manual_ack_worker
```

---

# 🌐 Access the Services

| Service | Address |
|---|---|
| FastAPI | `http://localhost:8000` |
| Swagger UI | `http://localhost:8000/docs` |
| RabbitMQ Management | `http://localhost:15672` |
| RabbitMQ AMQP | `localhost:5672` |

Sign in to RabbitMQ Management with the credentials configured in `.env`.

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

The request body accepts:

- `task_name`: required, 1–200 characters, cannot be blank.
- `mode`: either `auto` or `manual`; defaults to `manual`.

Example for Auto ACK:

```json
{
  "task_name": "generate_invoice",
  "mode": "auto"
}
```

Example for Manual ACK:

```json
{
  "task_name": "generate_invoice",
  "mode": "manual"
}
```

The API does not accept a processing outcome or a failure mode. The user chooses only which acknowledgment queue receives the task.

## Example Response

The API returns `202 Accepted` when the task has been published to RabbitMQ:

```json
{
  "task_id": "generated-uuid",
  "task_name": "generate_invoice",
  "created_at": "2026-10-06T10:30:00+00:00",
  "mode": "manual",
  "queue_name": "ack.manual.queue",
  "status": "queued"
}
```

`202 Accepted` means the task was queued. It does not mean the worker has finished processing it.

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
        +---- mode=auto -----> ack.auto.queue
        |
        +---- mode=manual ---> ack.manual.queue
                                  |
                                  v
                           Matching Worker
                                  |
                                  v
                              TaskHandler
                                  |
                                  v
                         DefaultTaskProcessor
                                  |
                                  v
                         ACK decision by mode
```

The task message published by the application contains:

```json
{
  "task_id": "generated-uuid",
  "task_name": "generate_invoice",
  "created_at": "timestamp"
}
```

The `mode`, selected queue, and `status` are included in the API response, but the message body contains the task fields.

---

# ✅ Acknowledgment Concepts

## Automatic Acknowledgment

The Auto ACK worker registers its consumer with:

```python
auto_ack=True
```

RabbitMQ considers a message acknowledged as soon as it delivers the message. The application does not send a manual ACK.

```text
RabbitMQ delivers message
        |
        v
RabbitMQ considers it acknowledged
        |
        v
Business processing runs
```

If processing fails after delivery, RabbitMQ does not requeue the message. The message may be lost.

## Manual Acknowledgment

The Manual ACK worker registers its consumer with:

```python
auto_ack=False
```

RabbitMQ keeps a delivered message unacknowledged until the consumer sends an ACK, NACK, or Reject.

```text
RabbitMQ delivers message
        |
        v
Message remains unacknowledged
        |
        +---- processing succeeds ----> basic_ack
        |
        +---- processing fails -------> basic_nack or basic_reject
```

The application sends a successful ACK only after the business processor completes successfully.

---

# 📨 ACK, NACK, and Reject

## `basic_ack`

Confirms successful processing:

```python
channel.basic_ack(
    delivery_tag=method.delivery_tag,
)
```

After RabbitMQ receives the ACK, it can remove the message.

## `basic_nack`

Negatively acknowledges one or more deliveries and can optionally requeue them:

```python
channel.basic_nack(
    delivery_tag=method.delivery_tag,
    requeue=True,
)
```

In this project, a first transient failure is requeued. If that message fails again and is already marked `redelivered=True`, the Manual ACK consumer rejects it without requeueing to prevent an endless loop.

## `basic_reject`

Rejects a single delivery:

```python
channel.basic_reject(
    delivery_tag=method.delivery_tag,
    requeue=False,
)
```

A permanent failure is rejected without requeueing. Malformed messages are also treated as permanent failures.

No Dead Letter Exchange is configured in this project. Therefore, a message rejected with `requeue=False` is discarded by RabbitMQ.

## Acknowledgment Behavior in This Project

| Processing result | Auto ACK worker | Manual ACK worker |
|---|---|---|
| Success | Already acknowledged on delivery | `basic_ack` |
| Transient failure, first delivery | Message is not requeued | `basic_nack(requeue=True)` |
| Transient failure, redelivered | Message is not requeued | `basic_reject(requeue=False)` |
| Permanent failure | Message is already acknowledged on delivery | `basic_reject(requeue=False)` |
| Malformed message | Message is already acknowledged on delivery | `basic_reject(requeue=False)` |

The default production processor performs a simple task validation and success path. Test-only fake processors simulate temporary and permanent failures in Unit Tests.

---

# 🏷️ `delivery_tag` and `redelivered`

## `delivery_tag`

RabbitMQ assigns a delivery tag to each delivery on a channel.

The consumer must ACK, NACK, or Reject the delivery on the same channel that delivered it. Delivery tags are scoped to their channel; they are not global message IDs.

## `redelivered`

RabbitMQ sets `redelivered=True` when it delivers a message that was previously delivered and returned to the queue.

The Manual ACK consumer uses this flag to allow one retry for a transient failure and then stop requeueing the same failing message indefinitely.

---

# ⚖️ Prefetch

The shared consumer configures:

```python
channel.basic_qos(
    prefetch_count=1,
)
```

With Manual ACK, `prefetch_count=1` limits the number of unacknowledged deliveries to one at a time for that consumer. RabbitMQ waits for the current delivery to be settled before sending another one.

With Auto ACK, the broker considers each delivery acknowledged immediately, so the prefetch limit does not provide the same protection against accumulating unacknowledged messages.

---

# 🔁 Requeue Loops

This can create a loop:

```text
Message delivered
      |
      v
Processing fails
      |
      v
basic_nack(requeue=True)
      |
      v
Same message delivered again
      |
      +------> Processing fails again
```

This project demonstrates a simple one-retry rule:

```text
Transient failure and redelivered=False
    → basic_nack(requeue=True)

Transient failure and redelivered=True
    → basic_reject(requeue=False)
```

This is an educational retry limit. It is not a complete retry architecture. A production retry design may use retry queues, delays, dead-letter exchanges, monitoring, and operational recovery procedures.

---

# ⚠️ Manual ACK Is Not Exactly-Once Processing

Manual ACK prevents RabbitMQ from removing a message before the consumer confirms it. It does not guarantee that business logic runs exactly once.

For example:

```text
Business operation succeeds
        |
        v
Consumer crashes before ACK reaches RabbitMQ
        |
        v
RabbitMQ requeues the unacknowledged message
        |
        v
Business operation may run again
```

Production business operations should be designed to handle duplicate deliveries safely, often using idempotency keys or deduplication.

---

# 🧪 Tests

The P08 tests are divided into Unit Tests and Integration Tests.

- Unit Tests verify application decisions using mocks and fake processors. They do not need RabbitMQ.
- Integration Tests use RabbitMQ to verify actual broker behavior. RabbitMQ must be running and reachable.

See [tests/README.md](tests/README.md) for the detailed test directory guide and per-file commands.

## Run Unit Tests

From the P08 project directory:

```bash
pytest tests/unit -v
```

Run an individual Unit Test file:

```bash
pytest tests/unit/test_task_processor.py -v
pytest tests/unit/test_task_handler.py -v
pytest tests/unit/test_manual_ack_consumer.py -v
pytest tests/unit/test_auto_ack_consumer.py -v
```

## Run Integration Tests from the Host

Configure host-side test settings in `.env`:

```env
RABBITMQ_TEST_HOST=localhost
RABBITMQ_TEST_PORT=5672
```

Make sure RabbitMQ is running, then run:

```bash
pytest tests/integration -v
```

Run one Integration Test:

```bash
pytest tests/integration/test_successful_ack.py -v
pytest tests/integration/test_unacked_message_requeue.py -v
pytest tests/integration/test_nack_with_requeue.py -v
pytest tests/integration/test_reject_without_requeue.py -v
pytest tests/integration/test_auto_ack_message_loss.py -v
```

## Run Tests in Docker

Unit Tests can run inside the FastAPI service:

```bash
docker compose exec fastapi pytest tests/unit -v
```

For Integration Tests inside the Docker network, override the host-side RabbitMQ test hostname so the test container connects to the Compose service:

```bash
docker compose exec `
  -e RABBITMQ_TEST_HOST=rabbitmq `
  fastapi pytest tests/integration -v
```

Run all tests inside the FastAPI service:

```bash
docker compose exec `
  -e RABBITMQ_TEST_HOST=rabbitmq `
  fastapi pytest -v
```

Linux or macOS shell users can write those Docker commands on one line:

```bash
docker compose exec -e RABBITMQ_TEST_HOST=rabbitmq fastapi pytest tests/integration -v
docker compose exec -e RABBITMQ_TEST_HOST=rabbitmq fastapi pytest -v
```

---

# 📋 Integration Scenario Summary

## Scenario 01 — Successful Manual ACK

File:

```text
tests/integration/test_successful_ack.py
```

The test publishes a message, retrieves it with `auto_ack=False`, acknowledges it, reconnects, and verifies that RabbitMQ does not make the message available again.

Expected result:

```text
ACK sent
Message is not requeued
```

## Scenario 02 — Unacked Message Requeued After Connection Loss

File:

```text
tests/integration/test_unacked_message_requeue.py
```

The test receives a message without acknowledging it, closes the connection, reconnects, and verifies that RabbitMQ delivers it again with `redelivered=True`.

Expected result:

```text
Connection closes before ACK
Message is requeued
redelivered=True
```

## Scenario 03 — NACK With Requeue

File:

```text
tests/integration/test_nack_with_requeue.py
```

The test sends `basic_nack(requeue=True)`, retrieves the message again, verifies `redelivered=True`, and acknowledges the second delivery.

Expected result:

```text
basic_nack(requeue=True)
Message is available again
redelivered=True
```

## Scenario 04 — Reject Without Requeue

File:

```text
tests/integration/test_reject_without_requeue.py
```

The test sends `basic_reject(requeue=False)` and verifies that the message is no longer available. Because the test queue has no Dead Letter Exchange, RabbitMQ discards it.

Expected result:

```text
basic_reject(requeue=False)
Message is not available again
```

## Scenario 05 — Auto ACK Message Loss

File:

```text
tests/integration/test_auto_ack_message_loss.py
```

The test retrieves a message using `auto_ack=True`, then reconnects and verifies that RabbitMQ does not requeue it.

This demonstrates the broker's Auto ACK behavior with `basic_get`. It does not terminate a live worker process.

Expected result:

```text
Message delivered with auto_ack=True
No manual ACK is sent
Message is not requeued
```

---

# 🧩 Application Components

## API

Files:

```text
app/api/routes.py
app/api/schemas.py
```

The API accepts a task name and acknowledgment mode. It returns `202 Accepted` after publishing the task.

The API does not accept `processing_outcome` or any failure simulation field.

## Task Service

File:

```text
app/services/task_service.py
```

The service:

- Generates a task ID and creation timestamp.
- Selects the queue based on `mode`.
- Builds the task message.
- Calls the Producer.
- Converts publishing failures into a service-level exception.

## Producer

File:

```text
app/producer/producer.py
```

The Producer:

- Validates the target queue name.
- Serializes the task as JSON.
- Declares a durable queue.
- Publishes persistent messages using `delivery_mode=2`.
- Adds message metadata such as content type and message ID.

This project does not enable Publisher Confirms in its application Producer. A successful API response means the publish operation completed through the application code; Consumer processing is a separate step.

## Base Consumer

File:

```text
app/consumers/base_consumer.py
```

`BaseConsumer` implements the common consumer pipeline:

```text
Declare queue
    ↓
Configure QoS
    ↓
Register callback
    ↓
Deserialize task
    ↓
Call TaskHandler
    ↓
Delegate acknowledgment decision
```

The subclasses provide acknowledgment-specific behavior.

## Auto ACK Consumer

File:

```text
app/consumers/auto_ack_consumer.py
```

Registers with `auto_ack=True`. It logs processing outcomes but does not send manual ACK, NACK, or Reject commands.

## Manual ACK Consumer

File:

```text
app/consumers/manual_ack_consumer.py
```

Registers with `auto_ack=False`. It sends:

- `basic_ack` after successful processing.
- `basic_nack(requeue=True)` for the first transient failure.
- `basic_reject(requeue=False)` for a redelivered transient failure or permanent failure.

## Task Handler and Processor

Files:

```text
app/services/task_handler.py
app/services/task_processor.py
app/services/contracts.py
app/services/exceptions.py
```

`TaskHandler` converts processing errors into transient or permanent failures understood by the consumers.

`DefaultTaskProcessor` validates required task fields and returns a successful result. Failure fakes are kept under `tests/fakes/` and are used in tests.

## RabbitMQ Connection

File:

```text
app/core/rabbitmq.py
```

Manages the application RabbitMQ connection and retries connection attempts according to the configured settings.

## Worker Entry Point

File:

```text
app/worker.py
```

Reads `CONSUMER_MODE`, selects the Auto ACK or Manual ACK consumer, registers shutdown signal handlers, and starts consuming.

---

# 🐳 Docker Compose Services

## `rabbitmq`

Runs RabbitMQ with the management interface.

Published ports:

```text
5672  → AMQP
15672 → Management UI
```

The named volume `rabbitmq_data` stores broker data.

## `fastapi`

Runs the FastAPI application and exposes port `8000`.

Development command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## `auto_ack_worker`

Runs:

```bash
python -m app.worker
```

with:

```text
CONSUMER_MODE=auto
```

## `manual_ack_worker`

Runs:

```bash
python -m app.worker
```

with:

```text
CONSUMER_MODE=manual
```

---

# 🔎 Observe the Application

Check all services:

```bash
docker compose ps
```

Follow Auto ACK worker logs:

```bash
docker compose logs -f auto_ack_worker
```

Follow Manual ACK worker logs:

```bash
docker compose logs -f manual_ack_worker
```

Open RabbitMQ Management:

```text
http://localhost:15672
```

Inspect these queues:

```text
ack.auto.queue
ack.manual.queue
```

Submit tasks to each mode through Swagger and compare the logs and queue behavior.

---

# 🛑 Stop the Services

Stop and remove containers while preserving the named RabbitMQ volume:

```bash
docker compose down
```

To also remove the RabbitMQ volume and all stored broker data:

```bash
docker compose down -v
```

Use `down -v` only when you intentionally want to delete persisted RabbitMQ data.

---

# 📝 Scope and Limitations

This project focuses on acknowledgment behavior and a simple one-retry demonstration.

It does not implement:

- A Dead Letter Exchange or Dead Letter Queue.
- Delayed retry queues.
- A complete retry policy or retry counter.
- Exactly-once message processing.
- Publisher Confirms in the application Producer.
- A real external business dependency such as a payment service.
- A live worker process termination test for Auto ACK message loss.

The Integration Tests exercise RabbitMQ directly to isolate broker acknowledgment behavior. Unit Tests exercise the consumers' decisions using mocks and fake processors.

---

# 🔜 Next Step

The next reliability topic can build on these concepts by introducing Dead Letter Exchanges, retry queues, and controlled delayed retries.

---

# 📝 Author

**Mehrad Abbasi**

GitHub:

https://github.com/Mehrad82a

---

# 📄 License

This project is licensed under the MIT License. See the [LICENSE](../../LICENSE) file for details.