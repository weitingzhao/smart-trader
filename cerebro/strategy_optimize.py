import io
import contextlib
import json
import os
import pickle

from bokeh.document import Document
from cerebro.base import cerebroBase
from core import settings
from .strategy.test_strategy_1st import TestStrategy

from backtrader_plotting import Bokeh, OptBrowser, OptComponents
from backtrader_plotting.schemes import Tradimo
from jinja2 import Environment, PackageLoader
from backtrader_plotting.bokeh import utils


class StrategyOptimize(cerebroBase):

    def __init__(self, stdstats=False):
        super().__init__(stdstats)

    def run(self, symbol, cut_over):
        result_file_path = os.path.join(settings.BASE_DIR, 'media', f'{symbol}_{cut_over}.pkl')

        self.add_data(symbol, cut_over)

        self.configure()

        # Add Strategy
        self.cerebro.optstrategy(TestStrategy, map_period=range(7, 15, 1))

        # Run over everything
        results = self.cerebro.run(optreturn=True)

        # Save the result to a local file
        with open(result_file_path, 'wb') as result_file:
            pickle.dump(results, result_file)

        return results
