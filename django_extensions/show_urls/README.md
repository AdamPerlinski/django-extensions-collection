# Show URLs

Display all URL patterns in your Django project.

## Installation

```python
INSTALLED_APPS = [
    'django_extensions.show_urls',
]
```

## Usage

```bash
python manage.py show_urls
```

## Output

```
/                       home                    myapp.views.home
/about/                 about                   myapp.views.about
/api/users/             api-users-list          myapp.api.UserViewSet
/api/users/<pk>/        api-users-detail        myapp.api.UserViewSet
/admin/                 admin:index             django.contrib.admin.sites.index
```

## Options

### Format

```bash
# Table format (default)
python manage.py show_urls

# JSON format
python manage.py show_urls --format json

# Pretty table
python manage.py show_urls --format table
```

### Filter by App

```bash
python manage.py show_urls --app myapp
```

### Filter by Pattern

```bash
python manage.py show_urls --pattern /api/
```

### Show Decorators

```bash
python manage.py show_urls --decorators
```

```
/api/users/  api-users  myapp.api.users  [@login_required, @csrf_exempt]
```

### Show HTTP Methods

```bash
python manage.py show_urls --methods
```

```
GET,POST    /api/users/        api-users-list    myapp.api.UserViewSet
GET,PUT,DEL /api/users/<pk>/   api-users-detail  myapp.api.UserViewSet
```

## Sorting

```bash
# Sort by URL
python manage.py show_urls --sort url

# Sort by name
python manage.py show_urls --sort name

# Sort by view
python manage.py show_urls --sort view
```

## Export

```bash
# Export to file
python manage.py show_urls > urls.txt

# Export as JSON
python manage.py show_urls --format json > urls.json
```

## License

MIT
