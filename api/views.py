from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import base64
from .models import Book, Page
from .serializers import BookSerializer
from .services.ai_service import simplify_text, suggest_title, extract_text_from_image
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
def get_all_books(request):
    """Get all books for a specific user"""
    user_id = request.GET.get('userId')
    if not user_id:
        return Response(
            {'error': 'userId is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    books = Book.objects.filter(user_id=user_id)
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def process_text(request):
    """Process text and create a new book"""
    try:
        text = request.data.get('text', '')
        user_id = request.data.get('userId')
        
        if not text or not user_id:
            return Response(
                {'error': 'Both text and userId are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new book with user_id
        book = Book.objects.create(
            title="Untitled Book",
            original_text=text,
            is_processed=True,
            user_id=user_id
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
    user_id = request.GET.get('userId')
    if not user_id:
        return Response(
            {'error': 'userId is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    book = get_object_or_404(Book, id=book_id, user_id=user_id)
    serializer = BookSerializer(book)
    return Response(serializer.data)

@api_view(['PATCH'])
def update_book(request, book_id):
    """Update book details"""
    try:
        user_id = request.data.get('userId')
        if not user_id:
            return Response(
                {'error': 'userId is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        book = get_object_or_404(Book, id=book_id, user_id=user_id)
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
        user_id = request.data.get('userId')
        if not user_id:
            return Response(
                {'error': 'userId is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        book = get_object_or_404(Book, id=book_id, user_id=user_id)
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
        book.refresh_from_db()
        
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

@api_view(['DELETE'])
def delete_book(request, book_id):
    """Delete a specific book"""
    try:
        user_id = request.data.get('userId')
        if not user_id:
            return Response(
                {'error': 'userId is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        book = get_object_or_404(Book, id=book_id, user_id=user_id)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def health_check(request):
    return Response({"status": "healthy"})