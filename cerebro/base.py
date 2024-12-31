import pandas as pd
from numpy.ma.core import get_data

import backtrader as bt
from apps.common.models import *


class cerebroBase():

    def __init__(self, stdstats=False):
        # Create a cerebro entity
        self.cerebro = bt.Cerebro(stdstats=stdstats)
        self.data = None

    def get_data_csv_example(self):
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

    def get_data(self, symbol, cut_over):
        stock_data = (MarketStockHistoricalBarsByDay.objects
                      .filter(symbol=symbol, time__gte=cut_over).order_by('time'))

        # Convert the QuerySet to a DataFrame
        stock_data_df = pd.DataFrame(list(stock_data.values()))

        # Ensure the DataFrame has the required columns for Backtrader
        stock_data_df['datetime'] = pd.to_datetime(stock_data_df['time'])
        stock_data_df.set_index('datetime', inplace=True)
        stock_data_df = stock_data_df[['open', 'high', 'low', 'close', 'volume']]

        return stock_data_df

    def add_data(self, symbol, cut_over):

        stock_data_df = get_data(symbol, cut_over)

        # Add the Data Feed to Cerebro
        self.data = bt.feeds.PandasData(dataname=stock_data_df)
        self.data._name = f"{symbol}_{cut_over}"
        self.cerebro.adddata(self.data)

    def configure(self):

        # Set our desired cash start
        self.cerebro.broker.setcash(1000.0)
        # Add a FixedSize sizer according to the stake
        self.cerebro.addsizer(bt.sizers.FixedSize, stake=10)
        # Set the Commission - 0.1% ... divide by 100 to remove the %
        self.cerebro.broker.setcommission(commission=0.001)
        # Add the Analyzers
        self.cerebro.addanalyzer(bt.analyzers.SQN)
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)  # visualize the drawdown evol
        self.cerebro.addobserver(bt.observers.DrawDown)  # visualize the drawdown evol
