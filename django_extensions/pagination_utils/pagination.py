"""
Pagination utilities - Enhanced pagination helpers.

Usage:
    from django_extensions.pagination_utils import paginate

    def my_view(request):
        items = Item.objects.all()
        page_obj = paginate(request, items, per_page=25)
        return render(request, 'items.html', {'page_obj': page_obj})
"""

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def paginate(request, queryset, per_page=25, page_param='page', orphans=0,
             allow_empty_first_page=True):
    """
    Paginate a queryset based on request parameters.

    Args:
        request: The HTTP request object.
        queryset: The queryset to paginate.
        per_page: Number of items per page.
        page_param: Query parameter name for the page number.
        orphans: Number of orphans allowed.
        allow_empty_first_page: Whether to allow empty first page.

    Returns:
        A Page object with additional convenience methods.
    """
    paginator = Paginator(
        queryset,
        per_page,
        orphans=orphans,
        allow_empty_first_page=allow_empty_first_page
    )

    page_number = request.GET.get(page_param, 1)

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    # Add convenience attributes
    page_obj.page_range = get_page_range(page_obj, window=3)
    page_obj.query_string = get_pagination_query_string(request, page_param)

    return page_obj


def get_page_range(page_obj, window=3):
    """
    Get a windowed page range around the current page.

    Args:
        page_obj: The Page object.
        window: Number of pages to show on each side.

    Returns:
        A list of page numbers to display.
    """
    current = page_obj.number
    total = page_obj.paginator.num_pages

    start = max(1, current - window)
    end = min(total, current + window)

    # Adjust window if at edges
    if current <= window:
        end = min(total, 2 * window + 1)
    if current > total - window:
        start = max(1, total - 2 * window)

    return list(range(start, end + 1))


def get_pagination_query_string(request, page_param='page'):
    """
    Get query string for pagination links, excluding the page parameter.

    Args:
        request: The HTTP request object.
        page_param: The page parameter name to exclude.

    Returns:
        Query string without the page parameter.
    """
    params = request.GET.copy()
    params.pop(page_param, None)

    if params:
        return '&' + params.urlencode()
    return ''


class EnhancedPaginator(Paginator):
    """Enhanced paginator with additional features."""

    def get_page_info(self, page_number):
        """
        Get detailed information about a page.

        Returns dict with:
            - page: The Page object
            - has_previous: Boolean
            - has_next: Boolean
            - previous_page: Previous page number or None
            - next_page: Next page number or None
            - start_index: First item index (1-based)
            - end_index: Last item index (1-based)
        """
        page = self.get_page(page_number)

        return {
            'page': page,
            'has_previous': page.has_previous(),
            'has_next': page.has_next(),
            'previous_page': page.previous_page_number() if page.has_previous() else None,
            'next_page': page.next_page_number() if page.has_next() else None,
            'start_index': page.start_index(),
            'end_index': page.end_index(),
            'total_count': self.count,
            'total_pages': self.num_pages,
        }


def cursor_paginate(queryset, cursor_field='id', cursor_value=None, limit=25, direction='forward'):
    """
    Cursor-based pagination for large datasets.

    Args:
        queryset: The queryset to paginate.
        cursor_field: Field to use for cursor.
        cursor_value: Current cursor value.
        limit: Number of items to return.
        direction: 'forward' or 'backward'.

    Returns:
        Dict with items, next_cursor, prev_cursor.
    """
    if direction == 'forward':
        if cursor_value:
            queryset = queryset.filter(**{f'{cursor_field}__gt': cursor_value})
        queryset = queryset.order_by(cursor_field)[:limit + 1]
    else:
        if cursor_value:
            queryset = queryset.filter(**{f'{cursor_field}__lt': cursor_value})
        queryset = queryset.order_by(f'-{cursor_field}')[:limit + 1]

    items = list(queryset)

    has_more = len(items) > limit
    if has_more:
        items = items[:limit]

    if direction == 'backward':
        items.reverse()

    return {
        'items': items,
        'has_next': has_more if direction == 'forward' else bool(cursor_value),
        'has_prev': bool(cursor_value) if direction == 'forward' else has_more,
        'next_cursor': getattr(items[-1], cursor_field, None) if items and has_more else None,
        'prev_cursor': getattr(items[0], cursor_field, None) if items else None,
    }
