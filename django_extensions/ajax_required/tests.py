"""Tests for ajax_required decorator."""

import pytest
import json
from django.test import RequestFactory
from django.http import HttpResponse, JsonResponse

from .decorators import ajax_required, is_ajax


class TestIsAjax:
    """Test cases for is_ajax function."""

    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    def test_not_ajax(self, request_factory):
        """Test regular request is not AJAX."""
        request = request_factory.get('/')
        assert is_ajax(request) is False

    def test_x_requested_with(self, request_factory):
        """Test X-Requested-With header detection."""
        request = request_factory.get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert is_ajax(request) is True

    def test_accept_json(self, request_factory):
        """Test Accept header detection."""
        request = request_factory.get('/', HTTP_ACCEPT='application/json')
        assert is_ajax(request) is True

    def test_accept_json_with_other(self, request_factory):
        """Test Accept header with multiple types."""
        request = request_factory.get('/', HTTP_ACCEPT='text/html, application/json')
        assert is_ajax(request) is True


class TestAjaxRequiredDecorator:
    """Test cases for ajax_required decorator."""

    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    def test_ajax_request_allowed(self, request_factory):
        """Test AJAX request passes through."""
        @ajax_required
        def view(request):
            return HttpResponse('OK')

        request = request_factory.get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = view(request)

        assert response.status_code == 200
        assert response.content == b'OK'

    def test_non_ajax_blocked(self, request_factory):
        """Test non-AJAX request is blocked."""
        @ajax_required
        def view(request):
            return HttpResponse('OK')

        request = request_factory.get('/')
        response = view(request)

        assert response.status_code == 400

    def test_json_error_response(self, request_factory):
        """Test JSON error response."""
        @ajax_required
        def view(request):
            return HttpResponse('OK')

        request = request_factory.get('/')
        response = view(request)

        data = json.loads(response.content)
        assert 'error' in data

    def test_non_json_error(self, request_factory):
        """Test non-JSON error response."""
        @ajax_required(json_error=False)
        def view(request):
            return HttpResponse('OK')

        request = request_factory.get('/')
        response = view(request)

        assert response.status_code == 400
        assert b'AJAX' in response.content

    def test_custom_error_response(self, request_factory):
        """Test custom error response."""
        custom_response = HttpResponse('Custom Error', status=403)

        @ajax_required(error_response=custom_response)
        def view(request):
            return HttpResponse('OK')

        request = request_factory.get('/')
        response = view(request)

        assert response.status_code == 403
        assert response.content == b'Custom Error'

    def test_decorator_with_arguments(self, request_factory):
        """Test decorator with arguments on view with arguments."""
        @ajax_required
        def view(request, pk):
            return HttpResponse(f'Item {pk}')

        request = request_factory.get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = view(request, pk=123)

        assert response.content == b'Item 123'

    def test_decorator_preserves_function_name(self):
        """Test decorator preserves function metadata."""
        @ajax_required
        def my_view(request):
            """My view docstring."""
            pass

        assert my_view.__name__ == 'my_view'
        assert my_view.__doc__ == 'My view docstring.'
