# Day 6 — Work Queues (Task Distribution Between Workers)

> Distribute background tasks between multiple workers using a shared RabbitMQ queue, FastAPI, Pika, and Docker.

---

# 🎯 Goal

In this project we implement the RabbitMQ **Work Queue** pattern.

Instead of routing messages to different queues based on an exchange or routing rule, all workers consume tasks from the **same shared queue**.

RabbitMQ distributes tasks between the available workers so that each task is processed by only one worker.

In this project, three workers consume tasks from the same queue:

```text
Task 1
   ↓
Worker1


Task 2
   ↓
Worker2


Task 3
   ↓
Worker3
```

When a worker is busy processing a task, RabbitMQ can dispatch the next task to another available worker.

---

# 🧠 What You Will Learn

- Understand the Work Queue pattern
- Distribute tasks between multiple workers
- Use one shared queue for multiple consumers
- Configure Fair Dispatch with `prefetch_count=1`
- Use manual acknowledgements
- Handle failed messages with NACK
- Separate message consumption from business logic
- Build reusable consumer infrastructure
- Apply Handler-based architecture
- Use Dependency Injection
- Work with durable queues
- Publish persistent messages
- Run multiple identical workers with Docker Compose
- Configure worker identity using environment variables
- Simulate long-running background tasks
- Understand how RabbitMQ distributes tasks between competing consumers

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
                  RabbitMQ Work Queue
                      "task_queue"
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
          Worker1         Worker2         Worker3
             |              |              |
             +--------------+--------------+
                            |
                            v
                       TaskHandler
                            |
                            v
                     Business Logic
```

All three workers consume from the same RabbitMQ queue.

RabbitMQ delivers each message to only one consumer.

---

# 📁 Project Structure

```text
p06_work_queues/
│
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── schemas.py
│   │
│   ├── consumers/
│   │   ├── __init__.py
│   │   ├── base_consumer.py
│   │   └── work_consumer.py
│   │
│   ├── producer/
│   │   ├── __init__.py
│   │   └── producer.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── task_service.py
│   │   └── handlers/
│   │       ├── __init__.py
│   │       ├── base_handler.py
│   │       └── task_handler.py
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
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

Automated tests will be implemented later.

---

# 🚀 Quick Start

## 1. Clone the repository

```bash
git clone https://github.com/Mohamad82a/RabbitMQ-Senior-Developer-Roadmap.git

cd part1_rabbitmq_fundamentals/p06_work_queues
```

---

## 2. Create environment file

```bash
cp .env.example .env
```

Configure your RabbitMQ credentials inside `.env`.

Example:

```env
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=your_rabbitmq_username
RABBITMQ_PASS=your_rabbitmq_password

RABBITMQ_DEFAULT_USER=your_rabbitmq_username
RABBITMQ_DEFAULT_PASS=your_rabbitmq_password

WORK_QUEUE_NAME=task_queue
```

---

## 3. Start all services

```bash
docker compose up --build -d
```

---

# 🌐 Access Services

| Service | URL |
|----------|-----|
| FastAPI | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| RabbitMQ Management | http://localhost:15672 |

RabbitMQ credentials are configured in the `.env` file.

---

# 📬 Send a Task

## Using Swagger

Open:

```text
http://localhost:8000/docs
```

Use:

```text
POST /api/v1/send-task
```

---

## Example Request

```json
{
  "task_name": "generate-monthly-report",
  "duration_seconds": 5
}
```

The API creates a task and publishes it to:

```text
task_queue
```

One of the available workers will receive the task.

---

## Example Response

```json
{
  "task_id": "9084b75d-cae2-4a12-9f4e-3ca798b79fe5",
  "task_name": "generate-monthly-report",
  "duration_seconds": 5,
  "status": "queued",
  "created_at": "2026-08-28T18:45:00.000000+00:00"
}
```

The API returns:

```text
202 Accepted
```

after the task has been published to RabbitMQ.

---

# 📋 Task Schema

The API accepts two fields:

```text
task_name
duration_seconds
```

---

## task_name

A descriptive name for the task.

Requirements:

```text
Minimum length: 3 characters
Maximum length: 100 characters
```

Example:

```json
{
  "task_name": "generate-monthly-report"
}
```

---

## duration_seconds

Defines how long the simulated task processing takes.

Requirements:

```text
Minimum: 1 second
Maximum: 30 seconds
```

Example:

```json
{
  "duration_seconds": 5
}
```

The duration is used by `TaskHandler` to simulate background processing.

---

# 🔄 Message Flow

### Step 1 — API receives the request

```text
POST /api/v1/send-task
```

↓

### Step 2 — Task Service creates the task

The service validates the input and generates:

```text
task_id
task_name
duration_seconds
status
created_at
```

A unique task ID is generated using UUID.

↓

### Step 3 — Producer serializes the task

The task is converted to JSON and encoded using UTF-8.

↓

### Step 4 — Producer declares the Work Queue

The producer declares:

```text
task_queue
```

as a durable queue.

↓

### Step 5 — Producer publishes the task

The message is published using RabbitMQ's default exchange:

```text
exchange = ""
```

with:

```text
routing_key = task_queue
```

↓

### Step 6 — RabbitMQ delivers the task

All workers consume from the same queue.

RabbitMQ delivers the task to one available worker.

↓

### Step 7 — WorkConsumer receives the message

The consumer deserializes the JSON message.

↓

### Step 8 — Consumer delegates processing

The consumer passes the task to:

```text
TaskHandler
```

↓

### Step 9 — Handler processes the task

The Handler executes the business logic.

In this project, processing is simulated using:

```python
time.sleep(duration_seconds)
```

↓

### Step 10 — Consumer acknowledges the message

After successful processing:

```text
ACK
```

is sent to RabbitMQ.

The task is then removed from the queue.

---

# 📥 Work Queue

The Work Queue is shared between all workers.

The configured queue name is:

```text
task_queue
```

The queue name is loaded from:

```env
WORK_QUEUE_NAME=task_queue
```

The Producer and Consumer both declare exactly the same queue.

```python
channel.queue_declare(
    queue=self._queue_name,
    durable=True,
)
```

This is important because RabbitMQ requires queue declaration properties to remain consistent.

---

# 📤 Publishing Tasks

The producer publishes tasks using RabbitMQ's **Default Exchange**.

```python
channel.basic_publish(
    exchange="",
    routing_key=self._queue_name,
    body=data,
    properties=pika.BasicProperties(
        content_type="application/json",
        content_encoding="utf-8",
        delivery_mode=2,
        type="work_task",
        message_id=self._get_task_id(task),
    ),
)
```

The default exchange automatically routes the message to the queue whose name matches the routing key.

In this project:

```text
routing_key = task_queue
```

therefore the message is delivered to:

```text
task_queue
```

---

# ⚖️ Competing Consumers

The three workers are **competing consumers**.

```text
                  task_queue
                      |
        +-------------+-------------+
        |             |             |
        v             v             v
     Worker1        Worker2        Worker3
```

All workers listen to the same queue.

However, RabbitMQ does not send the same message to all workers.

Each task is delivered to only one consumer.

For example:

```text
Task 1 → Worker1
Task 2 → Worker2
Task 3 → Worker3
Task 4 → Available Worker
```

This is different from the Fanout pattern.

In Fanout:

```text
One Message
   ↓
Multiple Queues
   ↓
Multiple Consumers receive copies
```

In Work Queues:

```text
One Message
   ↓
One Shared Queue
   ↓
One Consumer processes the message
```

---

# ⚖️ Fair Dispatch

Each worker configures:

```python
channel.basic_qos(
    prefetch_count=1
)
```

This enables the core Fair Dispatch behavior used in this project.

RabbitMQ will not give another unacknowledged task to a worker that is already processing one.

For example:

```text
Worker1 → Processing 10-second task
Worker2 → Available
Worker3 → Available
```

When a new task arrives, RabbitMQ can send it to an available worker instead of immediately assigning another unacknowledged task to Worker1.

This improves task distribution when processing durations are different.

---

# 🏛️ Project Design

The project separates RabbitMQ infrastructure from task business logic.

```text
Route
   │
   ▼
TaskService
   │
   ▼
Producer
   │
   ▼
RabbitMQ
   │
   ▼
WorkConsumer
   │
   ▼
TaskHandler
   │
   ▼
Business Logic
```

Each layer has a specific responsibility.

---

## Route

The API Route handles HTTP communication.

Responsibilities:

- Receive the request
- Use the request schema
- Call `TaskService`
- Return `202 Accepted`
- Convert publishing failures to `503 Service Unavailable`

It does not publish directly to RabbitMQ.

---

## Task Service

`TaskService` orchestrates task creation.

Responsibilities:

- Normalize the task name
- Validate task data
- Generate a unique task ID
- Add task metadata
- Call the Producer
- Convert publishing failures to `TaskPublishError`

The generated task contains:

```python
{
    "task_id": "...",
    "task_name": "...",
    "duration_seconds": 5,
    "status": "queued",
    "created_at": "..."
}
```

---

## Producer

The Producer is responsible for RabbitMQ message publishing.

Responsibilities:

- Connect to RabbitMQ
- Declare the durable queue
- Serialize the task to JSON
- Publish through the Default Exchange
- Configure message properties

The Producer does not contain task business logic.

---

## BaseConsumer

`BaseConsumer` contains common RabbitMQ consumer infrastructure.

Responsibilities:

- Connect to RabbitMQ
- Declare the queue
- Configure QoS
- Register the message callback
- Disable automatic acknowledgements
- Start consuming
- Stop the consumer
- Handle RabbitMQ connection errors

This prevents RabbitMQ infrastructure code from being duplicated.

---

## WorkConsumer

`WorkConsumer` extends `BaseConsumer`.

Responsibilities:

- Deserialize incoming messages
- Delegate processing to a Handler
- ACK successful tasks
- NACK failed tasks
- Reject malformed messages

It does not implement the actual task business logic.

---

## TaskHandler

`TaskHandler` contains task processing logic.

Responsibilities:

- Validate task fields
- Read task metadata
- Simulate task processing
- Return the processing result

The simulated processing is:

```python
time.sleep(duration_seconds)
```

This makes it easy to observe how RabbitMQ distributes tasks between multiple workers.

---

# 🧩 Handler Architecture

Business logic is separated from RabbitMQ consumption.

```text
BaseHandler
    │
    ▼
TaskHandler
```

`BaseHandler` defines the Handler contract:

```python
process(task)
```

`TaskHandler` implements the actual processing behavior.

The WorkConsumer depends on:

```text
BaseHandler
```

instead of being tightly coupled to the concrete Handler implementation.

This supports concepts such as:

- Separation of Concerns
- Dependency Injection
- Dependency Inversion
- Strategy-based processing
- Reusable consumer infrastructure

---

# 👷 Worker Architecture

The project does not create separate Python implementations for each worker.

There is only one worker bootstrap module:

```text
app/worker.py
```

All Docker workers execute:

```bash
python -m app.worker
```

The workers use the same:

```text
WorkConsumer
TaskHandler
RabbitMQ Queue
```

Their identity is provided through an environment variable.

---

## Worker1

```yaml
environment:
  HANDLER_NAME: Worker1-Handler
```

---

## Worker2

```yaml
environment:
  HANDLER_NAME: Worker2-Handler
```

---

## Worker3

```yaml
environment:
  HANDLER_NAME: Worker3-Handler
```

Inside `worker.py`:

```python
handler_name = os.getenv("HANDLER_NAME")
```

Each Docker container has its own environment.

Therefore:

```text
worker1 container
    ↓
HANDLER_NAME=Worker1-Handler


worker2 container
    ↓
HANDLER_NAME=Worker2-Handler


worker3 container
    ↓
HANDLER_NAME=Worker3-Handler
```

The same Python code can therefore identify which worker is processing a task.

---

# 🛡️ Reliability Features

## Durable Queue

Both Producer and Consumer declare:

```python
channel.queue_declare(
    queue=self._queue_name,
    durable=True,
)
```

A durable queue can survive a RabbitMQ broker restart.

---

## Persistent Messages

The Producer publishes messages using:

```python
pika.BasicProperties(
    delivery_mode=2
)
```

This marks the message as persistent.

Persistence is used in this project, but it will be explored in more detail in Day 7.

---

## Manual ACK

Automatic acknowledgements are disabled:

```python
channel.basic_consume(
    queue=self._queue_name,
    on_message_callback=self._callback,
    auto_ack=False,
)
```

After successful processing:

```python
channel.basic_ack(
    delivery_tag=method.delivery_tag
)
```

This tells RabbitMQ that processing completed successfully.

---

## NACK

If task processing raises an exception:

```python
channel.basic_nack(
    delivery_tag=method.delivery_tag,
    requeue=True,
)
```

The message can be returned to the queue for another delivery attempt.

---

## Invalid Messages

If the message cannot be decoded or parsed correctly:

```python
channel.basic_nack(
    delivery_tag=method.delivery_tag,
    requeue=False,
)
```

Invalid messages are not placed back into the queue.

This prevents malformed JSON messages from being continuously redelivered.

---

# ⚙️ Consumer Behavior

Each Consumer uses:

```python
channel.basic_qos(
    prefetch_count=1
)
```

and:

```python
auto_ack=False
```

The processing sequence is:

```text
Receive Message
      |
      v
Deserialize JSON
      |
      v
TaskHandler.process()
      |
      +---- Success ----> ACK
      |
      +---- Failure ----> NACK
```

The Consumer remains responsible for RabbitMQ delivery behavior.

The Handler remains responsible for business logic.

---

# 🐳 Docker Services

## rabbitmq

RabbitMQ broker with the Management UI.

Ports:

```text
5672
15672
```

The RabbitMQ service includes a health check:

```text
rabbitmq-diagnostics ping
```

Other services wait until RabbitMQ is healthy before starting.

---

## fastapi

Receives task requests and publishes tasks to RabbitMQ.

The FastAPI development server runs using:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## worker1

Runs:

```bash
python -m app.worker
```

with:

```text
HANDLER_NAME=Worker1-Handler
```

---

## worker2

Runs:

```bash
python -m app.worker
```

with:

```text
HANDLER_NAME=Worker2-Handler
```

---

## worker3

Runs:

```bash
python -m app.worker
```

with:

```text
HANDLER_NAME=Worker3-Handler
```

All three workers consume from:

```text
task_queue
```

---

# 📊 Example Logs

## Producer

```text
INFO | Task published successfully: task_id=<task-id> queue=task_queue
```

---

## Worker1

```text
INFO | Starting worker Worker1 on queue <task_queue>
INFO | Consumer started and waiting for messages on queue: task_queue
INFO | [WorkConsumer] Task Received: task_id<<task-id>>
INFO | [WorkConsumer] Task Processing started for task:<<task-id>>
INFO | [Worker1-Handler] Processing task:<<task-id>>
INFO | [Worker1-Handler] Finished Processing task:<<task-id>>
INFO | [WorkConsumer] Task with task_id=<task-id> acknowledged successfully
```

---

## Worker2

```text
INFO | Starting worker Worker2 on queue <task_queue>
INFO | Consumer started and waiting for messages on queue: task_queue
INFO | [Worker2-Handler] Processing task:<<task-id>>
INFO | [Worker2-Handler] Finished Processing task:<<task-id>>
```

---

## Worker3

```text
INFO | Starting worker Worker3 on queue <task_queue>
INFO | Consumer started and waiting for messages on queue: task_queue
INFO | [Worker3-Handler] Processing task:<<task-id>>
INFO | [Worker3-Handler] Finished Processing task:<<task-id>>
```

---

# 🧪 Test the Work Queue

To clearly observe task distribution, send several tasks while all three workers are running.

---

## Test 1 — Send Three Tasks

Send:

```json
{
  "task_name": "task-one",
  "duration_seconds": 10
}
```

Then:

```json
{
  "task_name": "task-two",
  "duration_seconds": 5
}
```

Then:

```json
{
  "task_name": "task-three",
  "duration_seconds": 3
}
```

Possible result:

```text
Task One      → Worker1
Task Two      → Worker2
Task Three    → Worker3
```

Each task must be processed by only one worker.

---

## Test 2 — Send More Tasks Than Workers

Send six tasks while three workers are running.

Possible processing:

```text
Task 1 → Worker1
Task 2 → Worker2
Task 3 → Worker3
```

At this point all workers may be busy.

Because:

```python
prefetch_count=1
```

is configured, workers do not receive another unacknowledged message while processing their current task.

When one worker completes its task and sends an ACK, it becomes available for another task.

For example:

```text
Worker3 finishes first
        ↓
ACK
        ↓
Worker3 becomes available
        ↓
RabbitMQ delivers Task 4
```

---

## Test 3 — Different Task Durations

Send tasks with significantly different durations:

```json
{
  "task_name": "slow-task",
  "duration_seconds": 20
}
```

```json
{
  "task_name": "medium-task",
  "duration_seconds": 10
}
```

```json
{
  "task_name": "fast-task",
  "duration_seconds": 2
}
```

Then continue sending tasks.

The fast worker will become available earlier and can receive another task.

This demonstrates why:

```text
prefetch_count=1
```

is useful for Work Queues where task processing times are different.

---

# 🔍 Observe Worker Logs

You can follow all services using:

```bash
docker compose logs -f
```

Or observe individual workers:

```bash
docker compose logs -f worker1
```

```bash
docker compose logs -f worker2
```

```bash
docker compose logs -f worker3
```

This makes it easy to see which worker processes each task.

---

# 🔎 RabbitMQ Management UI

Open:

```text
http://localhost:15672
```

Navigate to:

```text
Queues and Streams
```

and select:

```text
task_queue
```

You can observe information such as:

```text
Ready
Unacked
Total
Consumers
```

When all three workers are running, the queue should show multiple consumers connected to the same queue.

---

# 📚 Key Concepts

| Concept | Purpose |
|----------|---------|
| Work Queue | Distributes tasks between workers |
| Shared Queue | All workers consume from one queue |
| Competing Consumers | Only one consumer receives each message |
| Producer | Publishes tasks |
| Consumer | Receives tasks |
| Handler | Processes business logic |
| Default Exchange | Routes messages directly by queue name |
| Durable Queue | Preserves queue metadata across broker restart |
| Persistent Message | Requests message persistence |
| Manual ACK | Confirms successful processing |
| NACK | Rejects failed messages |
| Requeue | Returns a failed message to the queue |
| Prefetch | Limits unacknowledged messages per consumer |
| Fair Dispatch | Helps distribute work based on worker availability |
| Environment Variable | Provides worker-specific configuration |
| Dependency Injection | Decouples infrastructure components |
| Background Task | Work processed outside the HTTP request flow |

---

# ⚔️ Work Queue vs Previous Patterns

Unlike previous routing patterns, the goal of Work Queues is not to select a destination based on message type.

The goal is to **share processing load**.

```text
Fanout
One Message → Multiple Queues → Multiple Copies


Direct
Routing Key → Matching Queue


Topic
Routing Pattern → Matching Queue


Headers
Message Headers → Matching Queue


Work Queue
One Shared Queue → One Available Worker
```

Work Queues are commonly used for:

- Background jobs
- Report generation
- Image processing
- Email jobs
- File processing
- Data transformation
- CPU or I/O intensive tasks
- Asynchronous business operations

---

# ⚠️ Important Reliability Note

This project uses:

```text
durable=True
```

for the queue and:

```text
delivery_mode=2
```

for messages.

These options improve message durability, but they do not represent the complete RabbitMQ persistence guarantee.

For example, `delivery_mode=2` alone does not guarantee that a publisher knows whether RabbitMQ safely persisted a message before a broker failure.

Those details are intentionally deferred to the next project.

---

# 🔜 Next Step

## Day 7 — Message Persistence

Explore RabbitMQ persistence and message durability in more detail.

Topics will include:

- Durable vs Non-Durable Queues
- Persistent vs Transient Messages
- Broker Restart
- Message Survival
- Publisher Confirms
- Persistence Guarantees
- Limitations of `delivery_mode=2`

Day 6 uses durable queues and persistent messages as part of the Work Queue implementation.

Day 7 will focus specifically on understanding how these mechanisms behave and what guarantees they actually provide.

---

# 📝 Author

**Mohamad Abbasi**

GitHub:

https://github.com/Mohamad82a

---

# 📄 License

This project is licensed under the MIT License. See the [LICENSE](../../LICENSE) file for details.