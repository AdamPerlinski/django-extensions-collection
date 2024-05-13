# Timezone Middleware

Activate per-user timezone for requests.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.timezone_middleware',
]

MIDDLEWARE = [
    ...
    'django_extensions.timezone_middleware.TimezoneMiddleware',
]
```

## Usage

The middleware activates user timezone from:
1. User profile timezone field
2. Session timezone
3. Cookie timezone
4. Default timezone

## User Model Setup

```python
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        choices=[(tz, tz) for tz in pytz.common_timezones]
    )
```

## Session-Based Timezone

```python
def set_timezone(request):
    if request.method == 'POST':
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('/')
```

## Template Form

```django
{% load tz %}

<form method="post" action="{% url 'set_timezone' %}">
    {% csrf_token %}
    <select name="timezone">
        {% for tz in timezones %}
            <option value="{{ tz }}" {% if tz == current_tz %}selected{% endif %}>
                {{ tz }}
            </option>
        {% endfor %}
    </select>
    <button type="submit">Set Timezone</button>
</form>

<p>Current time: {% localtime on %}{{ now }}{% endlocaltime %}</p>
```

## Configuration

```python
# settings.py

# Field name on user model
TIMEZONE_USER_FIELD = 'timezone'

# Session key
TIMEZONE_SESSION_KEY = 'django_timezone'

# Cookie name
TIMEZONE_COOKIE_NAME = 'user_timezone'

# Default timezone
TIME_ZONE = 'UTC'
USE_TZ = True
```

## Priority Order

1. Authenticated user's timezone field
2. Session value
3. Cookie value
4. `settings.TIME_ZONE`

## License

MIT
