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

