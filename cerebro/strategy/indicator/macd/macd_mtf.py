import backtrader as bt
import numpy as np

class MACD_MTF(bt.Indicator):
    lines = ('macd', 'signal', 'histogram', 'hline',)

    params = (
        #periods
        ('fast_length', 12),
        ('slow_length', 26),
        ('signal_length', 9),

        ('use_current_res', True),
        ('res_custom', '60'),
        ('smd', True),
        ('sd', True),
        ('sh', True),

        #color change
        ('macd_color_change', True),
        ('hist_color_change', True),
    )

    plotinfo = dict(subplot=True, plotname='MACD_MTF')

    plotlines = dict(
        macd=dict(color='lime', linewidth=4),
        signal=dict(color='yellow', linewidth=2),
        histogram=dict(color='gray', linewidth=4, style='histogram'),
        hline=dict(_plotskip=False, color='black', linestyle='solid', linewidth=2)
    )

    def __init__(self):
        self.addminperiod(max(self.p.fast_length, self.p.slow_length, self.p.signal_length))
        self.source = self.data.close

        self.fast_ma = bt.indicators.EMA(self.source, period=self.p.fast_length)
        self.slow_ma = bt.indicators.EMA(self.source, period=self.p.slow_length)

        self.macd = self.fast_ma - self.slow_ma
        self.signal = bt.indicators.SMA(self.macd, period=self.p.signal_length)
        self.histogram = self.macd - self.signal

    def next(self):
        self.lines.macd[0] = self.macd[0]
        self.lines.signal[0] = self.signal[0]
        self.lines.histogram[0] = self.histogram[0]

        if self.p.hist_color_change:
            if self.histogram[0] > self.histogram[-1] and self.histogram[0] > 0:
                self.plotlines.histogram.color = 'aqua'
            elif self.histogram[0] < self.histogram[-1] and self.histogram[0] > 0:
                self.plotlines.histogram.color = 'blue'
            elif self.histogram[0] < self.histogram[-1] and self.histogram[0] <= 0:
                self.plotlines.histogram.color = 'red'
            elif self.histogram[0] > self.histogram[-1] and self.histogram[0] <= 0:
                self.plotlines.histogram.color = 'maroon'
            else:
                self.plotlines.histogram.color = 'yellow'

        if self.p.macd_color_change:
            if self.macd[0] >= self.signal[0]:
                self.plotlines.macd.color = 'lime'
                self.plotlines.signal.color = 'yellow'
            else:
                self.plotlines.macd.color = 'red'
                self.plotlines.signal.color = 'yellow'