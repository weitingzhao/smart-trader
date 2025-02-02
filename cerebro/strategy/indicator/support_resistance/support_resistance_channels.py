import backtrader as bt

class SupportResistanceChannels(bt.Indicator):
    lines = ('support', 'resistance')
    params = (('period', 20),)

    plotinfo = dict(subplot=False, plotname='Support/Resistance Channels')

    plotlines = dict(
        support=dict(color='black', linestyle='--'),
        resistance=dict(color='black', linestyle='--')
    )

    def __init__(self):
        self.addminperiod(self.p.period)
        self.l.support = bt.indicators.Lowest(self.data.low, period=self.p.period)
        self.l.resistance = bt.indicators.Highest(self.data.high, period=self.p.period)

