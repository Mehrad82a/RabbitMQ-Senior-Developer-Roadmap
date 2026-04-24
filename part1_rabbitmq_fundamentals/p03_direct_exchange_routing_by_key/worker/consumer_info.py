import sys, time, json
from api.rabbitmq_connection import RabbitMQConnection


def main():
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.connect()

    channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

    queue_name = 'info_logs'

    # Each worker connects to its direct queue
    channel.queue_declare(queue=queue_name, durable=True)

    # Bind queue to exchange
    channel.queue_bind(exchange='direct_logs', queue=queue_name, routing_key='info')

    print(f"[INFO Service] Waiting for info messages on queue: '{queue_name}'...")

    def callback(ch, method, properties, body):
        data = json.loads(body)

        print(f'[INFO Service] Received info; sending message for: {data}')
        time.sleep(3)  # For work simulation
        print(f'[INFO Service] Done')

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)

