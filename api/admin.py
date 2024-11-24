from django.contrib import admin
from .models import Book, Page

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'title', 'last_edited')  # Adjust fields as needed
    list_filter = ('created_at',)

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('book', 'page_number', 'created_at')
    list_filter = ('book', 'created_at')
