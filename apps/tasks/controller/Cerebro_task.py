import io
import base64
import contextlib
import pandas as pd
import backtrader as bt
from typing import List
from logics.logic import Logic
from .base_task import BaseTask
from apps.common.models import *
from django_celery_results.models import TaskResult

# import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt

from backtrader_plotting import Bokeh,OptBrowser
from backtrader_plotting.schemes import Tradimo

class CerebroTask(BaseTask):

    def __init__(self, celery, data):
        super().__init__(celery, data)

    def job_scripts(self) -> List:
        return [
            {"name":"Test Daily",
             "options":[
                 {
                     "text": "DAVE at Date Since 2024-01-01",
                     "value": "symbol=DAVE,cut_day=2024-01-01"
                 },
             ]},
        ]

    def _worker_run(self, script_name: str, logic : Logic, task_result: TaskResult, meta: dict, args: str = None):
        if script_name == 'Test Daily':
            run_cerebro_strategy('DAVE', '2024-01-01')


def run_cerebro_strategy(symbol, cut_over):
    cerebro = init_cerebro(symbol, cut_over)
    cerebro.addstrategy(TestStrategy, map_period=13)
    # Run over everything
    results = cerebro.run(optreturn=True)
    return plot_cerebro(cerebro, results)

def opt_cerebro_strategy(symbol, cut_over):
    cerebro = init_cerebro(symbol, cut_over)
    cerebro.optstrategy(TestStrategy, map_period=range(7,15,1))
    # Run over everything
    results = cerebro.run(optreturn=True)
    opt_cerebro(cerebro, results)


def init_cerebro(symbol, cut_over):
    stock_data = (MarketStockHistoricalBarsByDay.objects
                  .filter(symbol=symbol, time__gte=cut_over).order_by('time'))

    # Convert the QuerySet to a DataFrame
    stock_data_df = pd.DataFrame(list(stock_data.values()))

    # Ensure the DataFrame has the required columns for Backtrader
    stock_data_df['datetime'] = pd.to_datetime(stock_data_df['time'])
    stock_data_df.set_index('datetime', inplace=True)
    stock_data_df = stock_data_df[['open', 'high', 'low', 'close', 'volume']]

    # Create a cerebro entity
    cerebro = bt.Cerebro() #stdstats=False

    # Add the Data Feed to Cerebro
    data = bt.feeds.PandasData(dataname=stock_data_df)
    data._name = f"{symbol}_{cut_over}"
    cerebro.adddata(data)
    # Set our desired cash start
    cerebro.broker.setcash(1000.0)
    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    # Set the Commission - 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.001)
    # Add the Analyzers
    cerebro.addanalyzer(bt.analyzers.SQN)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)  # visualize the drawdown evol
    cerebro.addobserver(bt.observers.DrawDown)  # visualize the drawdown evol

    return cerebro

def plot_cerebro(cerebro, results):

    st0 = results[0]
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        for alyzer in st0.analyzers:
            alyzer.print()
    analysis_result = output.getvalue()
    output.close()

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Save the plot as an image
    # Plot the result
    bokeh = Bokeh(
        style='bar', plot_mode='single', scheme=Tradimo(), output_mode='memory')
    cerebro.plot(bokeh, iplot=False)
    plot = bokeh.plot_html(bokeh.figurepages[0].model, template="smart_trader.html.j2")

    return analysis_result, plot

def opt_cerebro(cerebro, results):
    # output = io.StringIO()
    # with contextlib.redirect_stdout(output):
    #     for alyzer in st0.analyzers:
    #         alyzer.print()
    # analysis_result = output.getvalue()
    # output.close()

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Optimization Browser
    b = Bokeh(style='bar', scheme=Tradimo(), output_mode='memory')
    browser = OptBrowser(b, results)
    browser.start()



def get_data_csv_example():
    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    # modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # datapath = os.path.join(modpath, 'datas/orcl-1995-2014.txt')
    # # Create a Data Feed
    # data = bt.feeds.YahooFinanceCSVData(
    #     dataname=datapath,
    #     # Do not pass values before this date
    #     fromdate=datetime.datetime(2000, 1, 1),
    #     # Do not pass values after this date
    #     todate=datetime.datetime(2000, 12, 31),
    #     reverse=False)
    pass

class TestStrategy(bt.Strategy):
    params = (
        ('map_period', 10),
        ('printlog', False),
    )


    def log(self, txt, dt=None, doprint=False):
        ''' Logging function for this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))



    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.data_close = self.datas[0].close

        # To keep track of pending orders
        self.order = None
        self.buy_price = None
        self.buy_comm = None
        self.bar_executed = 0

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.map_period)

        # Indicators for the plotting show
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        bt.indicators.WeightedMovingAverage(self.datas[0], period=25, subplot=True)
        bt.indicators.StochasticSlow(self.datas[0])
        bt.indicators.MACDHisto(self.datas[0])

        rsi = bt.indicators.RSI(self.datas[0])
        bt.indicators.SmoothedMovingAverage(rsi, period=10)
        bt.indicators.ATR(self.datas[0], plot=False)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                self.buy_price = order.executed.price
                self.buy_comm = order.executed.comm
            else: # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None


    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))


    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.data_close[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # Not yet ... we MIGHT BUY if ...
            if self.data_close[0] > self.sma[0]:
                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.data_close[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()
        else:
            if self.data_close[0] < self.sma[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.data_close[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()


    def stop(self):
        self.log('(MA Period %2d) Ending Value %.2f' %
                 (self.params.map_period, self.broker.getvalue()), doprint=True)
