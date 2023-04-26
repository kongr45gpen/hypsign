# signals.py
from django.dispatch.dispatcher import Signal
from django.db.models.signals import pre_save,post_save,m2m_changed
from signage.models import ScheduleEntry, Display
from django.dispatch import receiver

import logging

# Signal sent whenever the content of a display is updated
display_update_signal = Signal()

# Signal sent whenever a display is connected or disconnected
display_connect_signal = Signal()

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