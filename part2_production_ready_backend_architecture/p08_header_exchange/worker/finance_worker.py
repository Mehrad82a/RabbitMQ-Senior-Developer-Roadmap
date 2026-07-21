import os, pika, json, time, random, sys

from api.rabbitmq_connection import RabbitMQConnection


def main():
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.connect()

    channel.exchange_declare(
        exchange='department_exchange',
        exchange_type='headers',
        durable=True
    )

    queue_name = 'finance_queue'

    channel.queue_declare(
        queue=queue_name,
        durable=True
    )

    channel.queue_bind(
        exchange='department_exchange',
        queue=queue_name,
        arguments={
            'x-match': 'all',
            'department': 'finance',
            'priority': 'normal'

        }
    )

    channel.basic_qos(
        prefetch_count=1,
    )

    def callback(ch, method, properties, body):
        job = json.loads(body)

        for attempt in range(3):
            try:
                print(f'[FINANCE Service] Job received: {job}')
                time.sleep(5)  # For work simulation
                success = random.choice([True, False])

                if success:
                    print(f'[FINANCE Service] Job finished ✅: {job}')
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return

                else:
                    print(f'[FINANCE Service] Failed on attempt {attempt + 1} ❌')

            except Exception as e:
                print(f'[FINANCE Service] Exception: {e}')

        print(f'[FINANCE Service] All retries failed -> Requeue')
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)



