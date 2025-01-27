# Redis Cache

Redis caching with rate limiting and distributed locks.

## Installation

```bash
pip install redis
```

```python
INSTALLED_APPS = [
    'django_extensions.redis_cache',
]
```

## Configuration

```python
# settings.py
REDIS_URL = 'redis://localhost:6379/0'

# Or with authentication
REDIS_URL = 'redis://:password@localhost:6379/0'

# Optional settings
REDIS_KEY_PREFIX = 'myapp'
REDIS_DEFAULT_TTL = 3600
```

## Usage

### Basic Caching

```python
from django_extensions.redis_cache import cache_get, cache_set, cache_delete

# Set value
cache_set('user:123', {'name': 'John', 'email': 'john@example.com'}, ttl=3600)

# Get value
user = cache_get('user:123')

# Delete value
cache_delete('user:123')
```

### Rate Limiting

```python
from django_extensions.redis_cache import rate_limit

def api_view(request):
    user_id = request.user.id

    if not rate_limit(f'api:user:{user_id}', limit=100, window=60):
        return JsonResponse({'error': 'Rate limit exceeded'}, status=429)

    # Process request
    return JsonResponse({'status': 'ok'})
```

### Distributed Locks

```python
from django_extensions.redis_cache import distributed_lock

with distributed_lock('my-resource', timeout=30):
    # Only one process can execute this at a time
    perform_critical_operation()
```

### Cache Decorator

```python
from django_extensions.redis_cache import cached

@cached(ttl=3600, key_prefix='expensive')
def expensive_computation(x, y):
    return x ** y
```

### Pub/Sub

```python
from django_extensions.redis_cache import publish, subscribe

# Publish message
publish('channel:notifications', {'event': 'new_order', 'order_id': 123})

# Subscribe
for message in subscribe('channel:notifications'):
    print(f"Received: {message}")
```

### RedisClient Class

```python
from django_extensions.redis_cache import RedisClient

client = RedisClient()

# Atomic increment
count = client.incr('page_views')

# Set with expiration
client.setex('session:abc', 3600, 'data')

# Hash operations
client.hset('user:123', 'name', 'John')
client.hget('user:123', 'name')

# List operations
client.lpush('queue', 'task1')
task = client.rpop('queue')
```

## License

MIT
