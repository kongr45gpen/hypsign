# Periodic tasks, executed by Django-Q

from signage.consumers import SignageConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models import Q
from signage.models import ScheduleEntry
from signage.signals import display_update_signal

from datetime import datetime, timedelta

import logging

logger = logging.getLogger("tasks")

def send_keepalive():
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)('keepalive', {'type': 'keepalive'})

def check_for_updates():
    today = datetime.now().date()
    yesterday = datetime.now() - timedelta(days=1) # add some leeway for display sequences that need to be removed
    # Find all schedule items within a relevant time frame
    past_query = Q(start_date__lte=yesterday) | Q(start_date__isnull=True)
    future_query = Q(end_date__gte=today) | Q(end_date__isnull=True)

    displays = set()
    schedule_entries = ScheduleEntry.objects.filter(past_query, future_query)
    for entry in schedule_entries:
        displays.update(entry.displays.all())

    for display in displays:
        channel_layer = get_channel_layer()
        if display.did_page_change():
            logger.info("Display {} page changed".format(display.code))
            async_to_sync(channel_layer.group_send)(f'signage_display__{display.code}', {'type': 'display_updated'})
        else:
            logger.debug("Display {} unaffected by page change".format(display.code))

        
if __name__ == "__main__":
    send_keepalive()