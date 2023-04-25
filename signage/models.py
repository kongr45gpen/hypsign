from django.db import models
import logging

logger = logging.getLogger('app')

# Create your models here.
class Display(models.Model):
    code = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description
    
    def get_current_schedule_item(self):
        return ScheduleEntry.objects.filter(displays=self).first()
    
class Page(models.Model):
    description = models.CharField(max_length=255)
    path = models.CharField(max_length=512)
    mime_type = models.CharField(max_length=255, default="text/html")

    def __str__(self):
        return self.description

class ScheduleEntry(models.Model):
    displays = models.ManyToManyField(Display)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.displays} - {self.page} - {self.start_time} - {self.end_time}"