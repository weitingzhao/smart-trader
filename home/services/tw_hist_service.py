import redis
import asyncio
import threading
from cerebro.datafeed_tradingview import TvDatafeed, Interval


class TradingViewHistService:
    _instance = None
    _lock = threading.Lock()

    username = None
    password = None

    tv = TvDatafeed(username, password)

    # symbol = tv.search_symbol("TSLA", exchange="NASDAQ")

    # index
    hims_index_data = tv.get_hist(symbol='HIMS', exchange='NYSE', interval=Interval.in_1_hour,n_bars=1000)

    hims_extended_price_data = tv.get_hist(symbol="HIMS",exchange='NYSE', interval=Interval.in_1_hour,n_bars=1000, extended_session=True)

    # futures continuous contract
    # nifty_futures_data = tv.get_hist(symbol='NIFTY',exchange='NSE',interval=Interval.in_1_hour,n_bars=1000,fut_contract=1)

    # crudeoil
    # crudeoil_data = tv.get_hist(symbol='CRUDEOIL',exchange='MCX',interval=Interval.in_1_hour,n_bars=5000,fut_contract=1)

    # downloading data for extended market hours
    # extended_price_data = tv.get_hist(symbol="EICHERMOT",exchange="NSE",interval=Interval.in_1_hour,n_bars=500, extended_session=False)

    a = 1



