import re
import datetime
import logging
import asyncio
import random
import string

from channels.db import database_sync_to_async
from django.http import Http404

from djangochannelsrestframework.decorators import action
from djangochannelsrestframework.observer import observer
from djangochannelsrestframework.consumers import AsyncAPIConsumer
from asgiref.sync import SyncToAsync

from signage.models import Display
from rest_framework.exceptions import NotFound
from signage.serializers import PageSerializer
from .signals import display_update_signal, display_diagnosis, take_screenshot_signal
from channels.layers import get_channel_layer
from django.core.cache import cache

from channels import layers
from rest_framework import status

logger = logging.getLogger("websockets")

lock = asyncio.Lock()
connected_displays = {}

class SignageConsumer(AsyncAPIConsumer):
    # Code of the connected display, if any
    code = None
    # Code of the connected browser/device, if any
    device_id = None

    async def disconnect(self, close_code):
        async with lock:
            if self.channel_name in connected_displays:
                del connected_displays[self.channel_name]
                await SyncToAsync(display_diagnosis.send)(sender=self.__class__, data={'code': self.code}, type='disconnected')
        await self.channel_layer.group_discard(f'keepalive', self.channel_name)
        await self.channel_layer.group_discard(f'signage_display__{self.code}', self.channel_name)

    async def _add_to_connected_displays(self, data):
        async with lock:
            connected_displays[self.channel_name] = {
                **data,
                'ip_address': self.scope['client'][0],
                'connected_at': datetime.datetime.now().isoformat(),
                'device_id': self.device_id
            }
        await SyncToAsync(display_diagnosis.send)(sender=self.__class__, data=data, type='connected')

    def _create_random_device_id(self):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))

    @action()
    async def ping(self, **kwargs):
        return None, status.HTTP_204_NO_CONTENT

    @action()
    async def hello(self, code, device_id = None, **kwargs):
        try:
            display = await database_sync_to_async(Display.objects.get)(code=code)
        except Exception as e:
            logger.warning("Display not found: {}".format(e))
            raise NotFound("Display not found")

        self.code = code

        # Untrustworthy and can be easily spoofed, but is only used for diagnostics and doesn't affect anything
        if device_id is None:
            device_id = self._create_random_device_id()
        else:
            device_id = re.match(r'[a-zA-Z0-9_-]{1,7}', device_id)
            if device_id is None:
                device_id = self._create_random_device_id()
            else:
                device_id = device_id.group(0)
        self.device_id = device_id

        await self.display_updated_handler.subscribe(code=code, **kwargs)
        await self.take_screenshot_handler.subscribe(code=code, **kwargs)
        await self.channel_layer.group_add(f'keepalive', self.channel_name)
        await self.channel_layer.group_add(f'signage_display__{code}', self.channel_name)
        asyncio.create_task(self._add_to_connected_displays({'code': code, 'display': kwargs['display']}))

        logger.debug("Received hello from display: [{}] {}".format(self.device_id, display.code))
        return {'device_id': self.device_id}, status.HTTP_200_OK
    
    @action()
    async def request_screenshots(self, data = {}, **kwargs):
        logger.debug("Requested screenshot")
        await SyncToAsync(take_screenshot_signal.send)(sender=self.__class__)
    

    @action()
    async def screenshot(self, data, **kwargs):
        logger.debug("Received screenshot from device: [{}] {}".format(self.device_id, self.code))
        # Truncate data to 1 MB max
        data = data[:1024*1024]
        # cache.set(f'screenshot_{self.code}', data, timeout=60*10)
        await SyncToAsync(display_diagnosis.send)(sender=self.__class__, data={'device': self.device_id, 'code': self.code, 'data': data}, type='screenshot')
    
    @action()
    def get_current_page(self, code, **kwargs):
        try:
            display = Display.objects.get(code=code)
        except Exception as e:
            logger.warning("Display not found: {}".format(code))
            raise NotFound("Display not found")
        
        page = display.get_current_page()
        if not page:
            return None, 404
        else:
            logger.debug("Displaying page [{}] {} to display {}".format(page.id, page.description, code))
                        
        return PageSerializer(page).data, 200
    
    @action()
    async def get_connected_displays(self, **kwargs):
        async with lock:
            logger.debug("Found {} subscribed displays".format(len(connected_displays)))
            return list(connected_displays.values()), 200
    
    @observer(signal=display_update_signal)
    async def display_updated_handler(self, data, observer=None, action=None, subscribing_request_ids=[], **kwargs):
        for request_id in subscribing_request_ids:
            await self.reply(action='display_updated', data=data, status=status.HTTP_200_OK, request_id=request_id)

    # Enumerate which groups the event should be sent to
    @display_updated_handler.groups_for_signal
    def display_updated_handler(self, data, **kwargs):
        yield f'display__{data}'

    # Enumerate which groups should be subscribed/unsubscribed
    @display_updated_handler.groups_for_consumer
    def display_updated_handler(self, code, **kwargs):
        if code:
            yield f'display__{code}'

    @action()
    async def subscribe_to_display_connections(self, **kwargs):
        await self.display_connected_handler.subscribe(**kwargs)
        return {}, status.HTTP_204_NO_CONTENT 

    @observer(signal=display_diagnosis)
    async def display_connected_handler(self, data={}, type=None, subscribing_request_ids=[], **kwargs):
        type = data['type']
        for request_id in subscribing_request_ids:
            if type == 'connected' or type == 'disconnected':
                await self.handle_action(action='get_connected_displays', request_id=request_id)
            elif type == 'screenshot':
                await self.reply(action='screenshot_received', data=data, status=status.HTTP_200_OK, request_id=request_id)

    @display_connected_handler.serializer
    def display_connected_handler(self, signal, sender, type=None, data={}, **kwargs):
        return { 'type': type, 'data': data }

    async def keepalive(self, event):
        await self.reply(action='keepalive', data=None, status=status.HTTP_204_NO_CONTENT)

    #TODO: Request authentication!
    @action()
    async def request_refresh(self, **kwargs):
        await self.channel_layer.group_send('keepalive', {'type': 'do_send_refresh'})

    async def do_send_refresh(self, event):
        await self.reply(action='refresh', data=None, status=status.HTTP_204_NO_CONTENT)

    #TODO: Request authentication!
    @observer(signal=take_screenshot_signal)
    async def take_screenshot_handler(self, code, observer=None, action=None, subscribing_request_ids=[], **kwargs):
        for request_id in subscribing_request_ids:
            await self.reply(action='take_screenshot', data=None, status=status.HTTP_204_NO_CONTENT, request_id=request_id)

    async def display_updated(self, event):
        logger.debug("Display updated: {}".format(event))
        await self.reply(action='display_updated', data=None, status=status.HTTP_204_NO_CONTENT)
