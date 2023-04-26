# Periodic tasks, executed by Django-Q

from signage.consumers import SignageConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_keepalive():
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)('keepalive', {'type': 'keepalive'})

if __name__ == "__main__":
    send_keepalive()