import threading
from cerebro.datafeed_tradingview import TvDatafeed, Interval
from django.conf import settings
from home.services.ticker_sever import TickerSever
import pandas as pd
from business import logic
from sqlalchemy import text

class TradingViewHistService(TickerSever):
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(
                    cls,
                    server_name="TradingView WebSocket",
                    group_name="stock_hist",
                    loop_period= 10,
                )

                # Services
                cls.username = settings.TW_USERNAME
                cls.password = settings.TW_PASSWORD
                cls.tw = TvDatafeed(cls.username, cls.password)

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
        engine = logic.engine().sql_alchemy().create_engine()

        # <- Symbol Market
        market = pd.read_sql_query(f"""
            SELECT market FROM market_symbol WHERE symbol = '{symbol}'
        """, engine)['market'].iloc[0]

        # <- Last Time of Symbol History
        max_time = pd.read_sql_query(f"""
            SELECT MAX(time) as max_time
            FROM market_stock_hist_bars_day_ts
            WHERE symbol = '{symbol}'
        """, engine)['max_time'].iloc[0]

        if pd.isnull(max_time):
            n_bars = 1000
        else:
            # Refresh wishlist time flag
            current_date = pd.Timestamp.now().normalize()
            max_time = pd.Timestamp(max_time).normalize()
            n_bars = (current_date - max_time).days + 5
            # -> Update Last Time into Wishlist last_sync_time_day field
            with engine.connect() as connection:
                update_sql = f"""
                    UPDATE wishlist
                    SET last_sync_time_day = '{max_time}'
                    WHERE symbol_id = '{symbol}'
                """
                connection.execute(text(update_sql))
                connection.commit()

        # <- Wishlist record for the given symbol
        wishlist = pd.read_sql_query(f"""
            SELECT * FROM wishlist WHERE symbol_id = '{symbol}'
        """, engine).iloc[0]

        # Last step <- Pulling the historical data from TradingView
        stock_hist = self.tw.get_hist(
            symbol=symbol, exchange=market,
            interval=Interval.in_daily, n_bars=n_bars, extended_session=False)

        if stock_hist is not None and not stock_hist.empty:
            stock_hist['symbol'] = stock_hist['symbol'].apply(lambda x: x.split(':')[1] if ':' in x else x)
            self.merge_stock_hist(engine, stock_hist)

        return wishlist

    def merge_stock_hist(self, engine, stock_hist):

        with engine.connect() as connection:
            for _, row in stock_hist.iterrows():
                symbol = row['symbol']
                time = _.date()
                open = row['open']
                high = row['high']
                low = row['low']
                close_price = row['close']
                volume = row['volume']

                merge_query = text(f"""
                    INSERT INTO market_stock_hist_bars_day_ts (
                        symbol, time, open, high, low, close, volume, dividend, stock_splits)
                    VALUES (
                        :symbol, :time, :open, :high, :low, :close, :volume, 0, 0)
                    ON CONFLICT (symbol, time)
                    DO UPDATE SET 
                        open = EXCLUDED.open, high = EXCLUDED.high, 
                        low = EXCLUDED.low, close = EXCLUDED.close, 
                        volume = EXCLUDED.volume, dividend = 0, stock_splits = 0
                """)
                connection.execute(merge_query, {
                    'symbol': symbol,
                    'time': time,
                    'open': open,
                    'high': high,
                    'low': low,
                    'close': close_price,
                    'volume': volume
                })
            connection.commit()


    # # symbol = tv.search_symbol("TSLA", exchange="NASDAQ")
    #
    # # index
    # hims_index_data = tv.get_hist(symbol='HIMS', exchange='NYSE', interval=Interval.in_1_hour,n_bars=1000)
    #
    # hims_extended_price_data = tv.get_hist(symbol="HIMS",exchange='NYSE', interval=Interval.in_1_hour,n_bars=1000, extended_session=True)
    #
    # # futures continuous contract
    # # nifty_futures_data = tv.get_hist(symbol='NIFTY',exchange='NSE',interval=Interval.in_1_hour,n_bars=1000,fut_contract=1)
    #
    # # crudeoil
    # # crudeoil_data = tv.get_hist(symbol='CRUDEOIL',exchange='MCX',interval=Interval.in_1_hour,n_bars=5000,fut_contract=1)
    #
    # # downloading data for extended market hours
    # # extended_price_data = tv.get_hist(symbol="EICHERMOT",exchange="NSE",interval=Interval.in_1_hour,n_bars=500, extended_session=False)
    #
    # a = 1