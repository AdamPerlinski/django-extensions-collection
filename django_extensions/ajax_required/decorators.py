"""
ajax_required - Decorator to require AJAX requests.

Usage:
    from django_extensions.ajax_required import ajax_required

    @ajax_required
    def my_view(request):
        return JsonResponse({'data': 'value'})

    # With custom response
    @ajax_required(error_response=HttpResponseForbidden('AJAX only'))
    def my_view(request):
        ...
"""

from functools import wraps
from django.http import HttpResponseBadRequest, JsonResponse


def is_ajax(request):
    """Check if request is an AJAX request."""
