"""Tests for superuser_required decorator."""

import pytest
from django.test import RequestFactory
from django.http import HttpResponse
from django.contrib.auth.models import AnonymousUser
from unittest.mock import MagicMock

from .decorators import superuser_required, staff_required


class TestSuperuserRequiredDecorator:
    """Test cases for superuser_required decorator."""

    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    @pytest.fixture
    def anonymous_request(self, request_factory):
        request = request_factory.get('/admin/')
        request.user = AnonymousUser()
        return request

    @pytest.fixture
    def regular_user_request(self, request_factory):
        request = request_factory.get('/admin/')
        user = MagicMock()
        user.is_authenticated = True
        user.is_superuser = False
        request.user = user
        return request

    @pytest.fixture
    def superuser_request(self, request_factory):
        request = request_factory.get('/admin/')
        user = MagicMock()
        user.is_authenticated = True
        user.is_superuser = True
        request.user = user
        return request

    def test_superuser_allowed(self, superuser_request):
        """Test superuser can access view."""
        @superuser_required
        def view(request):
            return HttpResponse('OK')

        response = view(superuser_request)

        assert response.status_code == 200
        assert response.content == b'OK'

    def test_anonymous_redirected(self, anonymous_request):
        """Test anonymous user is redirected."""
        @superuser_required
        def view(request):
            return HttpResponse('OK')

        response = view(anonymous_request)

        assert response.status_code == 302

    def test_regular_user_forbidden(self, regular_user_request):
