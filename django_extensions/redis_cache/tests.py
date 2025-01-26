"""Tests for Redis Cache Utilities."""

import pytest
from unittest.mock import MagicMock, patch

from .cache import (
    RedisClient,
    cache_get,
    cache_set,
    cache_delete,
    cache_exists,
    rate_limit,
    distributed_lock,
    cached,
)


class TestRedisClient:
    """Test cases for RedisClient."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.REDIS_URL = 'redis://localhost:6379/0'
        return settings

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        mock = MagicMock()
        return mock

    @pytest.fixture
    def client(self, mock_settings, mock_redis):
        """Create RedisClient with mocked Redis."""
        with patch('django_extensions.redis_cache.cache.get_redis', return_value=mock_redis):
            c = RedisClient()
            c._client = mock_redis
            return c

    def test_get_string(self, client, mock_redis):
        """Test getting a string value."""
        mock_redis.get.return_value = 'hello'

        result = client.get('key')

        assert result == 'hello'

    def test_get_json(self, client, mock_redis):
        """Test getting a JSON value."""
        mock_redis.get.return_value = '{"name": "John"}'

        result = client.get('key')

        assert result == {'name': 'John'}

    def test_get_default(self, client, mock_redis):
        """Test get with default value."""
        mock_redis.get.return_value = None

        result = client.get('key', default='default')

        assert result == 'default'

    def test_set_string(self, client, mock_redis):
        """Test setting a string value."""
        client.set('key', 'value')

        mock_redis.set.assert_called_with('key', 'value')

    def test_set_dict(self, client, mock_redis):
        """Test setting a dict value."""
        client.set('key', {'name': 'John'})

        mock_redis.set.assert_called_with('key', '{"name": "John"}')

    def test_set_with_ttl(self, client, mock_redis):
        """Test setting with TTL."""
        client.set('key', 'value', ttl=3600)

        mock_redis.setex.assert_called_with('key', 3600, 'value')

    def test_delete(self, client, mock_redis):
        """Test deleting a key."""
        client.delete('key')

        mock_redis.delete.assert_called_with('key')

    def test_exists(self, client, mock_redis):
        """Test checking if key exists."""
        mock_redis.exists.return_value = 1

        result = client.exists('key')

        assert result is True

    def test_incr(self, client, mock_redis):
        """Test incrementing a value."""
        mock_redis.incr.return_value = 6

        result = client.incr('counter')

        assert result == 6
        mock_redis.incr.assert_called_with('counter', 1)

    def test_prefix(self, mock_settings, mock_redis):
        """Test key prefix."""
        with patch('django_extensions.redis_cache.cache.get_redis', return_value=mock_redis):
            client = RedisClient(prefix='myapp')
            client._client = mock_redis

            client.set('key', 'value')

            mock_redis.set.assert_called_with('myapp:key', 'value')

    def test_hset_hget(self, client, mock_redis):
        """Test hash operations."""
        mock_redis.hget.return_value = '{"value": 1}'

        client.hset('hash', 'field', {'value': 1})
        result = client.hget('hash', 'field')

        assert result == {'value': 1}

    def test_hgetall(self, client, mock_redis):
        """Test getting all hash fields."""
        mock_redis.hgetall.return_value = {
            'field1': '{"a": 1}',
            'field2': 'plain'
        }

        result = client.hgetall('hash')

        assert result == {'field1': {'a': 1}, 'field2': 'plain'}

    def test_lpush_lpop(self, client, mock_redis):
        """Test list operations."""
        mock_redis.lpop.return_value = '{"id": 1}'

        client.lpush('list', {'id': 1})
        result = client.lpop('list')

        assert result == {'id': 1}

    def test_lrange(self, client, mock_redis):
        """Test list range."""
        mock_redis.lrange.return_value = ['{"id": 1}', 'plain']

        result = client.lrange('list', 0, -1)

        assert result == [{'id': 1}, 'plain']

    def test_sadd_smembers(self, client, mock_redis):
        """Test set operations."""
        mock_redis.smembers.return_value = {'a', 'b', 'c'}

        client.sadd('set', 'a', 'b', 'c')
        result = client.smembers('set')

        assert result == {'a', 'b', 'c'}

    def test_publish(self, client, mock_redis):
        """Test publishing message."""
        client.publish('channel', {'event': 'test'})

        mock_redis.publish.assert_called_with('channel', '{"event": "test"}')


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.REDIS_URL = 'redis://localhost:6379/0'
        return settings

    def test_cache_get(self, mock_settings):
        """Test cache_get function."""
        with patch('django_extensions.redis_cache.cache.get_redis') as mock_get:
            mock_redis = MagicMock()
            mock_redis.get.return_value = '"value"'
            mock_get.return_value = mock_redis

            result = cache_get('key')

            assert result == 'value'

    def test_cache_set(self, mock_settings):
        """Test cache_set function."""
        with patch('django_extensions.redis_cache.cache.get_redis') as mock_get:
            mock_redis = MagicMock()
            mock_get.return_value = mock_redis

            cache_set('key', 'value', ttl=3600)

            mock_redis.setex.assert_called()

    def test_cache_delete(self, mock_settings):
        """Test cache_delete function."""
        with patch('django_extensions.redis_cache.cache.get_redis') as mock_get:
            mock_redis = MagicMock()
            mock_get.return_value = mock_redis

            cache_delete('key')

            mock_redis.delete.assert_called()


class TestRateLimiting:
    """Test rate limiting."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.REDIS_URL = 'redis://localhost:6379/0'
        return settings

    def test_rate_limit_first_request(self, mock_settings):
        """Test first request within limit."""
        with patch('django_extensions.redis_cache.cache.get_redis') as mock_get:
            mock_redis = MagicMock()
            mock_redis.get.return_value = None
            mock_get.return_value = mock_redis

            result = rate_limit('key', limit=100, window=60)

            assert result is True
            mock_redis.setex.assert_called_with('key', 60, 1)

    def test_rate_limit_within_limit(self, mock_settings):
        """Test request within limit."""
        with patch('django_extensions.redis_cache.cache.get_redis') as mock_get:
            mock_redis = MagicMock()
            mock_redis.get.return_value = '50'
            mock_get.return_value = mock_redis

            result = rate_limit('key', limit=100, window=60)

            assert result is True
            mock_redis.incr.assert_called_with('key')

    def test_rate_limit_exceeded(self, mock_settings):
        """Test rate limit exceeded."""
        with patch('django_extensions.redis_cache.cache.get_redis') as mock_get:
            mock_redis = MagicMock()
            mock_redis.get.return_value = '100'
            mock_get.return_value = mock_redis

            result = rate_limit('key', limit=100, window=60)

            assert result is False


class TestDistributedLock:
    """Test distributed locking."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.REDIS_URL = 'redis://localhost:6379/0'
        return settings

    def test_lock_acquired(self, mock_settings):
        """Test lock is acquired."""
        with patch('django_extensions.redis_cache.cache.get_redis') as mock_get:
            mock_redis = MagicMock()
            mock_redis.set.return_value = True
            mock_redis.get.return_value = None
            mock_get.return_value = mock_redis

            with distributed_lock('resource', blocking=False) as acquired:
                assert acquired is True

    def test_lock_not_acquired(self, mock_settings):
        """Test lock not acquired."""
        with patch('django_extensions.redis_cache.cache.get_redis') as mock_get:
            mock_redis = MagicMock()
            mock_redis.set.return_value = False
            mock_get.return_value = mock_redis

            with distributed_lock('resource', blocking=False) as acquired:
                assert acquired is False


class TestCachedDecorator:
    """Test cached decorator."""

    @pytest.fixture
    def mock_settings(self, settings):
        """Configure test settings."""
        settings.REDIS_URL = 'redis://localhost:6379/0'
        return settings

    def test_cached_first_call(self, mock_settings):
        """Test first call computes and caches."""
        with patch('django_extensions.redis_cache.cache.get_redis') as mock_get:
            mock_redis = MagicMock()
            mock_redis.get.return_value = None
            mock_get.return_value = mock_redis

            @cached(ttl=300)
            def compute(x):
                return x * 2

            result = compute(5)

            assert result == 10
            mock_redis.setex.assert_called()

    def test_cached_second_call(self, mock_settings):
        """Test second call uses cache."""
        with patch('django_extensions.redis_cache.cache.get_redis') as mock_get:
            mock_redis = MagicMock()
            mock_redis.get.return_value = '10'
            mock_get.return_value = mock_redis

            call_count = 0

            @cached(ttl=300)
            def compute(x):
                nonlocal call_count
                call_count += 1
                return x * 2

            result = compute(5)

            assert result == 10
            assert call_count == 0  # Function not called
