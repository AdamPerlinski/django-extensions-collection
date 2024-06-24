# Superuser Required Decorator

Restrict views to superusers only.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.superuser_required',
]
```

## Usage

```python
from django_extensions.superuser_required import superuser_required

@superuser_required
def admin_dashboard(request):
    return render(request, 'admin/dashboard.html')
```

## Response

Non-superusers receive:
- Redirect to login page (if not authenticated)
- 403 Forbidden (if authenticated but not superuser)

## Class-Based Views

```python
from django.utils.decorators import method_decorator
from django.views import View

@method_decorator(superuser_required, name='dispatch')
class AdminView(View):
    def get(self, request):
        return render(request, 'admin/panel.html')
```

## Custom Redirect

```python
@superuser_required(login_url='/admin/login/')
def admin_view(request):
    return render(request, 'admin/view.html')
```

## Custom 403 Response

```python
@superuser_required(raise_exception=True)
def admin_view(request):
    # Raises PermissionDenied instead of redirecting
    return render(request, 'admin/view.html')
```

## With Permission Check

```python
from django_extensions.superuser_required import superuser_required

@superuser_required
def delete_user(request, user_id):
    # Only superusers can delete users
    User.objects.get(pk=user_id).delete()
    return redirect('/users/')
```

## Difference from staff_member_required

| Decorator | Requires |
|-----------|----------|
| `login_required` | Any authenticated user |
| `staff_member_required` | `is_staff=True` |
| `superuser_required` | `is_superuser=True` |

## Template Check

```django
{% if user.is_superuser %}
    <a href="{% url 'admin_panel' %}">Admin Panel</a>
{% endif %}
```

## Combining Decorators

```python
@login_required
@superuser_required
def super_admin_view(request):
    # login_required first, then superuser check
    pass
```

## License

MIT
