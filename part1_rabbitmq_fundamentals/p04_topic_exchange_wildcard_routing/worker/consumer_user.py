import sys, time, json
from api.rabbitmq_connection import RabbitMQConnection


def main():
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.connect()

    channel.exchange_declare(exchange='topic_events', exchange_type='topic')

    queue_name = 'user_service_queue'

    channel.queue_declare(queue=queue_name, durable=True)

    # Bind queue to exchange
    channel.queue_bind(exchange='topic_events', queue=queue_name, routing_key='user.#')

    print(f"[USER Service] Listening for all user events on queue: {queue_name}...")

    def callback(ch, method, properties, body):
        data = json.loads(body)

        print(f'[USER Service] Received: {method.routing_key} -> {data}')
        time.sleep(3)  # For work simulation
        print('[USER Service] Done')

        ch.basic_ack(delivery_tag=method.delivery_tag)


    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)


