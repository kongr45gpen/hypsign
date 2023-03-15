from django.db import models

# Create your models here.
class Display(models.Model):
    code = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description
    
class Page(models.Model):
    description = models.CharField(max_length=255)
    path = models.CharField(max_length=512)
    mime_type = models.CharField(max_length=255, default="text/html")

    def __str__(self):
        return self.description
