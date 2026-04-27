import sys, time, json
from api.rabbitmq_connection import RabbitMQConnection


def main():
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.connect()

    channel.exchange_declare(exchange='topic_events', exchange_type='topic')

    queue_name = 'order_service_queue'

    channel.queue_declare(queue=queue_name, durable=True)

    # Bind queue to exchange
    channel.queue_bind(exchange='topic_events', queue=queue_name, routing_key='order.#')

    print(f"[ORDER Service] Listening for all order events on queue: {queue_name}...")

    def callback(ch, method, properties, body):
        data = json.loads(body)

        print(f'[ORDER Service] Received: {method.routing_key} -> {data}')
        time.sleep(3)  # For work simulation
        print(f'[ORDER Service] Done')

    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)


