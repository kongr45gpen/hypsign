from django.db import models
import logging

from signage.signals import display_update_signal
from django.db.models.signals import post_save,m2m_changed
from django.dispatch import receiver

logger = logging.getLogger('app')

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        displays = set()
        schedule_entries = ScheduleEntry.objects.filter(page=self)
        for schedule_entry in schedule_entries:
            displays.update(schedule_entry.displays.all())
        
        for display in displays:
            logging.info("Display {} schedule changed".format(display.code))
            display_update_signal.send(sender=Page, data=display.code)


    def __str__(self):
        return self.description

class ScheduleEntry(models.Model):
    displays = models.ManyToManyField(Display, blank=True)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.displays} - {self.page} - {self.start_time} - {self.end_time}"


@receiver(post_save, sender=ScheduleEntry)
def schedule_item_saved_post(sender, instance, **kwargs):
    for display in instance.displays.all():
        logging.info("Display {} schedule changed".format(display.code))
        display_update_signal.send(sender=sender, data=display.code)

@receiver(m2m_changed, sender=ScheduleEntry.displays.through)
def schedule_item_display_added(sender, instance, action, reverse, pk_set, **kwargs):
    if action == "post_add":
        if reverse:
            displays = [instance]
        else:
            displays = Display.objects.filter(id__in=pk_set)
    
        for display in displays:
            logging.info("Display {} schedule added".format(display.code))
            display_update_signal.send(sender=sender, data=display.code)