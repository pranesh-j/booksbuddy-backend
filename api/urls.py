from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.get_all_books),
    path('process/', views.process_text),
    path('books/<int:book_id>/', views.get_book),
    path('books/<int:book_id>/update/', views.update_book),
    path('books/<int:book_id>/add-page/', views.add_page),
    path('upload-image/', views.upload_image),
]