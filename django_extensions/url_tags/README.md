# URL Tags

Template tags for URL manipulation.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.url_tags',
]
```

## Usage

```django
{% load url_extras %}

{% add_query_param request.path 'page' 2 %}
{{ url|domain }}
{{ url|protocol }}
```

## Available Tags and Filters

### add_query_param

Add or update query parameters:

```django
{% add_query_param '/search/' 'q' 'django' %}
{# /search/?q=django #}

{% add_query_param request.get_full_path 'page' 2 %}
{# /items/?filter=active&page=2 #}
```

### remove_query_param

Remove a query parameter:

```django
{% remove_query_param '/search/?q=test&page=2' 'page' %}
{# /search/?q=test #}
```

### domain

Extract domain from URL:

```django
{{ 'https://www.example.com/path'|domain }}
{# example.com #}
```

### protocol

Extract protocol from URL:

```django
{{ 'https://example.com'|protocol }}
{# https #}
```

### make_absolute

Convert relative URL to absolute:

```django
{{ '/path/to/page/'|make_absolute:request }}
{# https://example.com/path/to/page/ #}
```

### urlencode_params

Encode dictionary as query string:

```django
{% urlencode_params params %}
{# key1=value1&key2=value2 #}
```

### is_external

Check if URL is external:

```django
{% if url|is_external:request %}
    <span class="external-link">External</span>
{% endif %}
```

## URL Building

```django
{% load url_extras %}

{% url_with_params 'search' q=query page=1 %}
{# /search/?q=django&page=1 #}
```

## License

MIT
