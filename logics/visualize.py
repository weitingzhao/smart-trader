from argparse import ArgumentParser
from logics.utilities.plugin import Plugin
from logics.research import Research
from logics.visualizes import BaseChart
from logics import visualizes as chart


class Visualize(BaseChart):
    def __init__(self, analyse: Research):
        super().__init__(analyse)

    def local_tradings(
            self,
            args,
            parser: ArgumentParser
    ) -> chart.TradingPatternChart:
        return chart.TradingPatternChart(
            self._analyse,
            args,
            Plugin(),
            parser)

    def web_visualization(self) -> chart.TradingVisualizeChart:
        return chart.TradingVisualizeChart(self._analyse)