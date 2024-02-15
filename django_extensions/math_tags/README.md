# Math Tags

Template tags for mathematical operations.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.math_tags',
]
```

## Usage

```django
{% load math_filters %}

{{ price|multiply:quantity }}
{{ total|divide:items }}
{{ value|percentage:total }}
```

## Available Filters

### add

Addition:

```django
{{ 10|add:5 }}  {# 15 #}
```

### subtract

Subtraction:

```django
{{ 10|subtract:3 }}  {# 7 #}
```

### multiply

Multiplication:

```django
{{ 10|multiply:5 }}  {# 50 #}
{{ price|multiply:quantity }}
```

### divide

Division:

```django
{{ 10|divide:2 }}  {# 5 #}
{{ 10|divide:3 }}  {# 3.333... #}
```

### percentage

Calculate percentage:

```django
{{ 25|percentage:100 }}  {# 25.0 #}
{{ completed|percentage:total }}%
```

### modulo

Modulo operation:

```django
{{ 10|modulo:3 }}  {# 1 #}
```

### absolute

Absolute value:

```django
{{ -5|absolute }}  {# 5 #}
```

### power

Exponentiation:

```django
{{ 2|power:3 }}  {# 8 #}
```

### round_decimal

Round to decimal places:

```django
{{ 3.14159|round_decimal:2 }}  {# 3.14 #}
```

### format_currency

Format as currency:

```django
{{ price|format_currency }}  {# $19.99 #}
{{ price|format_currency:'EUR' }}  {# 19.99 EUR #}
```

## Chaining Filters

```django
{{ base_price|multiply:quantity|add:shipping }}
```

## License

MIT
