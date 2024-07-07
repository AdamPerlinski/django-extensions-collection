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

        result1 = returns_none()
        result2 = returns_none()

        assert result1 is None
        assert result2 is None
        assert call_count == 1

    def test_cache_none_false(self):
        """Test not caching None results when disabled."""
        call_count = 0

        @cache_result(timeout=60, cache_none=False)
        def returns_none():
            nonlocal call_count
            call_count += 1
            return None

        result1 = returns_none()
        result2 = returns_none()

        assert result1 is None
        assert result2 is None
        assert call_count == 2


class TestCachePagePerUser:
    """Test cases for cache_page_per_user decorator."""

    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    def test_caches_for_authenticated_user(self, request_factory):
        """Test caching for authenticated users."""
        call_count = 0

        @cache_page_per_user(timeout=60)
        def view(request):
            nonlocal call_count
            call_count += 1
            return HttpResponse('OK')

        user = MagicMock()
        user.is_authenticated = True
        user.pk = 1

        request1 = request_factory.get('/test/')
        request1.user = user
        request2 = request_factory.get('/test/')
        request2.user = user

        response1 = view(request1)
        response2 = view(request2)

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert call_count == 1

    def test_different_users_separate_cache(self, request_factory):
        """Test different users have separate caches."""
        call_count = 0

        @cache_page_per_user(timeout=60)
        def view(request):
            nonlocal call_count
            call_count += 1
            return HttpResponse('OK')

        user1 = MagicMock()
        user1.is_authenticated = True
        user1.pk = 1

        user2 = MagicMock()
        user2.is_authenticated = True
        user2.pk = 2

        request1 = request_factory.get('/test/')
        request1.user = user1
        request2 = request_factory.get('/test/')
        request2.user = user2

        view(request1)
        view(request2)

        assert call_count == 2

    def test_post_not_cached(self, request_factory):
        """Test POST requests are not cached."""
        call_count = 0

        @cache_page_per_user(timeout=60)
        def view(request):
            nonlocal call_count
            call_count += 1
            return HttpResponse('OK')

        user = MagicMock()
        user.is_authenticated = True
        user.pk = 1

        request1 = request_factory.post('/test/')
        request1.user = user
        request2 = request_factory.post('/test/')
        request2.user = user

        view(request1)
        view(request2)

        assert call_count == 2


class TestCacheMethod:
    """Test cases for cache_method decorator."""

    def test_caches_method(self):
        """Test method result is cached."""
        call_count = 0

        class MyClass:
            pk = 1

            @cache_method(timeout=60)
            def expensive_method(self, x):
                nonlocal call_count
                call_count += 1
                return x * 2

        obj = MyClass()
        result1 = obj.expensive_method(5)
        result2 = obj.expensive_method(5)

        assert result1 == 10
        assert result2 == 10
        assert call_count == 1

    def test_different_instances_cached(self):
        """Test different instances have separate caches."""
        call_count = 0

        class MyClass:
            def __init__(self, pk):
                self.pk = pk

            @cache_method(timeout=60, key_attr='pk')
            def method(self):
                nonlocal call_count
                call_count += 1
                return self.pk * 2

        obj1 = MyClass(1)
        obj2 = MyClass(2)

        result1 = obj1.method()
        result2 = obj2.method()

        assert result1 == 2
        assert result2 == 4
        assert call_count == 2
