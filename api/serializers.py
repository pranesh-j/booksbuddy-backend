from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'created_at', 'updated_at', 'pages']
        read_only_fields = ['created_at', 'updated_at']