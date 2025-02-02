import backtrader as bt
import numpy as np

class CustomMACDHisto(bt.indicators.MACDHisto):
    plotlines = dict(
        histo=dict(
            _method='bar',
            color='#000000',
            _fill_gt=(0, '#0B9981'),
            _fill_lt=(0, '#FF5252')
        )
    )