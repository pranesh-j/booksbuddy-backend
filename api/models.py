from django.db import models
from django.utils import timezone

class Book(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True, default="Untitled Book")
    original_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)
    is_processed = models.BooleanField(default=False)
    total_pages = models.IntegerField(default=0)

    class Meta:
        ordering = ['-last_edited']

    def process_text(self, simplified_text):
        try:
            Page.objects.create(
                book=self,
                page_number=self.total_pages + 1,
                content=simplified_text
            )
            
            self.total_pages += 1
            self.is_processed = True
            self.last_edited = timezone.now()
            self.save()
            
        except Exception as e:
            print(f"Error in process_text: {str(e)}")
            raise

    def add_page(self, text):
        try:
            Page.objects.create(
                book=self,
                page_number=self.total_pages + 1,
                content=text
            )
            
            self.total_pages += 1
            self.last_edited = timezone.now()
            self.save()
            
        except Exception as e:
            print(f"Error adding page: {str(e)}")
            raise

class Page(models.Model):
    book = models.ForeignKey(Book, related_name='pages', on_delete=models.CASCADE)
    page_number = models.IntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['page_number']
        unique_together = ['book', 'page_number']