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

        assert hasattr(page_obj, 'page_range')
        assert isinstance(page_obj.page_range, list)


class TestGetPageRange:
    """Test cases for get_page_range function."""

    @pytest.fixture
    def create_page_obj(self):
        """Create a mock page object."""
        def _create(current_page, total_pages):
            page_obj = MagicMock()
            page_obj.number = current_page
            page_obj.paginator.num_pages = total_pages
            return page_obj
        return _create

    def test_middle_page(self, create_page_obj):
        """Test range for middle page."""
        page_obj = create_page_obj(5, 10)
        page_range = get_page_range(page_obj, window=2)

        assert page_range == [3, 4, 5, 6, 7]

    def test_first_page(self, create_page_obj):
        """Test range for first page."""
        page_obj = create_page_obj(1, 10)
        page_range = get_page_range(page_obj, window=2)

        assert 1 in page_range
        assert len(page_range) == 5

    def test_last_page(self, create_page_obj):
        """Test range for last page."""
        page_obj = create_page_obj(10, 10)
        page_range = get_page_range(page_obj, window=2)

        assert 10 in page_range
        assert len(page_range) == 5

    def test_small_paginator(self, create_page_obj):
        """Test range for small paginator."""
        page_obj = create_page_obj(2, 3)
        page_range = get_page_range(page_obj, window=3)

        assert page_range == [1, 2, 3]


class TestGetPaginationQueryString:
    """Test cases for get_pagination_query_string function."""

    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    def test_no_params(self, request_factory):
        """Test with no query parameters."""
        request = request_factory.get('/')
        qs = get_pagination_query_string(request)
        assert qs == ''

    def test_with_params(self, request_factory):
        """Test with other query parameters."""
        request = request_factory.get('/', {'sort': 'name', 'filter': 'active'})
        qs = get_pagination_query_string(request)

        assert 'sort=name' in qs
        assert 'filter=active' in qs

    def test_excludes_page_param(self, request_factory):
        """Test page parameter is excluded."""
        request = request_factory.get('/', {'page': '5', 'sort': 'name'})
        qs = get_pagination_query_string(request)

        assert 'page=' not in qs
        assert 'sort=name' in qs


class TestEnhancedPaginator:
    """Test cases for EnhancedPaginator."""

    def test_get_page_info(self):
        """Test get_page_info method."""
        items = list(range(1, 51))  # 50 items
        paginator = EnhancedPaginator(items, 10)

        info = paginator.get_page_info(3)

        assert info['page'].number == 3
        assert info['has_previous'] is True
        assert info['has_next'] is True
        assert info['previous_page'] == 2
        assert info['next_page'] == 4
        assert info['total_count'] == 50
        assert info['total_pages'] == 5

    def test_first_page_info(self):
        """Test get_page_info for first page."""
        items = list(range(1, 51))
        paginator = EnhancedPaginator(items, 10)

        info = paginator.get_page_info(1)

        assert info['has_previous'] is False
        assert info['previous_page'] is None

    def test_last_page_info(self):
        """Test get_page_info for last page."""
        items = list(range(1, 51))
        paginator = EnhancedPaginator(items, 10)

        info = paginator.get_page_info(5)

        assert info['has_next'] is False
        assert info['next_page'] is None
