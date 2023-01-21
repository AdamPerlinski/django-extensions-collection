from django.urls import path

def dummy_view(request):
    pass

urlpatterns = [
    path('', dummy_view, name='home'),
    path('about/', dummy_view, name='about'),
    path('users/<int:pk>/', dummy_view, name='user-detail'),
]
