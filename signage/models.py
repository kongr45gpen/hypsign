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
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)

    priority = models.IntegerField(default=0)

    def __str__(self):
        return f"{[str(s) for s in self.sequence.all()]} - {[str(d) for d in self.displays.all()]}"

class ScheduleSequenceItem(models.Model):
    schedule_entry = models.ForeignKey(ScheduleEntry, on_delete=models.CASCADE, related_name='sequence')
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    duration = models.FloatField(default=1, blank=False, null=False, help_text="Duration in minutes")

    order = models.PositiveIntegerField(default=0, blank=False, null=False)
    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.page} [{self.duration} min]"


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