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

