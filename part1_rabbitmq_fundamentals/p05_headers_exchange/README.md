# Day 5 — Headers Exchange (Header-Based Routing)

> Route messages using message headers with RabbitMQ Headers Exchange, FastAPI, and Docker.

---

# 🎯 Goal

In this project we implement the RabbitMQ **Headers Exchange** pattern.

Instead of routing messages using a routing key, RabbitMQ uses **message headers** to determine which queues should receive a message.

In this project, events are routed based on headers such as:

- `department`
- `priority`

For example:

```text
Finance + Normal Priority
        ↓
Finance Worker


Finance + High Priority
        ↓
High Priority Finance Worker


HR + Normal Priority
        ↓
HR Worker
```

---

# 🧠 What You Will Learn

- Understand the Headers Exchange pattern
- Route messages using message headers
- Use `x-match` with `all`
- Configure multiple header-based queue bindings
- Build reusable consumer infrastructure
- Separate message consumption from business logic
- Apply SOLID principles
- Use Handler-based architecture
- Work with durable exchanges and queues
- Use manual acknowledgements
- Run multiple workers with Docker Compose

---

# 🏗️ Architecture

```text
                         Client
                            |
                            v
                       FastAPI API
                            |
                            v
                     Event Service
                            |
                            v
                   Headers Exchange
                        "events"
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
   Finance Queue     High Priority       HR Queue
                     Finance Queue
          |                 |                 |
          v                 v                 v
 Finance Worker      High Priority       HR Worker
                     Finance Worker
```

RabbitMQ checks the message headers against the binding arguments of each queue.

---

# 📁 Project Structure

```text
p05_headers_exchange/
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
│   │   ├── finance_consumer.py
│   │   ├── high_priority_finance_consumer.py
│   │   └── hr_consumer.py
│   │
│   ├── producer/
│   │   ├── __init__.py
│   │   └── producer.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── event_service.py
│   │   └── handlers/
│   │       ├── __init__.py
│   │       ├── base_handler.py
│   │       ├── finance_handler.py
│   │       ├── high_priority_finance_handler.py
│   │       └── hr_handler.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── rabbitmq.py
│   │
│   ├── __init__.py
│   └── main.py
│
├── tests/ (To be implemented)
│   ├── __init__.py
│   ├── test_producer.py
│   ├── test_finance_consumer.py
│   ├── test_high_priority_finance_consumer.py
│   └── test_hr_consumer.py
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# 🚀 Quick Start

## 1. Clone the repository

```bash
git clone https://github.com/Mohamad82a/RabbitMQ-Senior-Developer-Roadmap.git

cd part1_rabbitmq_fundamentals/p05_headers_exchange
```

---

## 2. Create environment file

```bash
cp .env.example .env
```

Configure your RabbitMQ credentials inside `.env`.

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

# 📬 Send an Event

## Using Swagger

Open:

```text
http://localhost:8000/docs
```

Use:

```text
POST /send-event/
```

---

## Example Request — Normal Finance Event

```json
{
  "body": {
    "action": "generate_report",
    "user_id": "user_123",
    "format": "pdf"
  },
  "headers": {
    "department": "finance",
    "priority": "normal"
  }
}
```

This event is routed to the:

```text
Finance Worker
```

---

## Example Request — High Priority Finance Event

```json
{
  "body": {
    "action": "generate_report",
    "user_id": "user_123",
    "format": "pdf"
  },
  "headers": {
    "department": "finance",
    "priority": "high"
  }
}
```

This event is routed to the:

```text
High Priority Finance Worker
```

---

## Example Request — HR Event

```json
{
  "body": {
    "action": "update_employee",
    "user_id": "user_123"
  },
  "headers": {
    "department": "hr",
    "priority": "normal"
  }
}
```

This event is routed to the:

```text
HR Worker
```

---

# 🔄 Message Flow

### Step 1 — API receives the request

```text
POST /send-event/
```

↓

### Step 2 — Event Service creates the event payload

The service generates a unique `event_id` and adds metadata such as the creation timestamp.

↓

### Step 3 — Producer publishes the event

The producer publishes the event to the **Headers Exchange**.

The message headers are passed to RabbitMQ:

```text
department
priority
```

↓

### Step 4 — RabbitMQ evaluates the headers

RabbitMQ compares the message headers with the binding arguments of each queue.

↓

### Step 5 — Matching queue receives the event

Only queues whose header conditions match the message receive the event.

↓

### Step 6 — Consumer delegates processing

The consumer passes the event to its corresponding Handler.

↓

### Step 7 — Handler processes the event

The Handler executes the business logic and returns the result.

↓

### Step 8 — Message is acknowledged

After successful processing, the consumer sends an ACK to RabbitMQ.

---

# 📢 Headers Exchange

The producer declares a Headers Exchange:

```python
channel.exchange_declare(
    exchange="events",
    exchange_type="headers",
    durable=True
)
```

Unlike Direct and Topic Exchanges, a Headers Exchange does not use a routing key to determine the destination.

Instead, RabbitMQ uses the **message headers** and the queue's binding arguments.

The producer publishes with an empty routing key:

```python
channel.basic_publish(
    exchange="events",
    routing_key="",
    body=data,
    properties=pika.BasicProperties(
        delivery_mode=2,
        headers=headers
    )
)
```

---

# 📨 Queue Bindings

## Finance Queue

The Finance Worker handles normal Finance events:

```python
binding_arguments = {
    "x-match": "all",
    "department": "finance",
    "priority": "normal",
}
```

---

## High Priority Finance Queue

The High Priority Finance Worker handles high-priority Finance events:

```python
binding_arguments = {
    "x-match": "all",
    "department": "finance",
    "priority": "high",
}
```

---

## HR Queue

The HR Worker handles normal HR events:

```python
binding_arguments = {
    "x-match": "all",
    "department": "hr",
    "priority": "normal",
}
```

---

# 🔎 Header Matching

This project uses:

```python
"x-match": "all"
```

This means **all specified headers must match**.

For example:

```text
department = finance
priority = high
```

matches:

```python
{
    "x-match": "all",
    "department": "finance",
    "priority": "high"
}
```

but does not match:

```python
{
    "x-match": "all",
    "department": "finance",
    "priority": "normal"
}
```

---

# 🏛️ Project Design

The project separates RabbitMQ message consumption from business logic.

```text
Consumer
    │
    ▼
Base Consumer
    │
    ▼
Handler
    │
    ▼
Business Logic
```

The `BaseHeadersConsumer` contains the common RabbitMQ logic:

- Exchange declaration
- Queue declaration
- Queue binding
- QoS configuration
- Message consumption
- Message acknowledgement
- Error handling

Each specific consumer only defines:

- Queue name
- Binding arguments
- Handler

For example:

```python
class FinanceConsumer(BaseHeadersConsumer):

    queue_name = "finance_events"

    binding_arguments = {
        "x-match": "all",
        "department": "finance",
        "priority": "normal",
    }

    def __init__(self):
        super().__init__(
            handler=FinanceHandler()
        )
```

This prevents duplication between consumers.

---

# 🧩 Handler Architecture

Business logic is separated into independent handlers.

```text
BaseHandler
    │
    ├── FinanceHandler
    │
    ├── HighPriorityFinanceHandler
    │
    └── HRHandler
```

Each Handler is responsible for processing the event for its specific business case.

This keeps the Consumer focused on RabbitMQ operations instead of business logic.

The design uses concepts from:

- SOLID Principles
- Dependency Injection
- Strategy Pattern
- Template Method Pattern

---

# 🛡️ Reliability Features

## Durable Exchange

```python
channel.exchange_declare(
    exchange="events",
    exchange_type="headers",
    durable=True
)
```

---

## Durable Queues

```python
channel.queue_declare(
    queue="finance_events",
    durable=True
)
```

```python
channel.queue_declare(
    queue="high_priority_finance_events",
    durable=True
)
```

```python
channel.queue_declare(
    queue="hr_events",
    durable=True
)
```

---

## Persistent Messages

```python
pika.BasicProperties(
    delivery_mode=2
)
```

---

## Manual ACK

After successful processing:

```python
ch.basic_ack(
    delivery_tag=method.delivery_tag
)
```

These settings help ensure that messages are not lost if a consumer crashes before acknowledging them.

---

# ⚙️ Consumer Behavior

Each consumer uses:

```python
channel.basic_qos(
    prefetch_count=1
)
```

This limits the consumer to processing one unacknowledged message at a time.

Each consumer delegates the actual business logic to its corresponding Handler.

---

# 🐳 Docker Services

## rabbitmq

RabbitMQ broker with the Management UI.

---

## fastapi

Receives events and publishes them to the Headers Exchange.

---

## finance_consumer

Processes normal Finance events.

---

## high_priority_finance_consumer

Processes high-priority Finance events.

---

## hr_consumer

Processes normal HR events.

---

# 📊 Example Logs

## Producer

```text
INFO | [Producer] Published event successfully
```

---

## Finance Consumer

```text
INFO | [Finance Worker] Received event
INFO | [Finance Handler] Processing finance event
INFO | [Finance Handler] Event processed successfully
INFO | [Finance Worker] Message acknowledged successfully
```

---

## High Priority Finance Consumer

```text
INFO | [High-Priority Finance Worker] Received event
INFO | [High-Priority Finance Handler] Processing high priority finance event
INFO | [High-Priority Finance Handler] Event processed successfully
INFO | [High-Priority Finance Worker] Message acknowledged successfully
```

---

## HR Consumer

```text
INFO | [HR Worker] Received event
INFO | [HR Handler] Processing HR event
INFO | [HR Handler] Event processed successfully
INFO | [HR Worker] Message acknowledged successfully
```

---

# 🧪 Test the Routing

## Test 1 — Normal Finance Event

Send:

```json
{
  "body": {
    "action": "generate_report",
    "user_id": "user_123",
    "format": "pdf"
  },
  "headers": {
    "department": "finance",
    "priority": "normal"
  }
}
```

Expected:

```text
Finance Worker                  ✅
High Priority Finance Worker    ❌
HR Worker                       ❌
```

---

## Test 2 — High Priority Finance Event

Send:

```json
{
  "body": {
    "action": "generate_report",
    "user_id": "user_123",
    "format": "pdf"
  },
  "headers": {
    "department": "finance",
    "priority": "high"
  }
}
```

Expected:

```text
Finance Worker                  ❌
High Priority Finance Worker    ✅
HR Worker                       ❌
```

---

## Test 3 — HR Event

Send:

```json
{
  "body": {
    "action": "update_employee",
    "user_id": "user_123"
  },
  "headers": {
    "department": "hr",
    "priority": "normal"
  }
}
```

Expected:

```text
Finance Worker                  ❌
High Priority Finance Worker    ❌
HR Worker                       ✅
```

---

# 📚 Key Concepts

| Concept | Purpose |
|----------|---------|
| Exchange | Routes messages |
| Headers Exchange | Routes messages using headers |
| Message Headers | Define routing information |
| `x-match` | Defines how headers are matched |
| Queue Binding | Defines the required headers |
| Producer | Publishes events |
| Consumer | Receives events |
| Handler | Processes business logic |
| Durable Exchange | Survives broker restart |
| Durable Queue | Persists queue metadata |
| Persistent Message | Persists messages to disk |
| ACK | Confirms successful processing |
| Prefetch | Controls unacknowledged messages |

---

# 🔜 Next Step

## Day 6 — Work Queues

Learn how RabbitMQ distributes tasks between multiple workers using a shared queue, allowing background jobs to be processed concurrently and reliably.

---

# 📝 Author

**Mohamad Abbasi**

GitHub:

https://github.com/Mohamad82a

---

# 📄 License

This project is licensed under the MIT License. See the [LICENSE](../../LICENSE) file for details.
