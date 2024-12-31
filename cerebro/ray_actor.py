import os
import pickle

import ray
import math
import time
import random

from pandas.core.interchange.dataframe_protocol import DataFrame

from bokeh_server import TestStrategy
from cerebro.base import cerebroBase
import pandas as pd
from numpy.ma.core import get_data
import backtrader as bt
from apps.common.models import *
from core import settings



@ray.remote
class StrategyOptimizeRay:

    def __init__(self, stdstats=False):
        # Create a cerebro entity
        self.cerebro = bt.Cerebro(stdstats=stdstats)
        self.data = None

    def get_data(self, data_df: DataFrame) -> DataFrame:

        # Ensure the DataFrame has the required columns for Backtrader
        data_df['datetime'] = pd.to_datetime(data_df['time'])
        data_df.set_index('datetime', inplace=True)
        data_df = data_df[['open', 'high', 'low', 'close', 'volume']]

        return data_df

    def run(self, symbol, cut_over, data_df: DataFrame) -> DataFrame:
        # result_file_path = os.path.join(settings.BASE_DIR, 'media', f'{symbol}_{cut_over}.pkl')
        stock_data_df = self.get_data(data_df)

        # Add the Data Feed to Cerebro
        self.data = bt.feeds.PandasData(dataname=stock_data_df)
        self.data._name = f"{symbol}_{cut_over}"
        self.cerebro.adddata(self.data)

        self.configure()

        # Add Strategy
        self.cerebro.optstrategy(TestStrategy, map_period=range(7, 15, 1))

        # Run over everything
        results = self.cerebro.run(optreturn=True)

        # # Save the result to a local file
        # with open(result_file_path, 'wb') as result_file:
        #     pickle.dump(results, result_file)

        return results


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


