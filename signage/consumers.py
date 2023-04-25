import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

class SignageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        logging.debug("Received text data from user: {}".format(text_data_json))

        await self.send(text_data=json.dumps({"message": "received"}))