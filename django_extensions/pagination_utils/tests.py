"""Tests for pagination utilities."""

import pytest
from django.test import RequestFactory
from unittest.mock import MagicMock

from .pagination import (
    paginate,
    get_page_range,
    get_pagination_query_string,
    EnhancedPaginator,
)


class TestPaginate:
    """Test cases for paginate function."""

    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    @pytest.fixture
    def items(self):
        """Create mock queryset-like list."""
        return list(range(1, 101))  # 100 items

    def test_basic_pagination(self, request_factory, items):
        """Test basic pagination."""
        request = request_factory.get('/', {'page': '1'})
        page_obj = paginate(request, items, per_page=10)

        assert len(page_obj) == 10
        assert page_obj.number == 1
        assert page_obj.paginator.num_pages == 10

    def test_page_number(self, request_factory, items):
        """Test specific page number."""
        request = request_factory.get('/', {'page': '5'})
        page_obj = paginate(request, items, per_page=10)

        assert page_obj.number == 5

    def test_invalid_page_defaults_to_first(self, request_factory, items):
        """Test invalid page defaults to first page."""
        request = request_factory.get('/', {'page': 'invalid'})
        page_obj = paginate(request, items, per_page=10)

        assert page_obj.number == 1

    def test_out_of_range_page(self, request_factory, items):
        """Test out of range page goes to last page."""
        request = request_factory.get('/', {'page': '999'})
        page_obj = paginate(request, items, per_page=10)

        assert page_obj.number == 10

    def test_custom_per_page(self, request_factory, items):
        """Test custom per_page."""
        request = request_factory.get('/', {'page': '1'})
        page_obj = paginate(request, items, per_page=25)

        assert len(page_obj) == 25
        assert page_obj.paginator.num_pages == 4

    def test_custom_page_param(self, request_factory, items):
        """Test custom page parameter name."""
        request = request_factory.get('/', {'p': '2'})
        page_obj = paginate(request, items, per_page=10, page_param='p')

        assert page_obj.number == 2

    def test_page_range_attribute(self, request_factory, items):
        """Test page_range is added to page object."""
        request = request_factory.get('/', {'page': '5'})
        page_obj = paginate(request, items, per_page=10)

