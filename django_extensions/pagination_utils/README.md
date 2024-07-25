# Pagination Utils

Enhanced pagination utilities for Django.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.pagination_utils',
]
```

## Usage

### Basic Pagination

```python
from django_extensions.pagination_utils import Paginator

items = list(range(1, 101))  # 100 items
paginator = Paginator(items, per_page=10)

page = paginator.page(1)
print(page.object_list)    # [1, 2, 3, ..., 10]
print(page.has_next())     # True
print(page.has_previous()) # False
print(page.number)         # 1
print(paginator.num_pages) # 10
```

### Helper Function

```python
from django_extensions.pagination_utils import paginate

def my_view(request):
    items = Article.objects.all()
    page = paginate(items, request.GET.get('page', 1), per_page=20)
    return render(request, 'list.html', {'page': page})
```

### Page Range

```python
from django_extensions.pagination_utils import get_page_range

page = paginator.page(5)
page_range = get_page_range(page, window=2)
# [3, 4, 5, 6, 7]
```

## Template

```django
{% for item in page.object_list %}
    {{ item }}
{% endfor %}

<nav>
    {% if page.has_previous %}
        <a href="?page=1">First</a>
        <a href="?page={{ page.previous_page_number }}">Previous</a>
    {% endif %}

    {% for num in page_range %}
        {% if num == page.number %}
            <strong>{{ num }}</strong>
        {% else %}
            <a href="?page={{ num }}">{{ num }}</a>
        {% endif %}
    {% endfor %}

    {% if page.has_next %}
        <a href="?page={{ page.next_page_number }}">Next</a>
        <a href="?page={{ paginator.num_pages }}">Last</a>
    {% endif %}
</nav>
```

## Page Object Properties

| Property | Description |
|----------|-------------|
| `object_list` | Items on current page |
| `number` | Current page number |
| `has_next()` | Has next page |
| `has_previous()` | Has previous page |
| `next_page_number()` | Next page number |
| `previous_page_number()` | Previous page number |
| `start_index()` | 1-based index of first item |
| `end_index()` | 1-based index of last item |

## Exceptions

```python
from django_extensions.pagination_utils import PageNotAnInteger, EmptyPage

try:
    page = paginator.page(request.GET.get('page'))
except PageNotAnInteger:
    page = paginator.page(1)
except EmptyPage:
    page = paginator.page(paginator.num_pages)
```

## License

MIT
