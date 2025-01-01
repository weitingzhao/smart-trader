import pandas as pd
import backtrader as bt
from pandas.core.interchange.dataframe_protocol import DataFrame
import inspect

class cerebroBase():

    def __init__(self, stdstats=False):
        # Create a cerebro entity
        self.cerebro = bt.Cerebro(stdstats=stdstats)
        self.data = None
        self.data_name = None
        self.data_df = None
        self.result = None
        self.strategy  = None


    def set_data(self, data_name:str, data_df: DataFrame):
        # Set Data Name
        self.data_name = data_name

        # Set Data Frane
        # Ensure the DataFrame has the required columns for Backtrader
        data_df['datetime'] = pd.to_datetime(data_df['time'])
        data_df.set_index('datetime', inplace=True)
        data_df = data_df[['open', 'high', 'low', 'close', 'volume']]
        self.data_df = data_df

    def _prepare_data(self):
        # Add the Data Feed to Cerebro
        self.data = bt.feeds.PandasData(dataname=self.data_df)
        self.data._name = self.data_name
        self.cerebro.adddata(self.data)

    def set_strategy(self, strategy):
        self.strategy = strategy

    def get_strategy_source_code(self):
        if self.strategy is not None:
            return inspect.getsource(self.strategy)
        else:
            return None

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