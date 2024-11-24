from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('health/', views.health_check, name='health_check'),
    path('books/', views.book_list, name='book-list'),
    path('books/<int:pk>/', views.book_detail, name='book-detail'),
    path('process/', views.process_text, name='process-text'),
]

urlpatterns += router.urls 