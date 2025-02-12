import threading


from cerebro.strategy.live_strategy import LiveStrategy
from cerebro.strategy.strategy1stoperation import Strategy1stOperation
from home.services.ib.ib_interface import IBApi
import backtrader as bt
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

        return cls._instance

    def _on_attach(self, symbol):
        # setup Cerebro
        cerebro = bt.Cerebro()

        # Calculate fromdate and todate
        todate = datetime.now()
        fromdate = todate - timedelta(days=365)

        # Get IB Data Live
        ibstore = bt.stores.IBStore(host='127.0.0.1', port=7496, clientId=35)

        hourly_data = ibstore.getdata(
            # IB symbol
            dataname=symbol, sectype='STK', exchange='SMART', currency='',

            timeframe=bt.TimeFrame.Minutes,
            compression=60,
            historical=False,
            fromdate=fromdate,
            todate=todate,
            useRTH=True,
            what='TRADES',)

        # daily_data = IBDataLive(contract=contract, timeframe=bt.TimeFrame.Days)

        cerebro.adddata(hourly_data, name='Hourly')
        # cerebro.resampledata(hourly_data, timeframe=bt.TimeFrame.Days, name="Daily")

        # Add Strategy
        # cerebro.addstrategy(LiveStrategy)
        cerebro.addstrategy(Strategy1stOperation)

        # Add Broker
        broker = cerebro.getbroker()
        broker.setcommission(commission=0.001) # set commission

        # Start Live Trading
        cerebro.run()
        a = ""
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




