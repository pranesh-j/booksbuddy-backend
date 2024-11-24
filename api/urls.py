from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.get_all_books, name='get-all-books'),
    path('books/<int:book_id>/', views.get_book, name='get-book'),
    path('books/<int:book_id>/update/', views.update_book, name='update-book'),
    path('books/<int:book_id>/add-page/', views.add_page, name='add-page'),
    path('process/', views.process_text, name='process-text'),
    path('upload-image/', views.upload_image, name='upload-image'),
    path('health/', views.health_check, name='health_check'),
] 