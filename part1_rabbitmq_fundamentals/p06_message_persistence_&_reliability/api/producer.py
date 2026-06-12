import os, json, pika


from rabbitmq_connection import RabbitMQConnection


def publish(data: dict):
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.connect()

    # Declare a durable queue
    channel.queue_declare(queue='jobs', durable=True)

    channel.basic_publish(
        exchange='',
        routing_key='jobs',
        body=json.dumps(data),
        properties=pika.BasicProperties(
            delivery_mode=2,   # --> to persist on the message and avoid losing it.
        )
    )

    print(f'[x] Job published: {data}')


