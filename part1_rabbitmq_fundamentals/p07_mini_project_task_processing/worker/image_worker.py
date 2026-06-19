import sys, time, json, random
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
        json.loads(body)

        for attempt in range(3):
            try:
                print(f'[EMAIL Service] Sending email')
                time.sleep(5)  # For work simulation
                success = random.choice([True, False])

                if success:
                    print('[IMAGE Service] Image processed')
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return

                else:
                    print(f'[IMAGE Service] Failed on attempt {attempt + 1}')

            except Exception as e:
                print(f'[IMAGE Service] Exception: {e}')

        print(f'[IMAGE Service] All retries failed -> Requeue')
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
