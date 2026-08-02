# Day 3 — Direct Exchange (Routing by Key)

> Route messages selectively using RabbitMQ **Direct Exchange** and **Routing Keys** with FastAPI, Docker, and Python.

---

# 🎯 Goal

In this project we implement the RabbitMQ **Direct Exchange** pattern.

Unlike the Fanout Exchange, where every consumer receives every published message, a Direct Exchange delivers each message **only to the queue whose binding key exactly matches the routing key**.

```
                +----------------+
                |    FastAPI     |
                +----------------+
                        |
                        v
            RabbitMQ Direct Exchange
                 (direct_logs)
              /        |         \
             /         |          \
            v          v           v
      Info Queue  Warning Queue  Error Queue
           |            |             |
           v            v             v
     Info Worker  Warning Worker  Error Worker
```

Each worker processes only the messages it is responsible for.

---

# 🧠 What You Will Learn

- Understand the Direct Exchange pattern
- Learn how routing keys work
- Bind queues using routing keys
- Route messages selectively
- Build multiple independent consumers
- Apply SOLID principles
- Use Template Method and Strategy patterns
- Separate business logic using handlers
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
          RabbitMQ Direct Exchange
               (direct_logs)
          /          |           \
         /           |            \
        v            v             v
 info_logs     warning_logs    error_logs
      |             |               |
      v             v               v
Info Consumer  Warning Consumer  Error Consumer
      |             |               |
      v             v               v
Info Handler  Warning Handler  Error Handler
```

Each message is delivered only to the consumer whose routing key matches the published routing key.

---

# 📁 Project Structure

```text
p03_direct_exchange_routing_by_key/
│
├── app/
│   ├── api/
│   │   ├── routes.py
│   │   └── schemas.py
│   │
│   ├── producer/
│   │   └── producer.py
│   │
│   ├── consumers/
│   │   ├── base_consumer.py
│   │   ├── info_consumer.py
│   │   ├── warning_consumer.py
│   │   └── error_consumer.py
│   │
│   │
│   ├── services/
│   │   └── handlers/
│   │       ├── base_handler.py
│   │       ├── info_handler.py
│   │       ├── warning_handler.py
│   │       └── error_handler.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── rabbitmq.py
│   │
│   └── main.py
│
├── tests/ (Coming soon)
│   ├── test_producer.py
│   ├── test_info_consumer.py
│   ├── test_warning_consumer.py
│   └── test_error_consumer.py
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

cd rabbitmq-course/part1_rabbitmq_fundamentals/p03_direct_exchange_routing_by_key
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

# 📬 Send a Log Message

## Using Swagger

Open

```
http://localhost:8000/docs
```

Use the endpoint:

```
POST /send-log/
```

---

## Example Request

```json
{
  "level": "warning",
  "message": "CPU usage exceeded 90%"
}
```

---

## Example Response

```json
{
"status": "sent",
"level": "warning",
"message": "CPU usage exceeded 90%"
}
```

---

# 🔄 Message Flow

### Step 1 — API receives the request

```
POST /send-log/
```

↓

### Step 2 — Producer publishes the message

The producer serializes the log message and publishes it to the **Direct Exchange** using the specified routing key.

↓

### Step 3 — RabbitMQ checks the routing key

The Direct Exchange compares the routing key with all queue binding keys.

↓

### Step 4 — Matching queue receives the message

Only the queue whose binding key matches the routing key receives the message.

↓

### Step 5 — Consumer processes the message

The corresponding consumer receives the message and delegates the business logic to its handler.

↓

### Step 6 — Handler executes the business logic

The appropriate handler processes the message and the consumer acknowledges it.

---

# 📢 Direct Exchange

The producer declares a Direct Exchange:

```python
channel.exchange_declare(
    exchange="direct_logs",
    exchange_type="direct",
    durable=True
)
```

Unlike a Fanout Exchange, a Direct Exchange routes messages **only to queues whose binding key exactly matches the published routing key**.

This enables selective message delivery, allowing different consumers to process different types of messages.

---

# 📨 Queue Bindings

Info Queue

```python
channel.queue_bind(
    exchange="direct_logs",
    queue="info_logs",
    routing_key="info"
)
```

Warning Queue

```python
channel.queue_bind(
    exchange="direct_logs",
    queue="warning_logs",
    routing_key="warning"
)
```

Error Queue

```python
channel.queue_bind(
    exchange="direct_logs",
    queue="error_logs",
    routing_key="error"
)
```

Each queue receives **only the messages whose routing key matches its binding key**.

---

# 🏛️ Project Design

To keep the project modular and maintainable, the business logic is separated from the RabbitMQ consumers.

```
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

Each consumer is responsible only for consuming messages, while each handler contains the business logic for processing a specific log level.

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
    exchange="direct_logs",
    exchange_type="direct",
    durable=True
)
```

---

## Durable Queues

```python
channel.queue_declare(
    queue="info_logs",
    durable=True
)
```

```python
channel.queue_declare(
    queue="warning_logs",
    durable=True
)
```

```python
channel.queue_declare(
    queue="error_logs",
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

This limits each worker to processing one unacknowledged message at a time, providing fair message distribution and improving reliability.

Each consumer delegates the processing logic to its corresponding handler.

---

# 🐳 Docker Services

## rabbitmq

RabbitMQ broker with the Management UI.

---

## fastapi

Publishes log messages to the Direct Exchange.

---

## info_consumer

Processes messages with the **info** routing key.

---

## warning_consumer

Processes messages with the **warning** routing key.

---

## error_consumer

Processes messages with the **error** routing key.

---

# 📊 Example Logs

## Producer

```
INFO | Published log successfully
```

---

## Info Consumer

```
INFO | [Info Worker] Received...
INFO | Processing message...
INFO | [Info Worker] Message processed successfully
```

---

## Warning Consumer

```
INFO | [Warning Worker] Received...
INFO | Processing message...
INFO | [Warning Worker] Message processed successfully
```

---

## Error Consumer

```
INFO | [Error Worker] Received message
INFO | Processing message...
INFO | [Error Worker] Message processed successfully
```

---

# 🧪 Test the Project

Using curl

```bash
curl -X POST http://localhost:8000/send-log/ \
-H "Content-Type: application/json" \
-d '{
      "level":"warning",
      "message":"CPU usage exceeded 90%"
}'
```

Watch the logs:

```bash
docker compose logs -f warning_consumer
```

Then try:

```json
{
  "level": "error",
  "message": "Database connection failed"
}
```

Now only the **Error Consumer** should receive the message.

---

# 📚 Key Concepts

| Concept | Purpose |
|----------|----------|
| Exchange | Routes messages |
| Direct Exchange | Routes messages by routing key |
| Routing Key | Determines the destination queue |
| Queue Binding | Associates a queue with a routing key |
| Producer | Publishes messages |
| Consumer | Receives messages |
| Handler | Processes business logic |
| Durable Exchange | Survives broker restart |
| Durable Queue | Persists queue metadata |
| Persistent Message | Persists messages to disk |
| ACK | Confirms successful processing |

---

# 🔜 Next Step

## Day 4 — Topic Exchange

Learn how to route messages using **wildcard routing keys**, allowing consumers to subscribe to multiple related topics with flexible matching patterns.

---

# 📝 Author

**Mohamad Abbasi**

GitHub:

https://github.com/Mohamad82a

---

# 📄 License

This project is licensed under the MIT License. See the [LICENSE](../../LICENSE) file for details.