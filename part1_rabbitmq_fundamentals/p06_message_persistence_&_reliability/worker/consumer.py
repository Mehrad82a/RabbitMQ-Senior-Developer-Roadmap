import sys, time, json, random
from api.rabbitmq_connection import RabbitMQConnection


def main():
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.connect()

    channel.queue_declare(queue='jobs', durable=True)
    channel.basic_qos(prefetch_count=1)


    def callback(ch, method, properties, body):
        task = json.loads(body)

        for attempt in range(3):
            try:
                print(f'[Worker] received task: {task}')
                time.sleep(10) # For work simulation
                success = random.choice([True, False])

                if success:
                    print('[Worker] Success')
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return

                else:
                    print(f'[Worker] Failed on attempt {attempt + 1}')

            except Exception as e:
                print(f'[Worker] Exception: {e}')


        print(f'[Worker] All retries failed -> Requeue')
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


    channel.basic_consume(queue='jobs', on_message_callback=callback)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
