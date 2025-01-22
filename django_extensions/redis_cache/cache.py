"""
Redis Cache Utilities for Django.

Usage:
    # settings.py
    REDIS_URL = 'redis://localhost:6379/0'
    # or
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 0

    # Basic usage
    from django_extensions.redis_cache import cache_get, cache_set

    cache_set('user:123', {'name': 'John'}, ttl=3600)
    user = cache_get('user:123')

    # Rate limiting
    from django_extensions.redis_cache import rate_limit

    if rate_limit('api:user:123', limit=100, window=60):
        # Allow request
    else:
        # Rate limited

    # Distributed lock
    from django_extensions.redis_cache import distributed_lock

    with distributed_lock('resource:123'):
        # Only one process can execute this at a time
"""

import json
import time
import uuid
from functools import wraps
from contextlib import contextmanager
from django.conf import settings


def get_redis():
    """Get Redis connection from settings."""
    try:
        import redis
    except ImportError:
        raise ImportError("redis is required. Install it with: pip install redis")

    url = getattr(settings, 'REDIS_URL', None)

    if url:
        return redis.from_url(url)

    return redis.Redis(
        host=getattr(settings, 'REDIS_HOST', 'localhost'),
        port=getattr(settings, 'REDIS_PORT', 6379),
        db=getattr(settings, 'REDIS_DB', 0),
        password=getattr(settings, 'REDIS_PASSWORD', None),
        decode_responses=True,
    )


class RedisClient:
    """
    Redis client wrapper with convenient methods.

    Usage:
        client = RedisClient()
        client.set('key', 'value', ttl=3600)
        value = client.get('key')
    """

    def __init__(self, redis_url=None, prefix=''):
        self._client = None
        self._url = redis_url
        self.prefix = prefix

    @property
    def client(self):
        if self._client is None:
            if self._url:
                try:
                    import redis
                except ImportError:
                    raise ImportError("redis is required. Install it with: pip install redis")
                self._client = redis.from_url(self._url, decode_responses=True)
            else:
                self._client = get_redis()
        return self._client

    def _key(self, key):
        """Add prefix to key."""
        if self.prefix:
            return f"{self.prefix}:{key}"
        return key

    def get(self, key, default=None):
        """Get a value from Redis."""
        value = self.client.get(self._key(key))
        if value is None:
            return default
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    def set(self, key, value, ttl=None):
        """Set a value in Redis."""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        if ttl:
            self.client.setex(self._key(key), ttl, value)
        else:
            self.client.set(self._key(key), value)

    def delete(self, key):
        """Delete a key."""
        self.client.delete(self._key(key))

    def exists(self, key):
        """Check if key exists."""
        return bool(self.client.exists(self._key(key)))

    def incr(self, key, amount=1):
        """Increment a value."""
        return self.client.incr(self._key(key), amount)

    def decr(self, key, amount=1):
        """Decrement a value."""
        return self.client.decr(self._key(key), amount)

    def expire(self, key, ttl):
        """Set expiration on a key."""
        self.client.expire(self._key(key), ttl)

    def ttl(self, key):
        """Get TTL of a key."""
        return self.client.ttl(self._key(key))

    def keys(self, pattern='*'):
        """Get keys matching pattern."""
        full_pattern = self._key(pattern)
        keys = self.client.keys(full_pattern)
        if self.prefix:
            prefix_len = len(self.prefix) + 1
            return [k[prefix_len:] for k in keys]
        return keys

    def flush(self):
        """Delete all keys with the prefix."""
        if self.prefix:
            keys = self.client.keys(f"{self.prefix}:*")
            if keys:
                self.client.delete(*keys)
        else:
            self.client.flushdb()

    # Hash operations
    def hget(self, name, key):
        """Get hash field."""
        value = self.client.hget(self._key(name), key)
        if value:
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        return None

    def hset(self, name, key, value):
        """Set hash field."""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        self.client.hset(self._key(name), key, value)

    def hgetall(self, name):
        """Get all hash fields."""
        data = self.client.hgetall(self._key(name))
        result = {}
        for k, v in data.items():
            try:
                result[k] = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                result[k] = v
        return result

    def hdel(self, name, *keys):
        """Delete hash fields."""
        self.client.hdel(self._key(name), *keys)

    # List operations
    def lpush(self, key, *values):
        """Push to left of list."""
        serialized = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in values]
        self.client.lpush(self._key(key), *serialized)

    def rpush(self, key, *values):
        """Push to right of list."""
        serialized = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in values]
        self.client.rpush(self._key(key), *serialized)

    def lpop(self, key):
        """Pop from left of list."""
        value = self.client.lpop(self._key(key))
        if value:
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        return None

    def rpop(self, key):
        """Pop from right of list."""
        value = self.client.rpop(self._key(key))
        if value:
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        return None

    def lrange(self, key, start=0, end=-1):
        """Get list range."""
        values = self.client.lrange(self._key(key), start, end)
        result = []
        for v in values:
            try:
                result.append(json.loads(v))
            except (json.JSONDecodeError, TypeError):
                result.append(v)
        return result

    def llen(self, key):
        """Get list length."""
        return self.client.llen(self._key(key))

    # Set operations
    def sadd(self, key, *values):
        """Add to set."""
        self.client.sadd(self._key(key), *values)

    def srem(self, key, *values):
        """Remove from set."""
        self.client.srem(self._key(key), *values)

    def smembers(self, key):
        """Get all set members."""
        return self.client.smembers(self._key(key))

    def sismember(self, key, value):
        """Check set membership."""
        return self.client.sismember(self._key(key), value)

    # Pub/Sub
    def publish(self, channel, message):
        """Publish message to channel."""
        if isinstance(message, (dict, list)):
            message = json.dumps(message)
        self.client.publish(self._key(channel), message)

    def subscribe(self, *channels):
        """Subscribe to channels."""
        pubsub = self.client.pubsub()
        pubsub.subscribe(*[self._key(c) for c in channels])
        return pubsub


# Convenience functions

def cache_get(key, default=None):
    """Get a value from cache."""
    client = RedisClient()
    return client.get(key, default)


def cache_set(key, value, ttl=None):
    """Set a value in cache."""
    client = RedisClient()
    client.set(key, value, ttl=ttl)


def cache_delete(key):
    """Delete from cache."""
    client = RedisClient()
    client.delete(key)


def cache_exists(key):
    """Check if key exists in cache."""
    client = RedisClient()
    return client.exists(key)


def rate_limit(key, limit=100, window=60):
    """
    Check if request is within rate limit.

    Args:
        key: Unique identifier (e.g., 'api:user:123')
        limit: Maximum requests allowed
        window: Time window in seconds

    Returns:
        bool: True if within limit, False if rate limited
    """
    client = RedisClient()
    redis_client = client.client

    current = redis_client.get(key)

    if current is None:
        redis_client.setex(key, window, 1)
        return True

    if int(current) >= limit:
        return False

    redis_client.incr(key)
    return True


def rate_limit_remaining(key, limit=100, window=60):
    """
    Get remaining requests in rate limit.

    Returns:
        int: Remaining requests, or limit if key doesn't exist
    """
    client = RedisClient()
    current = client.client.get(key)

    if current is None:
        return limit

    return max(0, limit - int(current))


@contextmanager
def distributed_lock(name, timeout=10, blocking=True, sleep=0.1):
    """
    Distributed lock using Redis.

    Args:
        name: Lock name
        timeout: Lock timeout in seconds
        blocking: Whether to wait for lock
        sleep: Sleep time between retries

    Yields:
        bool: True if lock acquired
    """
    client = RedisClient()
    redis_client = client.client
    lock_key = f"lock:{name}"
    lock_value = str(uuid.uuid4())

    acquired = False
    try:
        if blocking:
            while not acquired:
                acquired = redis_client.set(
                    lock_key, lock_value, nx=True, ex=timeout
                )
                if not acquired:
                    time.sleep(sleep)
        else:
            acquired = redis_client.set(
                lock_key, lock_value, nx=True, ex=timeout
            )

        yield acquired
    finally:
        if acquired:
            # Only release if we own the lock
            if redis_client.get(lock_key) == lock_value:
                redis_client.delete(lock_key)


def cached(ttl=3600, key_prefix='cache'):
    """
    Decorator to cache function results.

    Args:
        ttl: Cache TTL in seconds
        key_prefix: Prefix for cache keys

    Usage:
        @cached(ttl=300)
        def expensive_function(arg1, arg2):
            return compute_something(arg1, arg2)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"

            client = RedisClient()
            result = client.get(cache_key)

            if result is not None:
                return result

            result = func(*args, **kwargs)
            client.set(cache_key, result, ttl=ttl)
            return result
        return wrapper
    return decorator
