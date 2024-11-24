from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import base64
from .models import Book, Page
from .serializers import BookSerializer
from .services.claude_service import simplify_text, suggest_title, extract_text_from_image
import logging
from rest_framework.reverse import reverse

logger = logging.getLogger(__name__)

@api_view(['GET'])
def get_all_books(request):
    """Get all books"""
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def process_text(request):
    try:
        text = request.data.get('text', '')
        if not text:
            return Response(
                {'error': 'No text provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new book
        book = Book.objects.create(
            title="Untitled Book",
            original_text=text,
            is_processed=True
        )
        
        # Simplify text using Claude
        try:
            simplified_text = simplify_text(text)
            suggested_title = suggest_title(text)
        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            return Response(
                {'error': 'Error processing text with AI service'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Add page and update title
        book.add_page(simplified_text)
        book.title = suggested_title
        book.save()
        
        serializer = BookSerializer(book)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error in process_text: {str(e)}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_book(request, book_id):
    """Get a specific book and its pages"""
    book = get_object_or_404(Book, id=book_id)
    serializer = BookSerializer(book)
    return Response(serializer.data)

@api_view(['PATCH'])
def update_book(request, book_id):
    """Update book details"""
    try:
        book = get_object_or_404(Book, id=book_id)
        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def add_page(request, book_id):
    """Add a new page to an existing book"""
    try:
        book = get_object_or_404(Book, id=book_id)
        text = request.data.get('text', '')
        
        if not text:
            return Response(
                {'error': 'No text provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Simplify new text
        try:
            simplified_text = simplify_text(text)
        except Exception as e:
            logger.error(f"Claude API error in add_page: {str(e)}")
            return Response(
                {'error': 'Error processing text with AI service'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Add as new page
        book.add_page(simplified_text)
        book.refresh_from_db()  # Refresh to get updated data
        
        serializer = BookSerializer(book)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error in add_page: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_image(request):
    """Handle image upload and text extraction using Claude"""
    try:
        if 'image' not in request.FILES:
            return Response(
                {'error': 'No image file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        image_file = request.FILES['image']
        
        # Read the image file and encode it to base64
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Extract text using Claude
        extracted_text = extract_text_from_image(image_data)
        
        return Response({
            'extracted_text': extracted_text
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def health_check(request):
    return Response({"status": "healthy"})

@api_view(['GET'])
def api_root(request):
    return Response({
        'health': '/api/health/',
        'books': '/api/books/',
        'process': '/api/process/'
    })

@api_view(['GET', 'POST'])
def book_list(request):
    if request.method == 'GET':
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def book_detail(request, pk):
    try:
        book = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BookSerializer(book)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)