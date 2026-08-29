# Day 4 — Topic Exchange (Wildcard Routing)

> Route messages intelligently using wildcard routing keys with RabbitMQ Topic Exchange, FastAPI, and Docker.

---

# 🎯 Goal

In this project we implement the RabbitMQ **Topic Exchange** pattern.

Unlike Direct Exchange, Topic Exchange allows a message to be routed to one or more queues based on **routing key patterns**.

```
                 +----------------+
                 |    FastAPI     |
                 +----------------+
                         |
                         v
               RabbitMQ Topic Exchange
                         |
      -----------------------------------------
      |                  |                    |
      v                  v                    v
 User Queue         Order Queue        Error Queue
 (user.#)          (order.#)          (#.error)
```

This enables flexible message routing using wildcard patterns.

---

# 🧠 What You Will Learn

- Understand Topic Exchange
- Learn wildcard routing (`*` and `#`)
- Bind queues using routing patterns
- Publish events with routing keys
- Route one message to multiple queues
- Build reusable consumers
- Apply SOLID architecture with handlers
- Organize a scalable RabbitMQ project

---

# 🏗️ Architecture

```
                 Client
                    |
                    v
               FastAPI API
                    |
                    v
                 Producer
                    |
                    v
        RabbitMQ Topic Exchange
                    |
      ---------------------------------
      |               |              |
      v               v              v
 User Queue      Order Queue    Error Queue
      |               |              |
      v               v              v
 User Handler   Order Handler   Error Handler
```

Each consumer processes only the messages matching its routing pattern.

---

# 📁 Project Structure

```text
p04_topic_exchange/
│
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── schemas.py
│   │
│   ├── producer/
│   │   ├── __init__.py
│   │   └── producer.py
│   │
│   ├── consumers/
│   │   ├── __init__.py
│   │   ├── base_consumer.py
│   │   ├── user_consumer.py
│   │   ├── order_consumer.py
│   │   ├── error_consumer.py
│   │   └── created_consumer.py
│   │
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── handlers/
│   │       ├── base_handler.py
│   │       ├── user_handler.py
│   │       ├── order_handler.py
│   │       ├── error_handler.py
│   │       └── created_handler.py
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
│
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

## 1. Clone the repository

```bash
git clone https://github.com/Mohamad82a/RabbitMQ-Senior-Developer-Roadmap.git

cd part1_rabbitmq_fundamentals/p04_topic_exchange_wildcard_routing
```

---

## 2. Create environment file

```bash
cp .env.example .env
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

# 📬 Publish an Event

## Using Swagger

Open

```
http://localhost:8000/docs
```

Use the endpoint

```
POST /send-event/
```

---

## Example Request

```json
{
  "routing_key": "user.created",
  "message": "New user registered."
}
```

---

## Example Response

```json
{
  "message": "Event accepted",
  "status": "queued"
}
```

---

# 🔄 Message Flow

### Step 1 — API receives the request

```
POST /send-event/
```

↓

### Step 2 — Producer publishes the event

The producer serializes the event and publishes it to the **Topic Exchange**.

↓

### Step 3 — RabbitMQ evaluates the routing key

RabbitMQ compares the routing key with every queue binding pattern.

↓

### Step 4 — Matching queues receive the event

One or multiple queues may receive the same message depending on the wildcard patterns.

↓

### Step 5 — Consumers process the event

Each consumer handles only the messages matching its binding key.

---

# 📢 Topic Exchange

The producer declares a Topic Exchange:

```python
channel.exchange_declare(
    exchange="topic_events",
    exchange_type="topic",
    durable=True
)
```

Unlike a Direct Exchange, a Topic Exchange routes messages based on **pattern matching** between the published routing key and the queue binding key.

This enables flexible message routing, allowing one message to be delivered to one or multiple queues using wildcard patterns.

---

# 🌟 Wildcard Routing

RabbitMQ Topic Exchange supports two wildcard characters:

| Wildcard | Description |
|----------|-------------|
| `*` | Matches exactly one word |
| `#` | Matches zero or more words |

Examples:

| Binding Key | Matches |
|------------|---------|
| `user.*` | `user.created`, `user.updated` |
| `user.#` | `user.created`, `user.profile.updated`, `user.deleted` |
| `#.error` | `database.error`, `user.error`, `payment.service.error` |
| `#.created` | `user.created`, `order.created`, `invoice.created` |

---

# 📨 Queue Bindings

User Queue

```python
channel.queue_bind(
    exchange="topic_events",
    queue="user_events",
    routing_key="user.#"
)
```

Order Queue

```python
channel.queue_bind(
    exchange="topic_events",
    queue="order_events",
    routing_key="order.#"
)
```

Error Queue

```python
channel.queue_bind(
    exchange="topic_events",
    queue="error_events",
    routing_key="#.error"
)
```

Created Queue

```python
channel.queue_bind(
    exchange="topic_events",
    queue="created_events",
    routing_key="#.created"
)
```

A single published message may be delivered to **multiple queues** if its routing key matches multiple binding patterns.

---

# 🏛️ Project Design

To keep the project modular and maintainable, the business logic is separated from the RabbitMQ consumers.

```
Consumer
    │
    ▼
Base Topic Consumer
    │
    ▼
Handler
    │
    ▼
Business Logic
```

Each consumer is responsible only for consuming RabbitMQ messages, while each handler contains the business logic for processing a specific category of events.

This design follows:

- SOLID Principles
- Template Method Pattern
- Strategy Pattern
- Dependency Injection

---

# 🛡️ Reliability Features

## Durable Exchange

```python
channel.exchange_declare(
    exchange="topic_events",
    exchange_type="topic",
    durable=True
)
```

---

## Durable Queues

```python
channel.queue_declare(
    queue="user_events",
    durable=True
)
```

```python
channel.queue_declare(
    queue="order_events",
    durable=True
)
```

```python
channel.queue_declare(
    queue="error_events",
    durable=True
)
```

```python
channel.queue_declare(
    queue="created_events",
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

```python
ch.basic_ack(
    delivery_tag=method.delivery_tag
)
```

These settings ensure that messages survive broker restarts and are not lost if a consumer crashes before acknowledging them.

---

# ⚙️ Consumer Behavior

Each consumer uses:

```python
channel.basic_qos(
    prefetch_count=1
)
```

This limits each consumer to processing one unacknowledged message at a time, improving reliability and fair workload distribution.

Each consumer delegates the business logic to its corresponding handler.

---

# 🐳 Docker Services

## rabbitmq

RabbitMQ broker with the Management UI.

---

## fastapi

Publishes events to the Topic Exchange.

---

## user_consumer

Processes events matching the `user.#` routing pattern.

---

## order_consumer

Processes events matching the `order.#` routing pattern.

---

## error_consumer

Processes events matching the `#.error` routing pattern.

---

## created_consumer

Processes events matching the `#.created` routing pattern.

---

# 📊 Example Logs

## Producer

```
INFO | Published event successfully
```

---

## User Consumer

```
INFO | [UserConsumer] Received event
INFO | [User Handler] Processing event...
INFO | [User Handler] Event processed successfully
INFO | [UserConsumer] Result: ...
INFO | [UserConsumer] Event acknowledged successfully

```

---

## Order Consumer

```
INFO | OrderConsumer] Received event
INFO | Order Handler] Processing event...
INFO | Order Handler] Event processed successfully
INFO | OrderConsumer] Result: ...
INFO | OrderConsumer] Event acknowledged successfully
```

---

## Error Consumer

```
INFO | [ErrorConsumer] Received event
INFO | [Error Handler] Processing event...
INFO | [Error Handler] Event processed successfully
INFO | [ErrorConsumer] Result: ...
INFO | [ErrorConsumer] Event acknowledged successfully
```

---

## Created Consumer

```
INFO | [CreatedConsumer] Received event
INFO | [Created Handler] Processing event...
INFO | [Created Handler] Event processed successfully
INFO | [CreatedConsumer] Result: ...
INFO | [CreatedConsumer] Event acknowledged successfully
```

---

# 🧪 Test the Project

Using curl

```bash
curl -X POST http://localhost:8000/send-event/ \
-H "Content-Type: application/json" \
-d '{
      "routing_key":"user.created",
      "message":"New user registered"
}'
```

Watch the logs:

```bash
docker compose logs -f user_worker
```

```bash
docker compose logs -f created_worker
```

Both consumers should receive the same message because the routing key `user.created` matches both `user.#` and `#.created`.

Now try:

```json
{
  "routing_key": "database.error",
  "message": "Database connection failed"
}
```

Only the **Error Consumer** should receive the message.

---

# 📚 Key Concepts

| Concept | Purpose |
|----------|---------|
| Exchange | Routes messages |
| Topic Exchange | Routes messages using wildcard patterns |
| Routing Key | Identifies the message topic |
| Binding Key | Defines which routing keys a queue receives |
| `*` Wildcard | Matches exactly one word |
| `#` Wildcard | Matches zero or more words |
| Producer | Publishes events |
| Consumer | Receives events |
| Handler | Processes business logic |
| Durable Exchange | Survives broker restart |
| Durable Queue | Persists queue metadata |
| Persistent Message | Persists messages to disk |
| ACK | Confirms successful processing |

---

# 🔜 Next Step

## Day 5 — Headers Exchange

Learn how to route messages based on **message headers** instead of routing keys, enabling attribute-based message filtering.

---

# 📝 Author

**Mohamad Abbasi**

GitHub:

https://github.com/Mohamad82a

---

# 📄 License

This project is licensed under the MIT License. See the [LICENSE](../../LICENSE) file for details.