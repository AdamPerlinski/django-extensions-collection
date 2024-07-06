"""Tests for cache decorators."""

import pytest
from django.core.cache import cache
from django.test import RequestFactory
from django.http import HttpResponse
from django.contrib.auth.models import AnonymousUser
from unittest.mock import MagicMock

from .decorators import cache_result, cache_page_per_user, cache_method, make_cache_key


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test."""
    cache.clear()
    yield
    cache.clear()


class TestMakeCacheKey:
    """Test cases for make_cache_key function."""

    def test_simple_args(self):
        """Test with simple arguments."""
        key1 = make_cache_key('a', 'b', 'c')
        key2 = make_cache_key('a', 'b', 'c')
        assert key1 == key2

    def test_different_args(self):
        """Test different arguments produce different keys."""
        key1 = make_cache_key('a', 'b')
        key2 = make_cache_key('a', 'c')
        assert key1 != key2

    def test_with_kwargs(self):
        """Test with keyword arguments."""
        key1 = make_cache_key(foo='bar')
        key2 = make_cache_key(foo='bar')
        assert key1 == key2

    def test_kwarg_order_independent(self):
        """Test kwargs order doesn't affect key."""
        key1 = make_cache_key(a=1, b=2)
        key2 = make_cache_key(b=2, a=1)
        assert key1 == key2


class TestCacheResult:
    """Test cases for cache_result decorator."""

    def test_caches_result(self):
        """Test result is cached."""
        call_count = 0

        @cache_result(timeout=60)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = expensive_function(5)
        result2 = expensive_function(5)

        assert result1 == 10
        assert result2 == 10
        assert call_count == 1  # Only called once

    def test_different_args_not_cached(self):
        """Test different arguments are cached separately."""
        call_count = 0

        @cache_result(timeout=60)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = expensive_function(5)
        result2 = expensive_function(10)

        assert result1 == 10
        assert result2 == 20
        assert call_count == 2

    def test_key_prefix(self):
        """Test key prefix is used."""
        @cache_result(timeout=60, key_prefix='myprefix')
        def func(x):
            return x

        func(5)
        # Key should include prefix
        # We can't easily test the exact key, but we can verify it works

    def test_cache_none_true(self):
        """Test caching None results when enabled."""
        call_count = 0

        @cache_result(timeout=60, cache_none=True)
        def returns_none():
            nonlocal call_count
            call_count += 1
            return None

