# Anonymous Required Decorator

Restrict views to unauthenticated users only.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.anonymous_required',
]
```

## Usage

```python
from django_extensions.anonymous_required import anonymous_required

@anonymous_required
def login_view(request):
    # Only accessible to logged-out users
    return render(request, 'login.html')

@anonymous_required
def register_view(request):
    # Redirect logged-in users
    return render(request, 'register.html')
```

## Default Behavior

Authenticated users are redirected to:
- `settings.LOGIN_REDIRECT_URL`
- Or `'/'` if not set

## Custom Redirect

```python
@anonymous_required(redirect_url='/dashboard/')
def login_view(request):
    return render(request, 'login.html')
```

## Response for AJAX

AJAX requests receive:
- Status: 403 Forbidden
- Body: `{"error": "Authentication not allowed"}`

```python
@anonymous_required(ajax_response=True)
def api_register(request):
    return JsonResponse({'status': 'ok'})
```

## Class-Based Views

```python
from django.utils.decorators import method_decorator
from django.views import View

@method_decorator(anonymous_required, name='dispatch')
class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        # Handle login
        pass
```

## Common Use Cases

- Login page
- Registration page
- Password reset request
- OAuth callbacks

## With Messages

```python
from django.contrib import messages

@anonymous_required(message="You are already logged in.")
def login_view(request):
    return render(request, 'login.html')
```

## Settings

```python
# settings.py
LOGIN_REDIRECT_URL = '/dashboard/'  # Where to redirect logged-in users
```

## License

MIT
