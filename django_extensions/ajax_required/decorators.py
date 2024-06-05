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
    # Modern way: Check Accept header
    if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
        return True

    # Legacy jQuery way: Check X-Requested-With header
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return True

    return False


def ajax_required(function=None, error_response=None, json_error=True):
    """
    Decorator that requires the request to be an AJAX request.

    Args:
        function: The view function to decorate.
        error_response: Custom response for non-AJAX requests.
        json_error: If True, return JSON error response.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not is_ajax(request):
                if error_response:
                    return error_response

                if json_error:
                    return JsonResponse(
                        {'error': 'This endpoint requires an AJAX request.'},
                        status=400
                    )

                return HttpResponseBadRequest('AJAX request required.')

            return view_func(request, *args, **kwargs)

        return wrapper

    if function:
        return decorator(function)

    return decorator
