# Day 7 — Message Persistence and Broker Recovery

> Compare queue durability, message persistence, publisher confirms, and consumer acknowledgements using RabbitMQ, FastAPI, Pika, Docker, and Pytest.

---

# 🎯 Goal

In this project, we explore what RabbitMQ can and cannot recover after a broker restart.

Queue durability and message persistence solve two different problems:

- A **durable queue** stores its metadata so the queue can be recovered after RabbitMQ restarts.
- A **persistent message** requests durable storage by using `delivery_mode=2`.

For a queued message to survive broker recovery, both conditions must be satisfied:

```text
Durable Queue + Persistent Message
                 ↓
       Message can be recovered
```

This project compares four persistence combinations:

```text
1. Non-durable Queue + Transient Message
2. Non-durable Queue + Persistent Message
3. Durable Queue + Transient Message
4. Durable Queue + Persistent Message
```

It also demonstrates that Publisher Confirms and Consumer Acknowledgements are separate reliability mechanisms.

---

# 🧠 What You Will Learn

- Understand Queue durability
- Understand Message persistence
- Compare transient and persistent Messages
- Use `delivery_mode=1` and `delivery_mode=2`
- Enable Publisher Confirms
- Understand `broker_confirmed=True`
- Understand `broker_confirmed=None`
- Use mandatory publishing
- Detect unroutable Messages
- Use manual Consumer acknowledgements
- Handle invalid Messages with NACK
- Separate message consumption from business logic
- Apply Handler-based architecture
- Run RabbitMQ, FastAPI, and a Worker with Docker Compose
- Verify recovery behavior using real Integration Tests
- Restart RabbitMQ automatically from Pytest
- Inspect Queue state before and after Broker restart
- Restore Docker services after test execution

---

# 🏗️ Architecture

```text
                         Client
                            |
                            v
                       FastAPI API
                            |
                            v
                  Persistence Service
                            |
                            v
                         Producer
                            |
                            v
                  RabbitMQ Default Exchange
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
   Non-durable Queues                  Durable Queues
          |                                 |
          +-----------------+---------------+
                            |
                            v
                  Persistence Consumer
                            |
                            v
                  Persistence Handler
                            |
                            v
                    ACK or NACK Result
```

There is one Worker process in this project.

The Worker registers one Consumer callback on each of the four experiment Queues.

---

# 📁 Project Structure

```text
p07_message_persistence/
│
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── schemas.py
│   │
│   ├── consumers/
│   │   ├── __init__.py
│   │   └── persistence_consumer.py
│   │
│   ├── producer/
│   │   ├── __init__.py
│   │   └── producer.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── persistence_service.py
│   │   └── handlers/
│   │       ├── __init__.py
│   │       └── persistence_handler.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── rabbitmq.py
│   │
│   ├── __init__.py
│   ├── main.py
│   └── worker.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   │
│   ├── helpers/
│   │   ├── __init__.py
│   │   ├── docker_compose.py
│   │   ├── settings.py
│   │   └── rabbitmq/
│   │       ├── __init__.py
│   │       ├── client.py
│   │       ├── publisher.py
│   │       ├── queue_repository.py
│   │       └── scenario.py
│   │
│   └── scenarios/
│       ├── __init__.py
│       ├── test_publisher_confirm.py
│       ├── test_scenario_01_non_durable_transient_message.py
│       ├── test_scenario_02_non_durable_persistent_message.py
│       ├── test_scenario_03_durable_transient_message.py
│       └── test_scenario_04_durable_persistent_message.py
│
├── .env.example
├── .gitignore
├── .dockerignore
├── docker-compose.yml
├── Dockerfile
├── rabbitmq.conf
├── requirements.txt
└── README.md
```

---

# 🚀 Quick Start

## 1. Clone the Repository

```bash
git clone https://github.com/Mehrad82a/RabbitMQ-Senior-Developer-Roadmap.git

cd part1_rabbitmq_fundamentals/p07_message_persistence
```

---

## 2. Create the Environment File

Linux and macOS:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Configure RabbitMQ credentials inside `.env`.

Example:

```env
RABBITMQ_HOST=rabbitmq
RABBITMQ_TEST_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=admin_user
RABBITMQ_PASS=admin_pass

HEARTBEAT=600
BLOCKED_CONNECTION_TIMEOUT=300
CONNECTION_ATTEMPTS=3
RETRY_DELAY=5
SOCKET_TIMEOUT=10

RABBITMQ_DEFAULT_USER=admin_user
RABBITMQ_DEFAULT_PASS=admin_pass

NON_DURABLE_TRANSIENT_QUEUE=p07.non_durable.transient
NON_DURABLE_PERSISTENT_QUEUE=p07.non_durable.persistent
DURABLE_TRANSIENT_QUEUE=p07.durable.transient
DURABLE_PERSISTENT_QUEUE=p07.durable.persistent

HANDLER_NAME=Persistence-Handler

RABBITMQ_CONTAINER_NAME=P07_RabbitMQ
FASTAPI_CONTAINER_NAME=P07_FastAPI
WORKER_CONTAINER_NAME=P07_Persistence_Worker
```

`RABBITMQ_HOST=rabbitmq` is used by application containers inside the Docker Compose network.

`RABBITMQ_TEST_HOST=localhost` is used by Pytest running on the host machine.

---

## 3. Start All Services

```bash
docker compose up --build -d
```

Check service status:

```bash
docker compose ps
```

The following services should be running:

```text
rabbitmq
fastapi
worker
```

---

# 🌐 Access Services

| Service | URL |
|----------|-----|
| FastAPI | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| RabbitMQ Management | http://localhost:15672 |

RabbitMQ credentials are configured in `.env`.

---

# 📬 Send a Persistence Message

## Using Swagger

Open:

```text
http://localhost:8000/docs
```

Use:

```text
POST /api/v1/send-message
```

Click **Try it out**, provide a request body, and click **Execute**.

---

## Example Request

```json
{
  "content": "Durable persistent message",
  "queue_durable": true,
  "message_persistent": true,
  "publisher_confirm": true
}
```

---

## Example Response

```json
{
  "message_id": "0a874f17-079c-4df4-8599-c83f5638655d",
  "content": "Durable persistent message",
  "queue_name": "p07.durable.persistent",
  "queue_durable": true,
  "message_persistent": true,
  "publisher_confirm": true,
  "broker_confirmed": true,
  "status": "published",
  "created_at": "2026-09-08T12:30:00.000000+00:00"
}
```

The API returns:

```text
202 Accepted
```

This means the Publish operation completed successfully.

It does not mean that the Worker has already processed the Message.

Consumer processing is confirmed separately by a Consumer ACK.

---

# 📋 Message Schema

The API accepts four fields.

## content

The message content used by the experiment.

```text
Minimum length: 1 character
Maximum length: 300 characters
```

Example:

```json
{
  "content": "Message persistence experiment"
}
```

---

## queue_durable

Controls whether Queue metadata survives a RabbitMQ restart.

```text
true  → Durable Queue
false → Non-durable Queue
```

---

## message_persistent

Controls the AMQP Message delivery mode.

```text
true  → delivery_mode=2
false → delivery_mode=1
```

---

## publisher_confirm

Controls whether the Producer waits for RabbitMQ to confirm the Publish operation.

```text
true  → broker_confirmed=true on success
false → broker_confirmed=null
```

---

# 🧪 Persistence Scenario Matrix

| Scenario | Queue Durable | Message Persistent | Queue After Restart | Message After Restart |
|----------|:-------------:|:------------------:|:-------------------:|:---------------------:|
| 01 | No | No | Removed | Removed |
| 02 | No | Yes | Removed | Removed |
| 03 | Yes | No | Survives | Removed |
| 04 | Yes | Yes | Survives | Survives |

The key recovery rule is:

```text
Message survives restart
        only when
Queue Durable = True
        and
Message Persistent = True
```

---

# 1️⃣ Scenario 01 — Non-durable Queue + Transient Message

Request:

```json
{
  "content": "Non-durable transient message",
  "queue_durable": false,
  "message_persistent": false,
  "publisher_confirm": true
}
```

Target Queue:

```text
p07.non_durable.transient
```

Before restart:

```text
Queue exists: True
Message count: 1
```

After restart:

```text
Queue exists: False
Message count: 0
```

The Queue is removed because it is non-durable.

The transient Message stored in that Queue is also removed.

---

# 2️⃣ Scenario 02 — Non-durable Queue + Persistent Message

Request:

```json
{
  "content": "Non-durable persistent message",
  "queue_durable": false,
  "message_persistent": true,
  "publisher_confirm": true
}
```

Target Queue:

```text
p07.non_durable.persistent
```

Before restart:

```text
Queue exists: True
Message count: 1
```

After restart:

```text
Queue exists: False
Message count: 0
```

The Message is marked persistent, but the Queue itself is non-durable.

RabbitMQ removes the Queue during restart, so the persistent Message cannot be recovered.

Message persistence alone is not sufficient.

---

# 3️⃣ Scenario 03 — Durable Queue + Transient Message

Request:

```json
{
  "content": "Durable transient message",
  "queue_durable": true,
  "message_persistent": false,
  "publisher_confirm": true
}
```

Target Queue:

```text
p07.durable.transient
```

Before restart:

```text
Queue exists: True
Message count: 1
```

After restart:

```text
Queue exists: True
Message count: 0
```

The Queue is recovered because it is durable.

The Message is discarded during Broker recovery because it was published as transient.

Queue durability alone is not sufficient for Message recovery.

---

# 4️⃣ Scenario 04 — Durable Queue + Persistent Message

Request:

```json
{
  "content": "Durable persistent message",
  "queue_durable": true,
  "message_persistent": true,
  "publisher_confirm": true
}
```

Target Queue:

```text
p07.durable.persistent
```

Before restart:

```text
Queue exists: True
Message count: 1
```

After restart:

```text
Queue exists: True
Message count: 1
```

The Queue metadata is recovered because the Queue is durable.

The Message is recovered because it was published as persistent.

This is the only experiment combination in which both the Queue and Message survive the restart.

---

# 🔄 Message Flow

### Step 1 — API Receives the Request

```text
POST /api/v1/send-message
```

↓

### Step 2 — Persistence Service Creates the Message

The Service generates:

```text
message_id
content
queue_name
queue_durable
message_persistent
publisher_confirm
created_at
```

A unique Message ID is generated using UUID.

↓

### Step 3 — Service Selects the Experiment Queue

The Queue is selected using Queue durability and Message persistence:

```python
(False, False) → non_durable_transient_queue
(False, True)  → non_durable_persistent_queue
(True, False)  → durable_transient_queue
(True, True)   → durable_persistent_queue
```

↓

### Step 4 — Producer Creates a Dedicated Channel

The RabbitMQ Connection is reused, but every Publish operation receives a dedicated Channel.

Publisher Confirm mode belongs to a Channel.

Once Confirm mode is enabled on a Channel, it cannot be disabled for later Publish operations on that Channel.

↓

### Step 5 — Producer Declares the Queue

```python
channel.queue_declare(
    queue=queue_name,
    durable=queue_durable,
)
```

↓

### Step 6 — Producer Configures Message Persistence

```python
delivery_mode=2 if message_persistent else 1
```

↓

### Step 7 — Producer Publishes the Message

The Message is published through the RabbitMQ Default Exchange:

```python
channel.basic_publish(
    exchange="",
    routing_key=queue_name,
    body=data,
    properties=pika.BasicProperties(
        delivery_mode=(
            2 if message_persistent else 1
        ),
    ),
    mandatory=publisher_confirm,
)
```

↓

### Step 8 — Consumer Receives the Message

The Persistence Consumer listens to all four experiment Queues.

↓

### Step 9 — Handler Processes Business Data

The Consumer deserializes the JSON payload and passes it to:

```text
PersistenceHandler
```

↓

### Step 10 — Consumer Sends ACK or NACK

```text
Successful processing       → ACK
Invalid Message             → NACK, requeue=False
Unexpected processing error → NACK, requeue=True
```

---

# 💾 Queue Durability

Queue durability applies to Queue metadata.

```python
channel.queue_declare(
    queue=queue_name,
    durable=True,
)
```

A durable Queue can be recovered after RabbitMQ restarts.

However, a durable Queue does not automatically make its Messages persistent.

```text
Durable Queue + Transient Message
              ↓
Queue survives, Message does not
```

A non-durable Queue is removed during Broker recovery:

```python
channel.queue_declare(
    queue=queue_name,
    durable=False,
)
```

---

# 📨 Message Persistence

Message persistence is controlled using AMQP `delivery_mode`.

## Transient Message

```python
pika.BasicProperties(
    delivery_mode=1,
)
```

A transient Message is not recovered after RabbitMQ restarts.

## Persistent Message

```python
pika.BasicProperties(
    delivery_mode=2,
)
```

A persistent Message can be recovered only when it is stored in a durable Queue.

```text
Persistent Message + Non-durable Queue
                   ↓
          Message is still lost
```

---

# ✅ Publisher Confirms

Publisher Confirms allow the Producer to determine whether RabbitMQ accepted responsibility for a Publish.

```python
channel.confirm_delivery()
```

When Confirm mode is enabled and the Publish succeeds:

```json
{
  "publisher_confirm": true,
  "broker_confirmed": true
}
```

When Confirm mode is disabled:

```json
{
  "publisher_confirm": false,
  "broker_confirmed": null
}
```

Publisher Confirms do not replace Message persistence.

```text
delivery_mode=2
    ↓
Controls Message recovery


confirm_delivery()
    ↓
Confirms Broker acceptance
```

A Publisher Confirm also does not prove that a Consumer processed the Message.

---

# 📨 Mandatory Publishing

When Publisher Confirms are enabled, the project also enables mandatory publishing:

```python
mandatory=publisher_confirm
```

If a mandatory Message cannot be routed to a Queue, Pika can raise:

```text
UnroutableError
```

If RabbitMQ negatively acknowledges the Publish, Pika can raise:

```text
NackError
```

These exceptions are converted to:

```text
ProducerPublishError
```

The Service converts that exception to:

```text
PersistencePublishError
```

The API then returns:

```text
503 Service Unavailable
```

---

# 🏛️ Project Design

The project separates HTTP handling, RabbitMQ infrastructure, and Message business logic.

```text
Route
  │
  ▼
PersistenceService
  │
  ▼
Producer
  │
  ▼
RabbitMQ
  │
  ▼
PersistenceConsumer
  │
  ▼
PersistenceHandler
```

Each layer has a specific responsibility.

---

## Route

The API Route handles HTTP communication.

Responsibilities:

- Receive the request
- Validate the request Schema
- Call `PersistenceService`
- Return `202 Accepted`
- Convert publishing failures to `503 Service Unavailable`

The Route does not use Pika directly.

---

## Persistence Service

`PersistenceService` coordinates the Publish use case.

Responsibilities:

- Generate a UUID Message ID
- Generate the creation timestamp
- Select one of the four experiment Queues
- Build the Message payload
- Call the Producer
- Convert Producer failures to `PersistencePublishError`

The generated Message contains:

```python
{
    "message_id": "...",
    "content": "...",
    "queue_name": "...",
    "queue_durable": True,
    "message_persistent": True,
    "publisher_confirm": True,
    "created_at": "...",
}
```

---

## Producer

The Producer owns RabbitMQ publishing behavior.

Responsibilities:

- Validate the Queue name
- Serialize the Message to JSON
- Reuse the RabbitMQ Connection
- Create a dedicated Channel for each Publish
- Declare the selected Queue
- Configure `delivery_mode`
- Optionally enable Publisher Confirms
- Enable mandatory routing
- Handle NACK and unroutable errors
- Close the dedicated Channel

The Producer does not contain Consumer or business logic.

---

## Persistence Consumer

`PersistenceConsumer` owns RabbitMQ consumption behavior.

Responsibilities:

- Declare all four experiment Queues
- Register a callback on each Queue
- Deserialize incoming JSON
- Delegate processing to the Handler
- ACK successfully processed Messages
- NACK invalid Messages
- Requeue unexpected processing failures
- Close the RabbitMQ Connection when stopped

The Consumer does not implement Message business logic.

---

## Persistence Handler

`PersistenceHandler` owns business validation and processing.

Responsibilities:

- Validate required String fields
- Validate required Boolean fields
- Accept valid `False` Boolean values
- Process the Message
- Return a structured result
- Identify itself using `HANDLER_NAME`

The Handler is created by the Worker and injected into the Consumer.

---

# 👷 Worker Architecture

The project has one Worker bootstrap module:

```text
app/worker.py
```

The Docker Worker executes:

```bash
python -m app.worker
```

The Worker performs these steps:

```text
Read HANDLER_NAME
        ↓
Create PersistenceHandler
        ↓
Create PersistenceConsumer
        ↓
Start consuming four Queues
```

Unlike Day 6, this project does not require multiple competing Workers.

Day 6 demonstrates task distribution between several Workers.

Day 7 compares Queue and Message persistence settings, so one Worker listening to all four experiment Queues is sufficient.

---

# 🛡️ Consumer ACK and NACK

Automatic acknowledgements are disabled:

```python
channel.basic_consume(
    queue=queue_name,
    on_message_callback=self._callback,
    auto_ack=False,
)
```

## Successful Processing

```python
channel.basic_ack(
    delivery_tag=method.delivery_tag,
)
```

After ACK, RabbitMQ removes the Message from the Queue.

## Invalid Message

```python
channel.basic_nack(
    delivery_tag=method.delivery_tag,
    requeue=False,
)
```

Invalid Messages are not returned to the Queue.

This prevents malformed data from being delivered repeatedly.

## Unexpected Processing Failure

```python
channel.basic_nack(
    delivery_tag=method.delivery_tag,
    requeue=True,
)
```

The Message is returned to the Queue because the failure may be temporary.

Publisher Confirms and Consumer ACKs happen at different stages:

```text
Producer → RabbitMQ
Publisher Confirm


RabbitMQ → Consumer → RabbitMQ
Consumer ACK
```

---

# ⚠️ RabbitMQ 4.x Compatibility

Recent RabbitMQ versions deprecate non-durable, non-exclusive Classic Queues and may reject them by default.

Day 7 intentionally uses this combination for an educational recovery experiment.

The project contains:

```text
rabbitmq.conf
```

with:

```ini
deprecated_features.permit.transient_nonexcl_queues = true
```

Docker Compose mounts it into RabbitMQ:

```yaml
volumes:
  - rabbitmq_data:/var/lib/rabbitmq/
  - ./rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf:ro
```

This compatibility option is appropriate for this learning experiment.

New production systems should generally prefer:

- Durable Queues
- Exclusive temporary Queues
- Queue TTL for temporary cleanup

After changing `rabbitmq.conf`, recreate the RabbitMQ Container:

```powershell
docker compose down
docker compose up --build -d
```

Do not use `down -v` during a persistence experiment because it removes the RabbitMQ Volume.

---

# 🐳 Docker Services

## rabbitmq

Provides RabbitMQ Broker and Management UI.

Ports:

```text
5672  → AMQP
15672 → Management UI
```

The health check uses:

```text
rabbitmq-diagnostics ping
```

The named Volume stores RabbitMQ data:

```text
rabbitmq_data
```

---

## fastapi

Receives persistence experiment requests and publishes Messages to RabbitMQ.

The FastAPI development server runs with:

```bash
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload
```

---

## worker

Consumes Messages from all four persistence experiment Queues.

The Worker runs:

```bash
python -m app.worker
```

Its Handler identity is provided through:

```text
HANDLER_NAME=Persistence-Handler
```

---

# 📊 Example Logs

## Producer

```text
INFO | Publisher confirmation enabled: queue=p07.durable.persistent
INFO | Message published successfully: message_id=<message-id> on queue=p07.durable.persistent | queue_durable=True - message_persistent=True - publisher_confirm=True - broker_confirmed=True
```

---

## Consumer

```text
INFO | [PersistenceConsumer] Message received: message_id=<message-id> Queue: <p07.durable.persistent>
INFO | [PersistenceConsumer] Message processing started for message=<message-id>
INFO | [Persistence-Handler] Processing message:<message-id>
INFO | [Persistence-Handler] Finished processing message:<message-id>
INFO | [PersistenceConsumer] Message with message_id=<message-id> acknowledged successfully
```

---

# 🧪 Automated Persistence Tests

The persistence Scenario tests are real Integration Tests.

They do not merely compare hard-coded expected values.

Every Scenario:

1. Publishes a real Message to RabbitMQ.
2. Verifies the Queue exists.
3. Verifies the Message count is one.
4. Restarts the RabbitMQ Container.
5. Waits for RabbitMQ to become ready.
6. Inspects the actual Queue state again.
7. Compares the real result with the expected result.
8. Deletes any Queue that remains.
9. Restores the initial Docker service state.

```text
Prepare RabbitMQ
       ↓
Stop Worker
       ↓
Publish Test Message
       ↓
Inspect Queue Before Restart
       ↓
Restart RabbitMQ Container
       ↓
Wait Until Broker Is Ready
       ↓
Inspect Queue After Restart
       ↓
Assert Actual Recovery State
       ↓
Delete Test Queue
       ↓
Restore Docker Services
```

---

# 📁 Test Directory Structure

```text
tests/
├── __init__.py
├── conftest.py
│
├── helpers/
│   ├── __init__.py
│   ├── docker_compose.py
│   ├── settings.py
│   └── rabbitmq/
│       ├── __init__.py
│       ├── client.py
│       ├── publisher.py
│       ├── queue_repository.py
│       └── scenario.py
│
└── scenarios/
    ├── __init__.py
    ├── test_publisher_confirm.py
    ├── test_scenario_01_non_durable_transient_message.py
    ├── test_scenario_02_non_durable_persistent_message.py
    ├── test_scenario_03_durable_transient_message.py
    └── test_scenario_04_durable_persistent_message.py
```

Each file has a single responsibility.

---

# ⚙️ Test Architecture

```text
Scenario Test
      │
      ▼
RabbitMQScenarioController
      │
      ├── RabbitMQTestPublisher
      │
      ├── RabbitMQQueueRepository
      │
      ├── RabbitMQTestClient
      │
      └── Docker Compose Helper
      │
      ▼
Real RabbitMQ Container
```

The Scenario files do not directly manage Connections, Channels, or Docker commands.

---

## `tests/conftest.py`

Defines the shared Pytest Fixtures.

Responsibilities:

- Detect services running before the tests
- Stop the Worker during persistence testing
- Start RabbitMQ when required
- Wait until RabbitMQ accepts connections
- Provide the `rabbitmq_scenario` Fixture
- Clean up Scenario Queues
- Restore the original service state

The main Fixture is:

```python
@pytest.fixture
def rabbitmq_scenario(...):
    ...
```

Scenario tests receive it automatically:

```python
def test_scenario(
    rabbitmq_scenario: RabbitMQScenarioController,
) -> None:
    ...
```

---

## `tests/helpers/settings.py`

Loads test configuration.

Responsibilities:

- Resolve the P07 project root
- Read values from `.env`
- Configure the RabbitMQ test Host
- Configure RabbitMQ credentials
- Define Docker service names
- Define readiness timeout
- Define retry delay

Application containers use:

```text
RABBITMQ_HOST=rabbitmq
```

Host-side Pytest uses:

```text
RABBITMQ_TEST_HOST=localhost
```

---

## `tests/helpers/docker_compose.py`

Provides a wrapper around Docker Compose.

Responsibilities:

- Execute Docker Compose commands
- Capture stdout and stderr
- Raise a readable error when commands fail
- Detect running services
- Start a service
- Stop a service
- Restart a service

All commands run from the P07 project directory.

---

## `tests/helpers/rabbitmq/client.py`

Owns RabbitMQ test Connections and Channels.

Responsibilities:

- Create a Blocking Connection
- Open a Channel safely
- Close the Channel
- Close the Connection
- Wait for RabbitMQ after restart
- Convert readiness failures to a test-specific error

The Channel is provided through a context manager:

```python
with client.open_channel() as channel:
    ...
```

This guarantees cleanup after the operation.

---

## `tests/helpers/rabbitmq/publisher.py`

Publishes real test Messages.

Responsibilities:

- Declare the Scenario Queue
- Configure Queue durability
- Enable Publisher Confirms
- Select `delivery_mode`
- Publish through the Default Exchange
- Enable mandatory routing
- Handle NACK and unroutable errors

Message delivery mode:

```python
delivery_mode=(
    2 if message_persistent else 1
)
```

---

## `tests/helpers/rabbitmq/queue_repository.py`

Inspects and deletes test Queues.

Queue inspection uses passive declaration:

```python
channel.queue_declare(
    queue=queue_name,
    passive=True,
)
```

Passive Queue declaration checks a Queue without creating it.

When the Queue exists, the Repository returns:

```python
QueueState(
    exists=True,
    message_count=1,
)
```

When RabbitMQ returns `404`, it returns:

```python
QueueState(
    exists=False,
    message_count=0,
)
```

It also deletes test Queues that survive the experiment.

---

## `tests/helpers/rabbitmq/scenario.py`

Coordinates the complete Scenario.

Responsibilities:

- Publish the test Message
- Track generated Queue names
- Inspect Queue state
- Restart RabbitMQ
- Wait until RabbitMQ becomes ready
- Clean up remaining Queues

Scenario files only communicate with this Controller.

---

# 🛑 Why the Worker Is Stopped During Tests

If the Worker remains active, it receives and ACKs the test Message immediately.

The Queue would then contain zero ready Messages before RabbitMQ restarts.

```text
Message published
       ↓
Worker receives Message
       ↓
Worker sends ACK
       ↓
Message removed
       ↓
Nothing remains to test
```

The session Fixture therefore stops the Worker before persistence tests.

If the Worker was running before the tests, it is restarted after all tests finish.

If the Worker was already stopped, the Fixture leaves it stopped.

---

# 🆔 Isolated Test Queue Names

Each Scenario generates a unique Queue name using UUID.

Example:

```text
p07.test.durable.persistent.3fda9c11d75c4dc4a68297649524fa92
```

This prevents collisions with:

- Application Queues
- Existing Messages
- Other Scenario tests
- Previous successful test runs

---

# 1️⃣ Automated Test Scenario 01

File:

```text
tests/scenarios/test_scenario_01_non_durable_transient_message.py
```

Configuration:

```text
queue_durable=False
message_persistent=False
```

Assertions:

```text
Before restart:
Queue exists = True
Message count = 1

After restart:
Queue exists = False
Message count = 0
```

Expected result:

```text
Queue removed
Message removed
```

---

# 2️⃣ Automated Test Scenario 02

File:

```text
tests/scenarios/test_scenario_02_non_durable_persistent_message.py
```

Configuration:

```text
queue_durable=False
message_persistent=True
```

Assertions:

```text
Before restart:
Queue exists = True
Message count = 1

After restart:
Queue exists = False
Message count = 0
```

Expected result:

```text
Queue removed
Message removed
```

This Scenario proves that Message persistence alone is insufficient.

---

# 3️⃣ Automated Test Scenario 03

File:

```text
tests/scenarios/test_scenario_03_durable_transient_message.py
```

Configuration:

```text
queue_durable=True
message_persistent=False
```

Assertions:

```text
Before restart:
Queue exists = True
Message count = 1

After restart:
Queue exists = True
Message count = 0
```

Expected result:

```text
Queue survives
Message removed
```

This Scenario proves that Queue durability alone is insufficient for Message recovery.

---

# 4️⃣ Automated Test Scenario 04

File:

```text
tests/scenarios/test_scenario_04_durable_persistent_message.py
```

Configuration:

```text
queue_durable=True
message_persistent=True
```

Assertions:

```text
Before restart:
Queue exists = True
Message count = 1

After restart:
Queue exists = True
Message count = 1
```

Expected result:

```text
Queue survives
Message survives
```

This Scenario proves that both persistence settings are required.

---

# ✅ Publisher Confirm Test

File:

```text
tests/scenarios/test_publisher_confirm.py
```

Publisher Confirm answers this question:

```text
Did RabbitMQ accept responsibility for the Publish?
```

It does not answer:

```text
Did the Message survive a restart?
Did a Consumer process the Message?
```

Publisher Confirm behavior should therefore be tested separately from Broker recovery.

---

# ▶️ Running the Tests

## 1. Create a Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux or macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

The test dependencies include:

```text
pytest
pika
```

---

## 3. Verify Docker

```powershell
docker --version
docker compose version
```

Docker Desktop must be running.

The tests execute Docker Compose commands from the host machine.

---

## 4. Run All Scenario Tests

Use `-s` to display Scenario logs and RabbitMQ restart progress:

```powershell
pytest tests/scenarios -v -s
```

Do not run these tests in parallel.

Each Scenario restarts the same RabbitMQ service.

---

## 5. Run Scenario 01

```powershell
pytest `
    tests/scenarios/test_scenario_01_non_durable_transient_message.py `
    -v `
    -s
```

---

## 6. Run Scenario 02

```powershell
pytest `
    tests/scenarios/test_scenario_02_non_durable_persistent_message.py `
    -v `
    -s
```

---

## 7. Run Scenario 03

```powershell
pytest `
    tests/scenarios/test_scenario_03_durable_transient_message.py `
    -v `
    -s
```

---

## 8. Run Scenario 04

```powershell
pytest `
    tests/scenarios/test_scenario_04_durable_persistent_message.py `
    -v `
    -s
```

---

# 📊 Expected Test Output

```text
Scenario 01
Before restart:
Queue exists: True
Message count: 1

After restart:
Queue exists: False
Message count: 0

PASSED
```

```text
Scenario 02
Before restart:
Queue exists: True
Message count: 1

After restart:
Queue exists: False
Message count: 0

PASSED
```

```text
Scenario 03
Before restart:
Queue exists: True
Message count: 1

After restart:
Queue exists: True
Message count: 0

PASSED
```

```text
Scenario 04
Before restart:
Queue exists: True
Message count: 1

After restart:
Queue exists: True
Message count: 1

PASSED
```

Final comparison:

| Scenario | Before Restart | After Restart |
|----------|----------------|---------------|
| 01 | Queue=True, Messages=1 | Queue=False, Messages=0 |
| 02 | Queue=True, Messages=1 | Queue=False, Messages=0 |
| 03 | Queue=True, Messages=1 | Queue=True, Messages=0 |
| 04 | Queue=True, Messages=1 | Queue=True, Messages=1 |

---

# 🧹 Test Cleanup

Each Scenario Controller tracks the Queue names it creates.

After every test, including when an Assertion fails, the Fixture calls:

```python
controller.cleanup()
```

The Queue Repository deletes any Queue that still exists.

The session Fixture restores Docker services to their initial state.

For example:

```text
Worker was running before tests
             ↓
Worker stopped during tests
             ↓
Tests completed
             ↓
Worker started again
```

---

# 🧪 Manual Recovery Test

You can also observe the same behavior manually using Swagger and RabbitMQ Management.

## 1. Stop the Worker

```powershell
docker compose stop worker
```

## 2. Open Swagger

```text
http://localhost:8000/docs
```

## 3. Publish All Four Scenarios

Use:

```text
POST /api/v1/send-message
```

Publish one Message for each durability combination.

## 4. Inspect RabbitMQ

Open:

```text
http://localhost:15672
```

Before restart, all four Queues should contain one ready Message.

## 5. Restart RabbitMQ

```powershell
docker compose restart rabbitmq
```

## 6. Inspect the Recovery Result

Before starting the Worker again, compare the four Queues.

## 7. Restore the Worker

```powershell
docker compose start worker
```

---

# 🧯 Troubleshooting

## Transient Queue Is Rejected

Possible error:

```text
Feature `transient_nonexcl_queues` is deprecated
and is not permitted anymore
```

Verify that `rabbitmq.conf` contains:

```ini
deprecated_features.permit.transient_nonexcl_queues = true
```

Then recreate the RabbitMQ Container:

```powershell
docker compose down
docker compose up --build -d
```

Do not use `down -v` during the experiment.

---

## Tests Cannot Connect to RabbitMQ

Application containers use:

```text
RABBITMQ_HOST=rabbitmq
```

Host-side Pytest uses:

```text
RABBITMQ_TEST_HOST=localhost
```

Also verify that Docker publishes port `5672`.

---

## RabbitMQ Does Not Become Ready

Check Broker logs:

```powershell
docker compose logs rabbitmq
```

Check service health:

```powershell
docker compose ps
```

The test Client waits up to the configured timeout:

```text
RABBITMQ_START_TIMEOUT_SECONDS=60
```

---

## Messages Disappear Before Restart

The Worker is probably consuming and acknowledging them.

Stop it before a manual test:

```powershell
docker compose stop worker
```

The automated Fixtures handle this automatically.

---

## Durable Queue Exists but Message Is Missing

Verify that the Message was published with:

```python
delivery_mode=2
```

A durable Queue does not automatically persist transient Messages.

---

## Queue Declaration Fails

RabbitMQ requires all declarations of the same Queue to use identical properties.

For example, an existing Queue declared with:

```python
durable=True
```

cannot later be declared with:

```python
durable=False
```

The Integration Tests avoid this conflict by generating unique Queue names.

---

## Reset the Experiment Completely

Stop the project without deleting RabbitMQ data:

```powershell
docker compose down
```

Delete RabbitMQ data and start with a clean Volume:

```powershell
docker compose down -v
```

Use `down -v` only when you intentionally want to remove all persisted Broker data.

---

# 📚 Key Concepts

| Concept | Purpose |
|---------|---------|
| Durable Queue | Recovers Queue metadata after restart |
| Non-durable Queue | Removed during Broker recovery |
| Persistent Message | Published with `delivery_mode=2` |
| Transient Message | Published with `delivery_mode=1` |
| Publisher Confirm | Confirms Broker acceptance |
| Mandatory Publish | Detects unroutable Messages |
| Consumer ACK | Confirms successful processing |
| Consumer NACK | Rejects or requeues failed Messages |
| Passive Declaration | Inspects a Queue without creating it |
| Named Volume | Preserves RabbitMQ durable data |
| Fixture | Prepares and restores test state |
| Integration Test | Verifies behavior against a real Broker |

---

# 🔜 Next Step

## Day 8 — Dead Letter Exchanges and Retry Handling

The next reliability step is to route rejected or expired Messages to a Dead Letter Exchange and introduce controlled retry behavior.

---

# 📝 Author

**Mehrad Abbasi**

GitHub:

https://github.com/Mehrad82a

---

# 📄 License

This project is licensed under the MIT License. See the [LICENSE](../../LICENSE) file for details.