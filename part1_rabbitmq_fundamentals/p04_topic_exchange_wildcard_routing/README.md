p04_topic_exchange_wildcard_routing/
│
├── app/
│   ├── api/
│   │   ├── routes.py
│   │   └── schemas.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── rabbitmq.py
│   │
│   ├── producer/
│   │   └── producer.py
│   │
│   ├── services/
│   │   └── handlers/
│   │       ├── base_handler.py
│   │       ├── user_handler.py
│   │       ├── order_handler.py
│   │       └── error_handler.py
│   │
│   ├── workers/
│   │   ├── base_consumer.py
│   │   └── consumers/
│   │       ├── user_consumer.py
│   │       ├── order_consumer.py
│   │       └── error_consumer.py
│   │
│   └── main.py
│
├── tests/ (planned for future implementation)
│   ├── test_producer.py
│   ├── test_user_consumer.py
│   ├── test_order_consumer.py
│   └── test_error_consumer.py
│
├── .env.example
├── .gitignore
├── .dockerignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md