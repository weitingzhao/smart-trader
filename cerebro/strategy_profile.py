import io
import contextlib

from cerebro.base import cerebroBase
from .strategy.test_strategy_1st import TestStrategy

from backtrader_plotting import Bokeh, OptBrowser, OptComponents
from backtrader_plotting.schemes import Tradimo

class StrategyProfile(cerebroBase):

    def __init__(self, stdstats=False):
        super().__init__(stdstats)

    def run(self, symbol, cut_over):

        self.add_data(symbol, cut_over)

        self.configure()

        # Add Strategy
        self.cerebro.addstrategy(TestStrategy, map_period=13)

        # Run over everything
        results = self.cerebro.run(optreturn=True)

        st0 = results[0]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            for alyzer in st0.analyzers:
                alyzer.print()
        analysis_result = output.getvalue()
        output.close()

        # Print out the starting conditions
        print('Starting Portfolio Value: %.2f' % self.cerebro.broker.getvalue())
        print('Final Portfolio Value: %.2f' % self.cerebro.broker.getvalue())

        # Save the plot as an image
        # Plot the result
        bokeh = Bokeh(
            style='bar', plot_mode='single', scheme=Tradimo(), output_mode='memory')
        self.cerebro.plot(bokeh, iplot=False)
        plot = bokeh.plot_html(bokeh.figurepages[0].model, template="smart_trader.html.j2")

        return analysis_result, plot