# Humanize Tags

Template tags for human-readable formatting.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.humanize_tags',
]
```

## Usage

```django
{% load humanize_extras %}

{{ article.created|naturaltime }}
{{ file.size|filesizeformat }}
{{ count|intcomma }}
{{ items|oxford_comma }}
```

## Available Filters

### naturaltime

Human-readable relative time:

```django
{{ datetime|naturaltime }}
```

| Input | Output |
|-------|--------|
| Now | just now |
| 30 seconds ago | just now |
| 5 minutes ago | 5 minutes ago |
| 2 hours ago | 2 hours ago |
| Yesterday | 1 day ago |
| Last week | 7 days ago |

### filesizeformat

Human-readable file sizes:

```django
{{ size|filesizeformat }}
```

| Input | Output |
|-------|--------|
| 512 | 512 B |
| 1024 | 1.0 KiB |
| 1048576 | 1.0 MiB |
| 1073741824 | 1.0 GiB |

### intcomma

Number with thousand separators:

```django
{{ number|intcomma }}
```

| Input | Output |
|-------|--------|
| 1000 | 1,000 |
| 1000000 | 1,000,000 |
| 1234567.89 | 1,234,567.89 |

### oxford_comma

List with Oxford comma:

```django
{{ items|oxford_comma }}
```

| Input | Output |
|-------|--------|
| ['a'] | a |
| ['a', 'b'] | a and b |
| ['a', 'b', 'c'] | a, b, and c |

### ordinal

Ordinal numbers:

```django
{{ number|ordinal }}
```

| Input | Output |
|-------|--------|
| 1 | 1st |
| 2 | 2nd |
| 3 | 3rd |
| 4 | 4th |
| 11 | 11th |

## License

MIT
