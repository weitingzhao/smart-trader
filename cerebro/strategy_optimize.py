import io
import contextlib
from bokeh.document import Document
from cerebro.base import cerebroBase
from .strategy.test_strategy_1st import TestStrategy

from backtrader_plotting import Bokeh, OptBrowser, OptComponents
from backtrader_plotting.schemes import Tradimo
from jinja2 import Environment, PackageLoader
from backtrader_plotting.bokeh import utils


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
        bokeh = Bokeh(style='bar', scheme=Tradimo(), output_mode='memory')

        browser = OptBrowser(bokeh, results)
        model = browser.build_optresult_model()

        # browser.start()

        return model, results
