import redis
import pandas as pd
import backtrader as bt
from apps.tasks.controller.instance import Instance
import json

class cerebroBase():

    def __init__(self, stdstats=False):
        # Create a cerebro entity
        self.cerebro = bt.Cerebro(stdstats=stdstats)
        self.data_condition = None
        self.data_name = None
        self.data = None
        self.data_df = None
        self.result = None
        self.strategy  = None
        self.instance = Instance()
        # Message
        self.sms_need = False
        self.msg_group_name = 'stock_bt_result'
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def set_data(self, data_json : object):


        # Extract symbols from JSON
        symbols = data_json.get('symbols')
        # Continue with the rest of your logic
        period = data_json.get('period')
        interval = data_json.get('interval')
        since = data_json.get('since')
        self.sms_need = True if data_json.get('sms') is True else False

        # Assign to self.data_meta
        self.data_condition = {'symbols': symbols, 'period': period, 'interval': interval, 'since': since}

        # Build the meta dictionary based on input
        meta = {
            'error': 'false',
            'output': '',
            'status': 'STARTED',
            'initial': 'false',
            'leftover': symbols.split('|'),
            'done': []
        }

        # Prepare args dictionary
        args = f"snapshot=True,period='{period}',interval='{interval}',symbols={symbols},since={since}"

        # Call the function to get Yahoo data
        worker = self.instance.service().fetching().stock_hist_bars_yahoo()
        error_list, meta = worker.run(meta=meta, task_result=None, args=args, is_test=False)
        if len(error_list) > 0:
            return
        yahoo_data = worker.snapshot
        # Convert yahoo_data to a DataFrame
        yahoo_data_df = pd.DataFrame(yahoo_data)

        # # Step 1.  Prepare data as Data Frame
        # Filter the DataFrame by the 'since' date
        stock_data_df = yahoo_data_df[yahoo_data_df.index >= since]
        stock_data_df.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume',
        }, inplace=True)
        # Remove the 'dividends' and 'stocksplits' columns
        stock_data_df.drop(columns=['Dividends', 'Stock Splits'], inplace=True)
        stock_data_df.rename_axis('datetime', inplace=True)
        # Add the openinterest column and set it to 0
        stock_data_df['openinterest'] = 0

        # Set Data Name
        self.data_name = f'{symbols}-{since}'
        self.data_df = stock_data_df

    def _prepare_data(self):
        # Add the Data Feed to Cerebro
        self.data = bt.feeds.PandasData(dataname=self.data_df)
        self.data._name = self.data_name
        self.cerebro.adddata(self.data)

    def set_strategy(self, strategy):
        self.strategy = strategy

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

    def sent_messge(self):
        try:
            if self.sms_need is False or  self.result is None:
                return

            # key = ticker.contract.symbol
            detail = {
                'atr': self.result[0].atr.array[-1],
                'bbands': {
                    'upper': self.result[0].bbands.lines.bolu.array[-1],
                    'middle': self.result[0].bbands.lines.mid.array[-1],
                    'lower': self.result[0].bbands.lines.bold.array[-1]
                },
                'rs': {
                    'upper': { 'max': 2.9, 'min': 2.1},
                    'lower': { 'max': 1.9, 'min': 1.1}
                },
                'rs2': {
                    'upper': {'max': 2.8, 'min': 2.2},
                    'lower': {'max': 1.8, 'min': 1.2}
                }
            }
            json_str = json.dumps({
                'type': 'bt_symbol',
                'meta': self.data_condition,
                'indicator' : detail
            })

            print(f"BT->Redis->: {json_str}")
            self.redis_client.publish(self.msg_group_name, json_str)
        except Exception as e:
            print(str(e))

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