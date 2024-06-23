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
        """Test regular user gets 403."""
        @superuser_required
        def view(request):
            return HttpResponse('OK')

        response = view(regular_user_request)

        assert response.status_code == 403

    def test_raise_exception_anonymous(self, anonymous_request):
        """Test raise_exception for anonymous user."""
        @superuser_required(raise_exception=True)
        def view(request):
            return HttpResponse('OK')

        response = view(anonymous_request)

        assert response.status_code == 403
        assert b'Authentication' in response.content

    def test_raise_exception_regular(self, regular_user_request):
        """Test raise_exception for regular user."""
        @superuser_required(raise_exception=True)
        def view(request):
            return HttpResponse('OK')

        response = view(regular_user_request)

        assert response.status_code == 403
        assert b'Superuser' in response.content

    def test_custom_login_url(self, anonymous_request):
        """Test custom login URL."""
        @superuser_required(login_url='/custom/login/')
        def view(request):
            return HttpResponse('OK')

        response = view(anonymous_request)

        assert response.status_code == 302
        assert '/custom/login/' in response.url

    def test_decorator_preserves_function_name(self):
        """Test decorator preserves function metadata."""
        @superuser_required
        def my_view(request):
            """My view docstring."""
            pass

        assert my_view.__name__ == 'my_view'


class TestStaffRequiredDecorator:
    """Test cases for staff_required decorator."""

    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    @pytest.fixture
    def staff_request(self, request_factory):
        request = request_factory.get('/admin/')
        user = MagicMock()
        user.is_authenticated = True
        user.is_staff = True
        request.user = user
        return request

    @pytest.fixture
    def non_staff_request(self, request_factory):
        request = request_factory.get('/admin/')
        user = MagicMock()
        user.is_authenticated = True
        user.is_staff = False
        request.user = user
        return request

    def test_staff_allowed(self, staff_request):
        """Test staff member can access view."""
        @staff_required
        def view(request):
            return HttpResponse('OK')

        response = view(staff_request)

        assert response.status_code == 200

    def test_non_staff_forbidden(self, non_staff_request):
        """Test non-staff user gets 403."""
        @staff_required
        def view(request):
            return HttpResponse('OK')

        response = view(non_staff_request)

        assert response.status_code == 403
