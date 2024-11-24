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

    def add_page(self, text):
        page_number = self.book_pages.count() + 1
        Page.objects.create(
            book=self,
            page_number=page_number,
            content=text
        )
        self.total_pages = page_number
        self.save()

    def __str__(self):
        return self.title

class Page(models.Model):
    book = models.ForeignKey(Book, related_name='book_pages', on_delete=models.CASCADE)
    page_number = models.IntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['page_number']
        unique_together = ['book', 'page_number']

    def __str__(self):
        return f"Page in {self.book.title}"