import io
import contextlib

from cerebro.base import cerebroBase
from .strategy.test_strategy_1st import TestStrategy

from backtrader_plotting import Bokeh, OptBrowser, OptComponents
from backtrader_plotting.schemes import Tradimo

class StrategyOptimize(cerebroBase):

    def __init__(self, stdstats=False):
        super().__init__(stdstats)

    def run(self, symbol, cut_over):

        self.add_data(symbol, cut_over)

        self.configure()

        # Add Strategy
        self.cerebro.optstrategy(TestStrategy, map_period=range(7, 15, 1))

        # Run over everything
        results = self.cerebro.run(optreturn=True)

        # Optimization Browser
        b = Bokeh(style='bar', scheme=Tradimo(), output_mode='memory')
        return b, results

