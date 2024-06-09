# Ajax Required Decorator

Restrict views to AJAX requests only.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.ajax_required',
]
```

## Usage

```python
from django_extensions.ajax_required import ajax_required

@ajax_required
def api_endpoint(request):
    return JsonResponse({'status': 'ok'})
```

## Response

Non-AJAX requests receive:
- Status: 400 Bad Request
- Body: `{"error": "AJAX request required"}`

## Class-Based Views

```python
from django.utils.decorators import method_decorator
from django_extensions.ajax_required import ajax_required

class MyAPIView(View):
    @method_decorator(ajax_required)
    def post(self, request):
        return JsonResponse({'status': 'ok'})
```

## With Other Decorators

```python
from django.contrib.auth.decorators import login_required

@login_required
@ajax_required
def protected_api(request):
    return JsonResponse({'user': request.user.username})
```

## AJAX Detection

Checks for:
- `X-Requested-With: XMLHttpRequest` header
- `Accept: application/json` header

## Custom Error Response

```python
@ajax_required(error_message="This endpoint requires AJAX")
def api_endpoint(request):
    return JsonResponse({'status': 'ok'})
```

## Allow All in Debug

```python
@ajax_required(debug_bypass=True)
def api_endpoint(request):
    # Allows non-AJAX in DEBUG mode
    return JsonResponse({'status': 'ok'})
```

## JavaScript Example

```javascript
// Using fetch
fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({data: 'value'})
});

// Using jQuery
$.ajax({
    url: '/api/endpoint/',
    type: 'POST',
    data: {data: 'value'}
});
```

## License

MIT
