import datetime
import logging
import asyncio

from channels.db import database_sync_to_async
from django.http import Http404

from djangochannelsrestframework.decorators import action
from djangochannelsrestframework.observer import observer
from djangochannelsrestframework.consumers import AsyncAPIConsumer
from asgiref.sync import SyncToAsync

from signage.models import Display
from rest_framework.exceptions import NotFound
from signage.serializers import PageSerializer
from .signals import display_update_signal, display_connect_signal

from channels import layers
from rest_framework import status

logger = logging.getLogger("websockets")

lock = asyncio.Lock()
connected_displays = {}

class SignageConsumer(AsyncAPIConsumer):
    # Code of the connected display, if any
    code = None

    async def disconnect(self, close_code):
        async with lock:
            if self.channel_name in connected_displays:
                del connected_displays[self.channel_name]
                await SyncToAsync(display_connect_signal.send)(sender=self.__class__, data={'code': self.code})

    async def _add_to_connected_displays(self, data):
        async with lock:
            connected_displays[self.channel_name] = {
                **data,
                'ip_address': self.scope['client'][0],
                'connected_at': datetime.datetime.now().isoformat()
            }
        await SyncToAsync(display_connect_signal.send)(sender=self.__class__, data=data)

    @action()
    async def hello(self, code, **kwargs):
        try:
            display = await database_sync_to_async(Display.objects.get)(code=code)
        except Exception as e:
            logger.warning("Display not found: {}".format(code))
            raise NotFound("Display not found")

        self.code = code

        await self.display_updated_handler.subscribe(code=code, **kwargs)
        asyncio.create_task(self._add_to_connected_displays({'code': code, 'display': kwargs['display']}))

        logger.debug("Received hello from display: {}".format(display.code))
        return {}, status.HTTP_204_NO_CONTENT
    
    @action()
    def get_current_page(self, code, **kwargs):
        try:
            display = Display.objects.get(code=code)
        except Exception as e:
            logger.warning("Display not found: {}".format(code))
            raise NotFound("Display not found")
        
        schedule_item = display.get_current_schedule_item()
        if not schedule_item:
            return {}, 404 
        
        page = schedule_item.page
                
        return PageSerializer(page).data, 200
    
    @action()
    async def get_connected_displays(self, **kwargs):
        async with lock:
            logger.debug("Found {} subscribed displays".format(len(connected_displays)))
            return list(connected_displays.values()), 200
    
    @observer(signal=display_update_signal)
    async def display_updated_handler(self, data, observer=None, action=None, subscribing_request_ids=[], **kwargs):
        for request_id in subscribing_request_ids:
            await self.reply(action='display_entered', data=data, status=status.HTTP_200_OK, request_id=request_id)

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

    @observer(signal=display_connect_signal)
    async def display_connected_handler(self, data, observer=None, action=None, subscribing_request_ids=[], **kwargs):
        for request_id in subscribing_request_ids:
            await self.handle_action(action='get_connected_displays', request_id=request_id)
