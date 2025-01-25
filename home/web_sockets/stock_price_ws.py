import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import redis
import json

class StockPriceWS(AsyncWebsocketConsumer):

    async def connect(self):
        self.group_name = 'stock_prices'
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

        # await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        # await self.send(text_data=json.dumps({'test': 'test'}))
        # Start a background task to listen to Redis messages
        asyncio.create_task(self.listen_to_redis())

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass


    async def listen_to_redis(self):
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(self.group_name)

        while True:
            message = pubsub.get_message()
            if message and message['type'] == 'message':
                json_str =json.dumps(json.loads(message['data']))
                await self.send(text_data=json_str)
            await asyncio.sleep(0.1)



