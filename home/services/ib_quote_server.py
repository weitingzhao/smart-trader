import asyncio
import threading
from ib_insync import *
import pandas as pd
import json
from business import logic
from home.services.ticker_sever import TickerSever


class IntBrokersQuoteService(TickerSever):
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(
                    cls,
                    server_name="IB WebSocket",
                    group_name="stock_quote",
                    loop_period= 1
                )

                # Services
                cls.ib = IB()
                cls.ib.connect('127.0.0.1', 7496, clientId=1)

        return cls._instance

    def _init_load(self):
        engine = logic.engine().sql_alchemy().create_engine()
        main_query = f"""SELECT * FROM wishlist"""
        wishlist_df = pd.read_sql_query(main_query, engine)
        for _, row in wishlist_df.iterrows():
            symbol = row['symbol_id']
            print(f"----{self.server_name} Services Attach {symbol}----")
            self.attach(symbol)

    def _on_attach(self, symbol):
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
        return ticker

    def _on_detach(self, symbol, ticker):
        ticker.updateEvent.clear()
        self.ib.cancelMktData(ticker.contract)






