# AWS SQS Queue

Amazon Simple Queue Service integration.

## Installation

```bash
pip install boto3
```

```python
INSTALLED_APPS = [
    'django_extensions.aws_sqs_queue',
]
```

## Configuration

```python
# settings.py
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_SQS_REGION = 'us-east-1'
AWS_SQS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/123456789/my-queue'
```

## Usage

### SQSQueue Class

```python
from django_extensions.aws_sqs_queue import SQSQueue

queue = SQSQueue('my-queue')

# Send message
queue.send({'event': 'user_created', 'user_id': 123})

# Send with delay
queue.send({'event': 'reminder'}, delay_seconds=300)

# Receive messages
messages = queue.receive(max_messages=10)
for msg in messages:
    print(msg.body)
    msg.delete()  # Remove from queue

# Batch send
queue.send_batch([
    {'event': 'event1'},
    {'event': 'event2'},
    {'event': 'event3'},
])
```

### Message Handling

```python
messages = queue.receive(
    max_messages=10,
    wait_time_seconds=20,  # Long polling
    visibility_timeout=60
)

for message in messages:
    try:
        data = message.body  # Already parsed JSON
        process(data)
        message.delete()
    except Exception:
        # Message returns to queue after visibility timeout
        pass
```

### Queue Management

```python
from django_extensions.aws_sqs_queue import (
    create_queue,
    delete_queue,
    purge_queue,
    get_queue_attributes
)

# Create queue
queue_url = create_queue('my-queue', fifo=False)

# Get queue stats
attrs = get_queue_attributes('my-queue')
print(attrs['ApproximateNumberOfMessages'])

# Purge all messages
purge_queue('my-queue')
```

### Dead Letter Queue

```python
queue = SQSQueue('my-queue', dead_letter_queue='my-dlq')

# Failed messages automatically move to DLQ after max receives
```

## Worker Pattern

```python
from django_extensions.aws_sqs_queue import SQSQueue

def worker():
    queue = SQSQueue('tasks')
    while True:
        for message in queue.receive(wait_time_seconds=20):
            try:
                handle_task(message.body)
                message.delete()
            except Exception as e:
                logger.error(f"Task failed: {e}")
```

## License

MIT
