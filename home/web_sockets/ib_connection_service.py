import redis
import asyncio
import threading
from ib_insync import *
import pandas as pd
import json
import datetime
from apps.common.models import Wishlist
from business import logic


class IBConnectionService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls.ib = IB()
                cls.ib.connect('127.0.0.1', 7496, clientId=1)
                cls._running = False
                cls.tickers = {}
                cls.group_name = 'stock_prices'
                cls.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
        return cls._instance


    def attach(self, symbol):

        async def on_tick(ticker):
            try:
                key = ticker.contract.symbol
                detail = {
                    'bid': ticker.bid if not pd.isna(ticker.bid) else None,
                    'ask': ticker.ask if not pd.isna(ticker.ask) else None,
                    'last': ticker.last if not pd.isna(ticker.last) else None,
                    'high': ticker.high if not pd.isna(ticker.high) else None,
                    'low': ticker.low if not pd.isna(ticker.low) else None,
                    'close': ticker.close if not pd.isna(ticker.close) else None,
                    'volume': ticker.volume if not pd.isna(ticker.volume) else None,
                    'time': ticker.time.isoformat()  # Add the time attribute
                }
                json_str = json.dumps({'type': 'quote', 'key': key, 'detail': detail})
                print(f"IB->Redis->: {json_str}")
                self.redis_client.publish(self.group_name,json_str)
            except Exception as e:
                print(str(e))

        contract = Stock(symbol, 'SMART', 'USD')
        ticker = self.ib.reqMktData(contract, genericTickList='', snapshot=False, regulatorySnapshot=False)
        ticker.updateEvent += lambda ticker: asyncio.create_task(on_tick(ticker))
        self.tickers[symbol] = ticker

    def detach(self, symbol):
        if symbol in self.tickers:
            ticker = self.tickers[symbol]
            ticker.updateEvent.clear()
            self.ib.cancelMktData(ticker.contract)
            del self.tickers[symbol]

    def load_wishlist(self):
        engine = logic.engine().sql_alchemy().create_engine()
        main_query = f"""SELECT * FROM wishlist"""
        wishlist_df = pd.read_sql_query(main_query, engine)
        for _, row in wishlist_df.iterrows():
            symbol = row['symbol_id']
            print(f"----IB WebSocket Services Attach {symbol}----")
            self.attach(symbol)

    @classmethod
    def is_instance_none(cls):
        return cls._instance is None

    async def start(self):
        if not self._running:
            self._running = True
            self.load_wishlist()
            await asyncio.to_thread(self.running)

    async def stop(self):
        self._running = False

    def running(self):
        try:
            while self._running:
                print(f"----IB WebSocket Services running---- {datetime.datetime.now().isoformat()}")
                self.ib.sleep(1)
        except KeyboardInterrupt:
            print("Interrupted by user")
        finally:
            print("----IB WebSocket Services Disconnect----")
            self.ib.disconnect()
            with self._lock:
                type(self)._instance = None
            print("----IB WebSocket Services Destroyed----")

