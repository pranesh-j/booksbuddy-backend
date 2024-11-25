from django.db import models
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Book(models.Model):
    user_id = models.CharField(max_length=100)
    title = models.CharField(max_length=200, blank=True, null=True, default="Untitled Book")
    original_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)
    is_processed = models.BooleanField(default=False)
    total_pages = models.IntegerField(default=0)

    class Meta:
        ordering = ['-last_edited']
        indexes = [
            models.Index(fields=['user_id', '-last_edited']),
        ]

    def add_page(self, text):
        """Add a new page to the book"""
        try:
            new_page = Page.objects.create(
                book=self,
                page_number=self.total_pages + 1,
                content=text
            )
            
            self.total_pages += 1
            self.last_edited = timezone.now()
            self.save()
            
            return new_page
            
        except Exception as e:
            logger.error(f"Error adding page: {str(e)}")
            raise

    def __str__(self):
        return f"{self.title} (User: {self.user_id})"

class Page(models.Model):
    book = models.ForeignKey(Book, related_name='pages', on_delete=models.CASCADE)
    page_number = models.IntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['page_number']
        unique_together = ['book', 'page_number']

    def __str__(self):
        return f"Page {self.page_number} in {self.book.title}"