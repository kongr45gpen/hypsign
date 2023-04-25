import json
import logging

from channels.db import database_sync_to_async
from django.http import Http404

from djangochannelsrestframework.decorators import action
from djangochannelsrestframework.consumers import AsyncAPIConsumer

from signage.models import Display

from rest_framework.exceptions import NotFound

from signage.serializers import PageSerializer

class SignageConsumer(AsyncAPIConsumer):
    # async def connect(self):
    #     await self.accept()

    # async def disconnect(self, close_code):
    #     pass

    @action()
    async def hello(self, code, **kwargs):
        try:
            display = await database_sync_to_async(Display.objects.get)(code=code)
        except Exception as e:
            logging.warning("Display not found: {}".format(code))
            raise NotFound("Display not found")

        logging.debug("Received hello from display: {}".format(display.code))
        return {}, 200
    
    @action()
    def get_current_page(self, code, **kwargs):
        try:
            display = Display.objects.get(code=code)
        except Exception as e:
            logging.warning("Display not found: {}".format(code))
            raise NotFound("Display not found")
        
        schedule_item = display.get_current_schedule_item()
        if not schedule_item:
            return {}, 404
        
        page = schedule_item.page
                
        return PageSerializer(page).data, 200
