# Day 1 — Setup & Basic Queue

> Build a basic RabbitMQ queue with FastAPI, Docker, and a background worker.

---

## 🎯 Goal

In this project we implement the **first messaging workflow**:

**FastAPI → RabbitMQ → Worker**

This is the foundation for all RabbitMQ patterns used in later days.

---

## 🧠 What You Will Learn

* Run RabbitMQ with Docker Compose
* Create a producer (publisher)
* Create a consumer (worker)
* Send messages from a FastAPI endpoint
* Process messages asynchronously
* Use durable queues and persistent messages
* Configure a production-style project structure

---

## 🏗️ Architecture

```text
Client
   |
   v
FastAPI API
   |
   v
RabbitMQ Queue (tasks)
   |
   v
Background Worker
```

---

## 📁 Project Structure

```text
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
│   ├── worker/
│   │   ├── __init__.py
│   │   └── consumer.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── rabbitmq.py
│   ├── __init__.py
│   └── main.py
│
├── tests/
│   ├── __init__.py
│   ├── test_producer.py
│   └── test_consumer.py
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

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Mohamad82a/RabbitMQ-Senior-Developer-Roadmap.git
cd rabbitmq-course/part1_rabbitmq_fundamentals/p01_basic_queue
```

### 2. Create environment file

```bash
cp .env.example .env
```

### 3. Start all services

```bash
docker compose up --build -d
```

---

## 🌐 Access Services

| Service                     | URL                        |
|-----------------------------| -------------------------- |
| FastAPI                     | http://localhost:8000      |
| Built-in FastAPI Swagger UI | http://localhost:8000/docs |
| RabbitMQ Management         | http://localhost:15672     |

RabbitMQ credentials are defined in the `.env` file.

---

## 📬 Send a Task

### Using Swagger

Open:

```text
http://localhost:8000/docs
```

Use the `POST /send-task/` endpoint.

### Example Request

```json
{
  "name": "generate_report",
  "body": {
            "format": "pdf",
            "user_id": "user_123",
            "department": "finance"
  }
}
```

### Example Response

```json
{
  "message": "Task accepted",
  "status": "accepted"
}
```

---

## 🔄 Message Flow

### Step 1 — API receives the request

```text
POST /send-task/
```

### Step 2 — Producer publishes the message

The producer serializes the task to JSON and publishes it to the `tasks` queue.

### Step 3 — RabbitMQ stores the message

The queue is declared as **durable** and messages are marked as **persistent**.

### Step 4 — Worker consumes the task

The worker processes the message and sends a manual ACK after successful completion.

---

## 🛡️ Reliability Features

### Durable Queue

```python
channel.queue_declare(
    queue=queue_name,
    durable=True
)
```

### Persistent Message

```python
pika.BasicProperties(delivery_mode=2)
```

### Manual ACK

```python
ch.basic_ack(delivery_tag=method.delivery_tag)
```

These three settings ensure messages survive broker restarts and are not lost if a worker crashes before acknowledging them.

---

## ⚙️ Worker Behavior

The worker uses:

```python
channel.basic_qos(prefetch_count=1)
```

This means each worker receives **one task at a time**, enabling fair task distribution across multiple workers.

---

## 🐳 Docker Services

### rabbitmq

RabbitMQ broker with management UI.

### fastapi

HTTP API that publishes tasks.

### worker

Background consumer that processes tasks from the queue.

---

## 📊 Example Logs

### Producer

```text
INFO | Task published successfully
```

### Worker

```text
INFO | Worker received task: {'name': 'generate_report', 'body': {'format': 'pdf', 'user_id': 'user_123', 'department': 'finance'}}
INFO | Task processed successfully
```

---

## 🧪 Test the Queue

Run multiple requests:

```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"name":"generate_report", "body": {"format': "pdf", "user_id": "user_123", "department": "finance"}}'
```

Then watch the worker logs:

```bash
docker compose logs -f worker
```

---

## 📚 Key Concepts

| Concept            | Purpose                        |
| ------------------ | ------------------------------ |
| Queue              | Stores messages                |
| Producer           | Publishes messages             |
| Consumer           | Processes messages             |
| Durable Queue      | Survives broker restart        |
| Persistent Message | Survives disk persistence      |
| ACK                | Confirms successful processing |
| QoS                | Controls message distribution  |

---

## 🔜 Next Step

**Day 2 — Fanout Exchange**

We will broadcast a single message to **multiple consumers** (Email and SMS services) using RabbitMQ Pub/Sub patterns.

---

## 📝 Author

**Mohamad A**

GitHub: https://github.com/Mohamad82a

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
