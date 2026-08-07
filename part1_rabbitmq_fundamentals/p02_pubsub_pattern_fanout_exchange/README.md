# Day 2 — Fanout Exchange (Publish / Subscribe)

> Broadcast a single message to multiple consumers using RabbitMQ Fanout Exchange with FastAPI and Docker.

---

# 🎯 Goal

In this project we implement the RabbitMQ **Publish / Subscribe** pattern.

A single message published by FastAPI is automatically delivered to multiple independent consumers.

```
            +----------------+
            |    FastAPI     |
            +----------------+
                    |
                    v
          RabbitMQ Fanout Exchange
            /                  \
           /                    \
          v                      v
 Email Consumer            SMS Consumer
```

Unlike Day 1, where one message was consumed by a single worker, here every consumer receives its own copy of the published event.

---

# 🧠 What You Will Learn

- Understand the Publish / Subscribe messaging pattern
- Create and configure a Fanout Exchange
- Broadcast a message to multiple queues
- Bind multiple queues to the same exchange
- Build multiple independent consumers
- Separate business logic into services
- Organize a scalable RabbitMQ project
- Test event broadcasting with FastAPI

---

# 🏗️ Architecture

```
                Client
                   |
                   v
             FastAPI API
                   |
                   v
      RabbitMQ Fanout Exchange
          (notifications)
             /         \
            /           \
           v             v
   Email Queue      SMS Queue
        |               |
        v               v
 Email Consumer    SMS Consumer
```

Every published event is copied into **both queues**, allowing each service to process the event independently.

---

# 📁 Project Structure

```
p01_basic_queue/
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
│   │   ├── email_consumer.py
│   │   └── sms_consumer.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── broadcast_service.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── rabbitmq.py
│   ├── __init__.py
│   └── main.py
│
├── tests/ (Coming soon)
│   ├── __init__.py
│   ├── test_producer.py
│   ├── test_email_consumer.py
│   └── test_sms_consumer.py
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

cd part1_rabbitmq_fundamentals/p02_pubsub_pattern_fanout_exchange
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

# 📬 Broadcast a Notification

## Using Swagger

Open

```
http://localhost:8000/docs
```

Use the endpoint:

```
POST /broadcast-event/
```

---

## Example Request

```json
{
  "user_id": "user_123",
  "title": "Payment Successful",
  "message": "Your invoice has been paid successfully."
}
```

---

## Example Response

```json
{
  "message": "Notification sent successfully",
  "status": "sent"
}
```

---

# 🔄 Message Flow

### Step 1 — API receives the request

```
POST /broadcast-evnt/
```

↓

### Step 2 — Producer publishes the event

The producer serializes the notification and publishes it to the **Fanout Exchange**.

↓

### Step 3 — RabbitMQ broadcasts the message

The Fanout Exchange sends a copy of the message to every bound queue.

↓

### Step 4 — Email Consumer receives the message

The Email service processes the notification.

↓

### Step 5 — SMS Consumer receives the message

The SMS service processes the same notification independently.

---

# 📢 Fanout Exchange

The producer declares a Fanout Exchange:

```python
channel.exchange_declare(
    exchange="notifications",
    exchange_type="fanout",
    durable=True
)
```

Unlike Direct or Topic exchanges, Fanout completely ignores routing keys.

Every bound queue receives every published message.

---

# 📨 Queue Bindings

Email Queue

```python
channel.queue_bind(
    exchange="notifications",
    queue="email_notifications"
)
```

SMS Queue

```python
channel.queue_bind(
    exchange="notifications",
    queue="sms_notifications"
)
```

Because both queues are bound to the same Fanout Exchange, every published notification is delivered to both queues.

---

# 🛡️ Reliability Features

## Durable Exchange

```python
channel.exchange_declare(
    durable=True
)
```

---

## Durable Queues

```python
channel.queue_declare(
    queue="email_notifications",
    durable=True
)
```

```python
channel.queue_declare(
    queue="sms_notifications",
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

---

# 🐳 Docker Services

## rabbitmq

RabbitMQ broker with Management UI.

---

## fastapi

Publishes notification events.

---

## email_consumer

Processes email message for broadcast notifications.

---

## sms_consumer

Processes SMS message for broadcast notifications.

---

# 📊 Example Logs

## Producer

```
INFO | Published event successfully
```

---

## Email Consumer

```
INFO | [Email Worker] received event
INFO | Sending email to user_123 (3 secs)
INFO | Email Worker] Event processed successfully
```

---

## SMS Consumer

```
INFO | [SMS Worker] received event
INFO | Sending sms to user_123 (3 secs)
INFO | SMS Worker] Event processed successfully
```

---

# 🧪 Test the Broadcast

Using curl

```bash
curl -X POST http://localhost:8000/broadcast-event/ \
-H "Content-Type: application/json" \
-d '{
      "user_id":"user_123",
      "title":"Payment Successful",
      "message":"Your invoice has been paid successfully."
}'
```

Watch the logs:

```bash
docker compose logs -f email_consumer
```

```bash
docker compose logs -f sms_consumer
```

You should observe that **both consumers receive and process the exact same notification**.

---

# 📚 Key Concepts

| Concept | Purpose |
|----------|----------|
| Exchange | Routes messages |
| Fanout Exchange | Broadcasts messages to all queues |
| Queue | Stores messages |
| Producer | Publishes events |
| Consumer | Processes events |
| Queue Binding | Connects a queue to an exchange |
| Durable Exchange | Survives broker restart |
| Durable Queue | Persists queue metadata |
| Persistent Message | Persists messages to disk |
| ACK | Confirms successful processing |

---

# 🔜 Next Step

## Day 3 — Direct Exchange

Learn how to route messages selectively using **routing keys**, allowing different consumers to receive only the messages they are interested in.

---

# 📝 Author

**Mohamad Abbasi**

GitHub:

https://github.com/Mohamad82a

---

# 📄 License

This project is licensed under the MIT License. See the [LICENSE](../../LICENSE) file for details.
