import contextlib
import io
import ray

from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo
from cerebro.cerebro_base import cerebroBase

# @ray.remote
class RayStrategyProfile(cerebroBase):

    def __init__(self, stdstats=False):
        super().__init__(stdstats)


    def run(self):
        # Prepare data
        self._prepare_data()
        # Configure
        self.configure()
        # Add Strategy
        self.cerebro.addstrategy(self.strategy, map_period=13)
        # Run cerebro
        self.result = self.cerebro.run(optreturn=True)
        return self.result

    def plot(self):
        st0 = self.result[0]
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
            # kwargs
            style='bar', plot_mode='single',
            # params
            scheme=Tradimo(), output_mode='memory')

        self.cerebro.plot(bokeh, iplot=False)
        # plot = bokeh.plot_html(bokeh.figurepages[0].model, template="smart_trader.html.j2")

        return analysis_result, bokeh.figurepages[0].model
