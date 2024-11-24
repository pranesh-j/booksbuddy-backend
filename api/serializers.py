from rest_framework import serializers
from .models import Book, Page

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['id', 'page_number', 'content', 'created_at']

class BookSerializer(serializers.ModelSerializer):
    pages = PageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'original_text', 'created_at', 'last_edited',
                  'is_processed', 'total_pages', 'pages']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['pages'] = sorted(
            representation['pages'],
            key=lambda x: x['page_number']
        )
        return representation