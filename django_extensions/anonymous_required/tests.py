"""Tests for anonymous_required decorator."""

import pytest
from django.test import RequestFactory
from django.http import HttpResponse
from django.contrib.auth.models import AnonymousUser
from unittest.mock import MagicMock

from .decorators import anonymous_required


class TestAnonymousRequiredDecorator:
    """Test cases for anonymous_required decorator."""

    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    @pytest.fixture
    def anonymous_request(self, request_factory):
        request = request_factory.get('/')
        request.user = AnonymousUser()
        return request

    @pytest.fixture
    def authenticated_request(self, request_factory):
        request = request_factory.get('/')
        user = MagicMock()
        user.is_authenticated = True
        request.user = user
        return request

    def test_anonymous_allowed(self, anonymous_request):
        """Test anonymous user can access view."""
        @anonymous_required
        def view(request):
            return HttpResponse('OK')

        response = view(anonymous_request)

        assert response.status_code == 200
        assert response.content == b'OK'

    def test_authenticated_redirected(self, authenticated_request):
        """Test authenticated user is redirected."""
        @anonymous_required
        def view(request):
            return HttpResponse('OK')

        response = view(authenticated_request)

        assert response.status_code == 302

    def test_custom_redirect_url(self, authenticated_request):
        """Test custom redirect URL."""
        @anonymous_required(redirect_url='/dashboard/')
        def view(request):
            return HttpResponse('OK')

        response = view(authenticated_request)

        assert response.status_code == 302
        assert response.url == '/dashboard/'

    def test_decorator_with_arguments(self, anonymous_request):
        """Test decorator with view arguments."""
        @anonymous_required
        def view(request, pk):
            return HttpResponse(f'Item {pk}')

        response = view(anonymous_request, pk=123)

        assert response.content == b'Item 123'

    def test_decorator_preserves_function_name(self):
        """Test decorator preserves function metadata."""
        @anonymous_required
        def my_view(request):
            """My view docstring."""
            pass

        assert my_view.__name__ == 'my_view'
        assert my_view.__doc__ == 'My view docstring.'

    def test_decorator_without_parentheses(self, anonymous_request):
        """Test decorator can be used without parentheses."""
        @anonymous_required
        def view(request):
            return HttpResponse('OK')

        response = view(anonymous_request)
        assert response.status_code == 200

    def test_decorator_with_parentheses(self, anonymous_request):
        """Test decorator can be used with parentheses."""
        @anonymous_required()
        def view(request):
            return HttpResponse('OK')

        response = view(anonymous_request)
        assert response.status_code == 200
