import sys, time, json
from api.rabbitmq_connection import RabbitMQConnection



def main():
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.connect()

    channel.exchange_declare(
        exchange='jobs_exchange',
        exchange_type='direct',
        durable=True
    )

    queue_name = 'image_queue'

    channel.queue_declare(
        queue=queue_name,
        durable=True
    )

    channel.queue_bind(
        exchange='jobs_exchange',
        queue=queue_name,
        routing_key='image.job'
    )

    channel.basic_qos(
        prefetch_count=1,
    )


    def callback(ch, method, properties, body):
        data = json.loads(body)

        print(f'[IMAGE Service] Processing image job')
        time.sleep(5)  # For work simulation
        print('[IMAGE Service] Image processed')

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
