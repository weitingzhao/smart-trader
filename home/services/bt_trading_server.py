import threading

from ibapi.contract import Contract

from cerebro.strategy.live_strategy import LiveStrategy
from home.services.ib.ib_interface import IBApi
import backtrader as bt
# from backtrader.feeds import ibdata
import time
from datetime import datetime, timedelta
from home.services.ticker_sever import TickerSever

class BTTradingService(TickerSever):
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(
                    cls,
                    server_name="BackTrader Live",
                    group_name="trading_live",
                    loop_period= 1
                )

                # Services
                cls.ib = IBApi()
                cls.ib.connect('127.0.0.1', 7497, clientId=1) # Connect to IB Gateway 7496 is live trading

        return cls._instance

    def _on_attach(self, symbol):
        # setup Cerebro
        cerebro = bt.Cerebro()

        # Add data source
        # Create Contract
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"

        # Calculate fromdate and todate
        todate = datetime.now()
        fromdate = todate - timedelta(days=365)

        # Get IB Data Live
        hourly_data = bt.feeds.IBData(
            contract = contract,
            timeframe = bt.TimeFrame.Minutes,
            compression = 60,
            historical=False,
            fromdate=fromdate,
            todate=todate,
            useRTH=True,
            what='TRADES'
        )
        # daily_data = IBDataLive(contract=contract, timeframe=bt.TimeFrame.Days)

        cerebro.addstrategy(hourly_data, name='Hourly')
        cerebro.resampledata(hourly_data, timeframe=bt.TimeFrame.Days, name="Daily")

        # Add Strategy
        cerebro.addstrategy(LiveStrategy)

        # Add Broker
        broker = cerebro.getbroker()
        broker.setcommission(commission=0.001) # set commission

        # Start Live Trading
        cerebro.run()
        return cerebro


    def _on_detach(self, symbol, ticker):
        ticker.updateEvent.clear()
        self.ib.cancelMktData(ticker.contract)


    def _running_cycle(self):
        time.sleep(self.loop_period)
        for symbol, cerebro in self.tickers.items():
            # 实时更新仓位信息
            positions = cerebro.getpositions()
            # 打印实时统计
            print(f"\nReal-time Statistics:")
            broker = cerebro.getbroker()
            if broker is not None:
                print(f"Account Value: { broker.getvalue():.2f}")
                print(f"Cash: {broker.getcash():.2f}")
                print(f"Positions: {positions}")



    def _init_load(self):
        self.attach("NVDA")
        pass


    def _before_final_shutdown(self):
        self.ib.disconnect()




