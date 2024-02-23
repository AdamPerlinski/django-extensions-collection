# String Tags

Template tags for string manipulation.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.string_tags',
]
```

## Usage

```django
{% load string_extras %}

{{ title|slugify }}
{{ text|truncate_chars:50 }}
{{ html_content|remove_html }}
```

## Available Filters

### slugify

URL-safe slug:

```django
{{ "Hello World!"|slugify }}  {# hello-world #}
```

### title

Title case:

```django
{{ "hello world"|title }}  {# Hello World #}
```

### remove_html / strip_tags

Remove HTML tags:

```django
{{ "<p>Hello <b>World</b></p>"|remove_html }}  {# Hello World #}
```

### truncate_chars

Truncate to character limit:

```django
{{ text|truncate_chars:20 }}  {# First 20 chars... #}
```

### truncate_words

Truncate to word limit:

```django
{{ text|truncate_words:10 }}  {# First 10 words... #}
```

### replace

Replace substring:

```django
{{ text|replace:"old,new" }}
```

### wrap

Wrap text at width:

```django
{{ long_text|wrap:80 }}
```

### initials

Get initials:

```django
{{ "John Doe"|initials }}  {# JD #}
```

### mask

Mask sensitive data:

```django
{{ email|mask:3 }}  {# joh***@example.com #}
{{ phone|mask:4 }}  {# ****1234 #}
```

### pluralize_word

Smart pluralization:

```django
{{ count }} item{{ count|pluralize_word }}
{# 1 item / 2 items #}
```

### camelcase

Convert to camelCase:

```django
{{ "hello_world"|camelcase }}  {# helloWorld #}
```

### snakecase

Convert to snake_case:

```django
{{ "HelloWorld"|snakecase }}  {# hello_world #}
```

## License

MIT
