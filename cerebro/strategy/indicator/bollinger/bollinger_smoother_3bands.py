import backtrader as bt
from ...decorator.nadaraya_watson_smoother import NadarayaWatsonSmoother


class BollingerSmoother3bands(bt.Indicator):
    lines = (
        'mid',
        'bolu_1', 'bold_1',
        'bolu_2', 'bold_2',
        'bolu_2b', 'bold_2b',
        'bolu_3', 'bold_3',
    )

    params = (
        ('repaint', False), #"Repaint Smoothing", tooltip = "This setting allows for repainting of the estimation"

        # default smoothing nadaraya smoothing length
        ('smooth_dist', 500),
        ('smooth_factor', 6), #"Smoothing Factor", tooltip = "Smoothing factor for the Nadaraya-Watson estimator"
        ('sens', 4),

        # group_boll = "Bollinger Bands Settings (Short, Medium, Long)"
        ('short_period', 20),
        ('short_stdev', 3),

        ('med_period', 75),
        ('med_stdev', 4),

        ('long_period', 100),
        ('long_stdev', 4.25),
    )

    plotinfo = dict(subplot=False, plotname='BB') # Plot in the main chart

    plotlines = dict(
        bolu_1=dict(color='#FF5252',  _fill_gt=('bolu_2', ('#FF5252', 0.10))),
        bolu_2=dict(color='#FFFFFF', _fill_gt=('bolu_1', ('#FF5252',0.10))),
        bolu_2b=dict(color='#FFFFFF',   _fill_gt=('bolu_3', ('#FF5252', 0.20))),
        bolu_3=dict(color='#FFFFFF', _fill_gt=('bolu_2b', ('#FF5252', 0.20))),

        bold_1=dict(color='#0B9981', _fill_gt=('bold_2', ('#4CAF50', 0.10))),
        bold_2=dict( color='#FFFFFF',  _fill_gt=('bold_1', ('#4CAF50', 0.10))),
        bold_2b=dict(color='#FFFFFF', _fill_gt=('bold_3', ('#4CAF50', 0.20))),
        bold_3=dict(markersize=0.0, color='#FFFFFF',  _fill_gt=('bold_2b', ('#4CAF50', 0.20))),
    )


    def smooth_bollinger(self, data, period, dev_factor):
        # Calculate the original bollinger bands line
        bb = bt.indicators.BollingerBands(data, period=period, devfactor=dev_factor)
        # Smooth the middle band using Nadaraya-Watson
        top = NadarayaWatsonSmoother(bb.l.top, window=period, bandwidth= self.p.smooth_factor)
        bot = NadarayaWatsonSmoother(bb.l.bot, window=period, bandwidth=self.p.smooth_factor)
        return top.l.smoothed, bot.l.smoothed


    def __init__(self):
        # Create the theme
        self.n = self.p.smooth_dist

        # Calculate the smoothed bollinger bands
        bb = bt.indicators.BollingerBands(self.data, period=self.p.short_period, devfactor=self.p.short_stdev)
        self.l.mid = NadarayaWatsonSmoother(bb.l.mid, window=self.p.short_period, bandwidth=self.p.smooth_factor)

        self.l.bolu_1, self.l.bold_1 = self.smooth_bollinger(self.data, self.p.short_period, self.p.short_stdev)
        self.l.bolu_2, self.l.bold_2 = self.smooth_bollinger(self.data, self.p.med_period, self.p.short_stdev)
        self.l.bolu_2b, self.l.bold_2b = self.smooth_bollinger(self.data, self.p.med_period, self.p.short_stdev)
        self.l.bolu_3, self.l.bold_3 = self.smooth_bollinger(self.data, self.p.long_period, self.p.med_stdev)

