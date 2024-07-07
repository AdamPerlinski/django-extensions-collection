# Cache Decorator

Function result caching with Django's cache backend.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.cache_decorator',
]
```

## Usage

```python
from django_extensions.cache_decorator import cache_result

@cache_result(timeout=3600)
def expensive_calculation(x, y):
    # This result is cached for 1 hour
    return x ** y

result = expensive_calculation(2, 10)  # Calculated
result = expensive_calculation(2, 10)  # From cache
```

## Options

### Timeout

```python
@cache_result(timeout=60)  # 60 seconds
@cache_result(timeout=3600)  # 1 hour
@cache_result(timeout=86400)  # 1 day
@cache_result(timeout=None)  # Never expires
```

### Key Prefix

```python
@cache_result(timeout=3600, key_prefix='myapp')
def my_function():
    pass
# Cache key: myapp:my_function:...
```

### Custom Key Function

```python
def make_key(func, args, kwargs):
    return f"custom:{func.__name__}:{args[0]}"

@cache_result(timeout=3600, key_func=make_key)
def get_user_data(user_id):
    pass
```

### Cache Backend

```python
@cache_result(timeout=3600, cache='redis')
def my_function():
    pass
```

## Cache Key Generation

Default key format:
```
{prefix}:{function_name}:{hash(args, kwargs)}
```

## Invalidation

```python
from django_extensions.cache_decorator import invalidate_cache

# Invalidate specific call
invalidate_cache(expensive_calculation, 2, 10)

# Invalidate all for function
invalidate_cache(expensive_calculation, all=True)
```

## Method Caching

```python
class MyClass:
    @cache_result(timeout=3600, include_self=False)
    def instance_method(self, arg):
        pass
```

## Conditional Caching

```python
@cache_result(timeout=3600, condition=lambda result: result is not None)
def maybe_none():
    pass
```

## Debug Mode

```python
@cache_result(timeout=3600, debug=True)
def my_function():
    pass
# Logs cache hits/misses
```

## License

MIT
