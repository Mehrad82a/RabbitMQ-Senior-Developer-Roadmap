Some thinks that this is enough:
```python
durable=True
```
But for not losing the message, we should add:
```python
delivery_mode=2
```

Worst thing to do:
```python
auto_ack=True
```
Why? Because Rabbitmq delete the message before it's fully done by worker. And if worker crashes during 
the task:
```text
Message Lost ❌
```
In production:
```text
manual ack
```


The flow:
```text
              Queue
                |
      ---------------------
      |         |         |
   Worker1   Worker2   Worker3
      |
   gets Task A
      |
    fails
      |
  Attempt 1
      |
   Success? ---- Yes ---> ACK ---> Done
      |
      No
      |
  Attempt 2
      |
   Success? ---- Yes ---> ACK ---> Done
      |
      No
      |
  Attempt 3
      |
   Success? ---- Yes ---> ACK ---> Done
      |
      No
      |
 basic_nack(requeue=True)
      |
Message goes back to RabbitMQ
      |
      v
              Queue
                |
      ---------------------
      |         |         |
   Worker1   Worker2   Worker3
                |
          Worker2 gets Task A

```
