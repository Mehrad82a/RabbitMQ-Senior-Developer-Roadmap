Direct Exchange:
```python
routing_key = welcome_email
```

Topic Exchange:
```python
user.created
or 
user.update
or
user.deleted
```
Different works for each

But in Header Exchange, Routing Key is not imported at all.
RabbitMQ decides based on Headers of messages


Example:
Only the worker with normal priority defined in its header will receive this task
```python
headers = {
    "department": "finance",
    "priority": "normal"
}
```

Only the worker with high priority defined in its header will receive this task
```python
headers = {
    "department": "finance",
    "priority": "high"
}
```