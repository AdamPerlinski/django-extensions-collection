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
