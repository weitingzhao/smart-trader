import ray
from bokeh_server import TestStrategy
from cerebro.cerebro_base import cerebroBase
from pandas.core.interchange.dataframe_protocol import DataFrame

@ray.remote
class RayStrategyOptimize(cerebroBase):

    def __init__(self, stdstats=False):
        super().__init__(stdstats)


    def run(self) -> DataFrame:
        # Prepare data
        self._prepare_data()
        # Configure
        self.configure()
        # Add Strategy
        self.cerebro.optstrategy(TestStrategy, map_period=range(7, 15, 1))

        # Run cerebro
        self.result = self.cerebro.run(optreturn=True)
        return self.result

