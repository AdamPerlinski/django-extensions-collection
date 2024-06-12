"""
anonymous_required - Decorator to require non-authenticated users.

Usage:
    from django_extensions.anonymous_required import anonymous_required

    @anonymous_required
    def login_view(request):
        ...

    # With custom redirect
    @anonymous_required(redirect_url='/dashboard/')
    def register_view(request):
        ...
"""

