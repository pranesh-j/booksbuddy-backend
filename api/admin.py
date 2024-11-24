from django.contrib import admin
from .models import Book, Page

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'is_processed', 'total_pages')
    list_filter = ('is_processed', 'created_at')

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('book', 'page_number', 'created_at')
    list_filter = ('book', 'created_at')
