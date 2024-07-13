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
