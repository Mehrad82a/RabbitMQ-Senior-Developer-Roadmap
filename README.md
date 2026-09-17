# RabbitMQ Senior Developer Roadmap

I’m happy to share my RabbitMQ learning and engineering journey through this repository.

I created this roadmap to explore RabbitMQ step by step—from fundamental messaging concepts to reliability patterns and production-oriented systems. Instead of focusing only on theory, each day includes an independent and practical project that demonstrates how RabbitMQ can be used to solve real backend engineering problems.

The repository starts with the fundamentals, gradually introduces more advanced reliability concepts, and finally moves toward senior-level projects inspired by real production scenarios.

My goal is to document not only the final implementations, but also the architectural decisions, technical challenges, engineering patterns, and lessons learned throughout the journey.

## Learning Roadmap

The roadmap is organized into three progressive parts. Each day introduces a new concept through an independent, runnable project.

---

## Part 1 — RabbitMQ Fundamentals

Directory:

```text
part1_rabbitmq_fundamentals/
```

This part focuses on RabbitMQ’s core components and messaging patterns. Each day introduces one fundamental concept and demonstrates how it works in practice.

| Day | Project | What You Will Learn |
|---:|---|---|
| 01 | Basic Queue | Learn how a producer publishes a message to a queue and how a consumer processes it asynchronously. |
| 02 | Fanout Exchange | Learn how to broadcast the same event to multiple independent queues and consumers. |
| 03 | Direct Exchange | Learn how to route messages selectively through exact routing-key matches. |
| 04 | Topic Exchange | Learn how to route messages flexibly using wildcard patterns such as `*` and `#`. |
| 05 | Headers Exchange | Learn how to route messages using headers and metadata instead of routing keys. |
| 06 | Work Queue | Learn how competing consumers distribute background tasks and balance workloads. |
| 07 | Message Persistence | Learn how durable queues, durable exchanges, and persistent messages survive broker restarts. |

By completing Part 1, you will understand RabbitMQ’s essential building blocks and the most common messaging patterns.

---

## Part 2 — Reliability Patterns

Directory:

```text
part2_reliability_patterns/
```

This part focuses on reliable delivery and failure handling. Each day demonstrates how RabbitMQ applications can respond safely to failed processing, delayed work, retries, prioritization, and request-response workflows.

| Day | Project | What You Will Learn |
|---:|---|---|
| 08 | Acknowledgment | Learn how manual acknowledgements, rejection, and requeue decisions control message delivery. |
| 09 | Dead-Letter Queue | Learn how to isolate expired, rejected, or repeatedly failed messages for later inspection. |
| 10 | Delay Queue | Learn how to postpone message processing using message TTL and dead-letter routing. |
| 11 | Priority Queue | Learn how to process important messages before lower-priority messages within the same queue. |
| 12 | Retry Strategy | Learn how to implement controlled retries, delay intervals, maximum attempts, and final dead-lettering. |
| 13 | RPC Pattern | Learn how to build request-response communication using `reply_to`, correlation IDs, and timeouts. |

By completing Part 2, you will understand how to build RabbitMQ workflows that remain predictable during failures, retries, delays, and message redelivery.

---

## Part 3 — Production Projects

Directory:

```text
part3_production_projects/
```

This part focuses on production-oriented engineering and senior-level design decisions. Each day applies RabbitMQ to a realistic scenario involving architecture, observability, testing, or complete event processing.

| Day | Project | What You Will Learn |
|---:|---|---|
| 14 | Background Tasks vs RabbitMQ | Learn when to use in-process background tasks and when a message broker is the safer architectural choice. |
| 15 | Logging and Monitoring | Learn how to observe message flow using structured logs, correlation IDs, metrics, and health monitoring. |
| 16 | Testing | Learn how to test producers, consumers, routing, acknowledgements, retries, and failure scenarios. |
| 17 | Event Tracking Project | Learn how to combine routing, reliability, observability, and event lifecycle tracking in a realistic production project. |

By completing Part 3, you will understand how to make architectural decisions and build observable, testable, and production-oriented RabbitMQ systems.

---

## Technology Stack

The projects use a consistent technology stack so the focus remains on RabbitMQ concepts, messaging patterns, reliability, and production-oriented architecture.

| Technology | Purpose |
|---|---|
| Python | Implements producers, consumers, handlers, services, and business logic |
| RabbitMQ | Provides message brokering, routing, queuing, and asynchronous communication |
| FastAPI | Exposes HTTP endpoints for publishing messages and testing workflows |
| Pika | Connects Python applications to RabbitMQ using AMQP |
| Pydantic | Validates API requests, events, and application data |
| Pydantic Settings | Loads configuration from environment variables |
| Uvicorn | Runs the FastAPI applications |
| Docker | Packages applications and consumers into isolated containers |
| Docker Compose | Starts RabbitMQ, APIs, producers, and consumers together |
| RabbitMQ Management UI | Monitors exchanges, queues, bindings, consumers, and messages |
| Swagger UI / OpenAPI | Provides interactive API documentation and request testing |
| Pytest | Tests business logic, messaging behavior, and failure scenarios |
| Environment Variables | Manage RabbitMQ credentials and application configuration |
| Structured Logging | Tracks message publication, routing, processing, and failures |

### Core Technologies

```text
Python
FastAPI
RabbitMQ
Pika
Pydantic
Docker
Docker Compose
Pytest
```

### Architecture and Engineering Practices
In addition to the technology stack, the projects demonstrate:
- Event-driven architecture
- Asynchronous communication
- Producer and consumer separation
- Publish/Subscribe
- Message routing
- Competing consumers
- Dependency injection
- SOLID principles
- Strategy pattern
- Template Method pattern
- Environment-based configuration
- Structured logging
- Failure handling
- Retry strategies
- Message acknowledgements
- Automated testing
- Containerized development


## Repository Structure

```text
RabbitMQ-Senior-Developer-Roadmap/
│
├── README.md
├── LICENSE
├── .gitignore
│
├── part1_rabbitmq_fundamentals/
│   │
│   ├── p01_basic_queue/
│   ├── p02_fanout_exchange/
│   ├── p03_direct_exchange/
│   ├── p04_topic_exchange/
│   ├── p05_headers_exchange/
│   ├── p06_work_queue/
│   └── p07_message_persistence/
│
├── part2_reliability_patterns/
│   │
│   ├── p08_acknowledgment/
│   ├── p09_dead_letter_queue/
│   ├── p10_delay_queue/
│   ├── p11_priority_queue/
│   ├── p12_retry_strategy/
│   └── p13_rpc_pattern/
│
└── part3_production_projects/
    │
    ├── p14_background_tasks_vs_rabbitmq/
    ├── p15_logging_monitoring/
    ├── p16_testing/
    └── p17_event_tracking_project/
```