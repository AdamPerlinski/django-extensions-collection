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
