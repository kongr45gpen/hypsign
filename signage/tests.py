from django.test import TestCase
from channels.testing import WebsocketCommunicator
from signage.consumers import SignageConsumer

class WebSocketTests(TestCase):
    async def test_websocket(self):
        communicator = WebsocketCommunicator(SignageConsumer.as_asgi(), "/")
        connected, subprotocol = await communicator.connect()
        assert connected
        # Test sending text
        await communicator.send_to(text_data="{\"type\": \"hello\"}")
        response = await communicator.receive_from()
        assert response == "{\"message\": \"received\"}"
        # Close
        await communicator.disconnect()