import backtrader as bt
import numpy as np

class SupportResistanceBands(bt.Indicator):
    lines = ('support', 'resistance')
    params = (
        ('period', 10),

        # Calculated using Highest/Lowest levels in 300 bars
        ('channel_width', 5), # 1 - 8 # Maximum Channel Width %
        ('min_strength', 1), # 1 # Channel must contain at least 2 Pivot Points
        ('max_num_sr', 6),  # 1 - 10 # Maximum number of Support/Resistance Channels to Show
        ('loopback', 290), # 100 - 400 # While calculating S/R levels it checks Pivots in Loopback Period
    )

    plotinfo = dict(subplot=False, plotname='Support/Resistance Channels')

    plotlines = dict(
        support=dict(color='lime', linestyle='--'),
        resistance=dict(color='red', linestyle='--')
    )

    def __init__(self):
        self.addminperiod(self.p.period)
        self.pivot_highs = []
        self.pivot_lows = []
        self.sr_levels = []

    def next(self):
        # Calculate pivot points
        if len(self.data) >= self.p.period * 2 + 1:
            high = self.data.high.get(size=self.p.period * 2 + 1)
            low = self.data.low.get(size=self.p.period * 2 + 1)
            if high[self.p.period] == max(high):
                self.pivot_highs.append((self.data.datetime[0], high[self.p.period]))
            if low[self.p.period] == min(low):
                self.pivot_lows.append((self.data.datetime[0], low[self.p.period]))

        # Remove old pivot points
        self.pivot_highs = [(dt, val) for dt, val in self.pivot_highs if self.data.datetime[0] - dt <= self.p.loopback]
        self.pivot_lows = [(dt, val) for dt, val in self.pivot_lows if self.data.datetime[0] - dt <= self.p.loopback]

        # Calculate support and resistance levels
        self.sr_levels = self.calculate_sr_levels()

        # Plot support and resistance levels
        if self.sr_levels:
            self.lines.support[0] = self.sr_levels[0][1]
            self.lines.resistance[0] = self.sr_levels[0][0]
        else:
            self.lines.support[0] = np.nan
            self.lines.resistance[0] = np.nan

    def calculate_sr_levels(self):
        sr_levels = []
        for pivot in self.pivot_highs + self.pivot_lows:
            level = self.find_sr_level(pivot)
            if level:
                sr_levels.append(level)
        sr_levels = sorted(sr_levels, key=lambda x: x[2], reverse=True)[:self.p.max_num_sr]
        return sr_levels

    # find / create SR channel of a pivot point
    def find_sr_level(self, pivot):
        high, low = pivot[1], pivot[1]
        strength = 0
        for other_pivot in self.pivot_highs + self.pivot_lows:
            if abs(other_pivot[1] - pivot[1]) <= self.p.channel_width:
                high = max(high, other_pivot[1])
                low = min(low, other_pivot[1])
                strength += 1
        if strength >= self.p.min_strength:
            return (high, low, strength)
        return None