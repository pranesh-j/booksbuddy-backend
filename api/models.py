from django.db import models
from django.utils import timezone

class Book(models.Model):
    title = models.CharField(max_length=200, default="Untitled")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pages = models.JSONField(default=list, blank=True)

    def add_page(self, text):
        if not isinstance(self.pages, list):
            self.pages = []
        self.pages.append(text)
        self.save()

    def __str__(self):
        return self.title

class Page(models.Model):
    book = models.ForeignKey(Book, related_name='pages', on_delete=models.CASCADE)
    page_number = models.IntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['page_number']
        unique_together = ['book', 'page_number']