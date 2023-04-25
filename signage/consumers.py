import json
import logging
import asyncio

from channels.db import database_sync_to_async
from django.http import Http404

from djangochannelsrestframework.decorators import action
from djangochannelsrestframework.observer import observer
from djangochannelsrestframework.consumers import AsyncAPIConsumer

from signage.models import Display
from rest_framework.exceptions import NotFound
from signage.serializers import PageSerializer
from .signals import display_update_signal

from channels import layers
from rest_framework import status

logger = logging.getLogger("websockets")

lock = asyncio.Lock()
subscribed_displays = {}

class SignageConsumer(AsyncAPIConsumer):
    async def disconnect(self, close_code):
        async with lock:
            if self.channel_name in subscribed_displays:
                del subscribed_displays[self.channel_name]

    async def add_to_subscribed_displays(self, data):
        async with lock:
            subscribed_displays[self.channel_name] = {**data, 'ip_address': self.scope['client'][0]}

    @action()
    async def hello(self, code, **kwargs):
        try:
            display = await database_sync_to_async(Display.objects.get)(code=code)
        except Exception as e:
            logger.warning("Display not found: {}".format(code))
            raise NotFound("Display not found")

        await self.display_updated_handler.subscribe(code=code, **kwargs)
        asyncio.create_task(self.add_to_subscribed_displays({'code': code, 'display': kwargs['display']}))

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
    async def get_subscribed_displays(self, **kwargs):
        async with lock:
            logger.debug("Found {} subscribed displays".format(len(subscribed_displays)))
            return list(subscribed_displays.values()), 200
    
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
