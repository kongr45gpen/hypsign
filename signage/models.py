from django.db import models
import logging

from django.core.cache import cache
from django.db.models import Q
from signage.signals import display_update_signal
from django.db.models.signals import post_save,m2m_changed
from django.dispatch import receiver
from django.core import serializers
from datetime import datetime, timedelta

logger = logging.getLogger('app')

class Display(models.Model):
    code = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description
    
    @staticmethod
    def Query_Time(when):
        after_start_date = Q(start_date__isnull=True) | Q(start_date__lte=when.date())
        before_end_date = Q(end_date__isnull=True) | Q(end_date__gte=when.date())

        after_start_time = Q(start_time__isnull=True) | Q(start_time__lte=when.time())
        before_end_time = Q(end_time__isnull=True) | Q(end_time__gte=when.time())

        return after_start_date & before_end_date & after_start_time & before_end_time

    
    def get_current_schedule_item(self):
        time_query = self.Query_Time(datetime.now())
        return ScheduleEntry.objects.filter(time_query, displays=self, enabled=True).order_by('-priority').first()
    
    def get_current_page(self):
        schedule_item = self.get_current_schedule_item()
        if schedule_item:
            sequence_item = schedule_item.get_current_sequence_item()
            if sequence_item:
                page = sequence_item.page
                cache.set(f'display_{self.code}', serializers.serialize('json', [page]), 7200)
                return page
            
        cache.delete(f'display_{self.code}')
        return None
        
    def did_page_change(self):
        old_page_json = cache.get(f'display_{self.code}')
        new_page = self.get_current_page()

        if old_page_json:
            new_page_json = serializers.serialize('json', [new_page])
            if old_page_json == new_page_json:
                return False

        return new_page
    
    class Meta:
        ordering = ['code']
        
class Page(models.Model):
    description = models.CharField(max_length=255)
    path = models.CharField(max_length=512)
    mime_type = models.CharField(max_length=255, default="text/html")

    cover = models.BooleanField(default=False, help_text="Whether images should be cropped and upscaled to cover the entire page, instead of being fully contained inside the page")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        displays = Display.objects.filter(scheduleentry__sequence__page=self)
        
        for display in displays:
            if display.did_page_change():
                logging.info("Display {} page changed".format(display.code))
                display_update_signal.send(sender=Page, data=display.code)
            else:
                pass


    def __str__(self):
        return self.description

class ScheduleEntry(models.Model):
    displays = models.ManyToManyField(Display, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)

    priority = models.IntegerField(default=0)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{[str(s) for s in self.sequence.all()]} - {[str(d) for d in self.displays.all()]}"
    
    def is_active_now(self, time=None):
        if time is None:
            time = datetime.now()
        
        if self.start_date and self.start_date > time.date():
            return False
        
        if self.end_date and self.end_date < time.date():
            return False
        
        if self.start_time and self.start_time > time.time():
            return False
        
        if self.end_time and self.end_time < time.time():
            return False
        
        return True
    
    def get_current_sequence_item(self, time=None):
        if time is None:
            time = datetime.now()

        seconds_since_midnight = (time - time.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        
        total_duration = self.sequence.aggregate(models.Sum('duration'))['duration__sum']

        if not total_duration:
            logger.error("Schedule entry {} has no sequence items".format(self))
            return None

        seconds_counted = seconds_since_midnight % (total_duration * 60)

        current_duration = 0
        for sequence_item in self.sequence.all():
            current_duration += sequence_item.duration * 60
            if current_duration >= seconds_counted:
                return sequence_item
        
        # Normally this point shouldn't be reached
        return None

    class Meta:
        ordering = ['start_date', 'start_time', '-priority']


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