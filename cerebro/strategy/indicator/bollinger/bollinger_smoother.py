import backtrader as bt
from ...decorator.nadaraya_watson_smoother import NadarayaWatsonSmoother


class BollingerSmoother(bt.Indicator):
    lines = ('mid', 'bolu', 'bold')
    params = (
        # default smoothing nadaraya smoothing length
        ('smooth_dist', 500),
        ('smooth_factor', 6), #"Smoothing Factor", tooltip = "Smoothing factor for the Nadaraya-Watson estimator"
        # group_boll = "Bollinger Bands Settings"
        ('period', 20),
        ('stdev', 3),
    )
    plotinfo = dict(subplot=False, plotname='BB') # Plot in the main chart
    plotlines = dict(
        mid=dict(color='blue'),
        bolu=dict(color='#FF5252', markersize=2),
        bold=dict(color='#0B9981', markersize=2),
    )

    def smooth_bollinger(self, data, period, dev_factor):
        # Calculate the original bollinger bands line
        bb = bt.indicators.BollingerBands(data, period=period, devfactor=dev_factor)
        # Smooth the middle band using Nadaraya-Watson
        top = NadarayaWatsonSmoother(bb.l.top, window=period, bandwidth= self.p.smooth_factor)
        bot = NadarayaWatsonSmoother(bb.l.bot, window=period, bandwidth=self.p.smooth_factor)
        return top.l.smoothed, bot.l.smoothed

    def __init__(self):
        # Calculate the smoothed bollinger bands
        bb = bt.indicators.BollingerBands(self.data, period=self.p.period, devfactor=self.p.stdev)
        self.l.mid = NadarayaWatsonSmoother(bb.l.mid, window=self.p.period, bandwidth=self.p.smooth_factor)

        self.l.bolu, self.l.bold = self.smooth_bollinger(self.data, self.p.period, self.p.stdev)

