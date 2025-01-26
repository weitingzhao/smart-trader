import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import redis
import json
import pandas as pd
from business import logic

class StockMonitorWS(AsyncWebsocketConsumer):
    sms_name_stock_quote = 'stock_quote'
    sms_name_stock_hist = 'stock_hist'

    async def connect(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

        self.pubsub = self.redis_client.pubsub()
        self.pubsub.subscribe(
            self.sms_name_stock_quote,
            self.sms_name_stock_hist)

        await self.accept()
        self.redis_task = asyncio.create_task(self.listen_to_redis())
        await self._init_stock_hist()

    async def disconnect(self, close_code):
        self.pubsub.unsubscribe(
            self.sms_name_stock_quote,
            self.sms_name_stock_hist)

        self.redis_task.cancel()
        try:
            await self.redis_task
        except asyncio.CancelledError:
            pass

    async def receive(self, text_data):
        pass

    async def listen_to_redis(self):
        while True:
            message = self.pubsub.get_message()
            if message and message['type'] == 'message':
                json_str =json.dumps(json.loads(message['data']))
                await self.send(text_data=json_str)
            await asyncio.sleep(0.1)



    async def _init_stock_hist(self):
        recent_prices = pd.read_sql_query("""
            SELECT
                w.symbol_id AS symbol,
                b.close,
                b.time,
                prev_b.close AS pre_close,
                prev_b.time AS pre_time
            FROM
                wishlist w
            LEFT JOIN
                market_stock_hist_bars_day_ts b
            ON
                w.symbol_id = b.symbol
            LEFT JOIN
                market_stock_hist_bars_day_ts prev_b
            ON
                w.symbol_id = prev_b.symbol
                AND prev_b.time = (
                    SELECT MAX(time)
                    FROM market_stock_hist_bars_day_ts
                    WHERE symbol = w.symbol_id
                    AND time < (SELECT MAX(time) FROM market_stock_hist_bars_day_ts WHERE symbol = w.symbol_id)
                )
            WHERE
            b.time = (SELECT MAX(time) FROM market_stock_hist_bars_day_ts);
        """, logic.engine().sql_alchemy().create_engine())
        for _, row in recent_prices.iterrows():
            detail = {
                'close': row['close'],
                'date': row['time'].isoformat(),
                'pre_close': row['pre_close'],
                'pre_time': row['pre_time'].isoformat(),
            }
            json_str = json.dumps({'type': 'hist', 'interval': 'D',  'key': row['symbol'], 'detail': detail})
            print(f"Hist->Redis->: {json_str}")
            self.redis_client.publish(self.sms_name_stock_hist, json_str)
