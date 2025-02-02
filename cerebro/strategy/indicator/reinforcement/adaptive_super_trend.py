import backtrader as bt
import numpy as np

class AdaptiveSuperTrend(bt.Indicator):
    lines = (
        'supertrend',
        'direction'
    )

    params = (
        ('atr_len', 10),
        ('factor', 3.0),
        ('training_data_period', 100),
        ('highvol', 0.75),
        ('midvol', 0.5),
        ('lowvol', 0.25),
    )

    def __init__(self):
        self.addminperiod(self.params.training_data_period)
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_len)
        self.volatility = self.atr

    def next(self):
        if len(self) < self.params.training_data_period:
            return

        training_data = self.volatility.get(size=self.params.training_data_period)
        upper = max(training_data)
        lower = min(training_data)

        high_volatility = lower + (upper - lower) * self.params.highvol
        medium_volatility = lower + (upper - lower) * self.params.midvol
        low_volatility = lower + (upper - lower) * self.params.lowvol

        hv = [v for v in training_data if abs(v - high_volatility) < abs(v - medium_volatility) and abs(v - high_volatility) < abs(v - low_volatility)]
        mv = [v for v in training_data if abs(v - medium_volatility) < abs(v - high_volatility) and abs(v - medium_volatility) < abs(v - low_volatility)]
        lv = [v for v in training_data if abs(v - low_volatility) < abs(v - high_volatility) and abs(v - low_volatility) < abs(v - medium_volatility)]

        hv_new = np.mean(hv) if hv else high_volatility
        mv_new = np.mean(mv) if mv else medium_volatility
        lv_new = np.mean(lv) if lv else low_volatility

        vdist_a = abs(self.volatility[0] - hv_new)
        vdist_b = abs(self.volatility[0] - mv_new)
        vdist_c = abs(self.volatility[0] - lv_new)

        distances = [vdist_a, vdist_b, vdist_c]
        centroids = [hv_new, mv_new, lv_new]

        cluster = distances.index(min(distances))
        assigned_centroid = centroids[cluster]

        src = (self.data.high + self.data.low) / 2
        upper_band = src + self.params.factor * assigned_centroid
        lower_band = src - self.params.factor * assigned_centroid

        prev_lower_band = self.lines.supertrend[-1] if len(self) > 1 else lower_band
        prev_upper_band = self.lines.supertrend[-1] if len(self) > 1 else upper_band

        lower_band = lower_band if lower_band > prev_lower_band or self.data.close[-1] < prev_lower_band else prev_lower_band
        upper_band = upper_band if upper_band < prev_upper_band or self.data.close[-1] > prev_upper_band else prev_upper_band

        if len(self) == 1 or np.isnan(self.lines.supertrend[-1]):
            direction = 1
        elif self.lines.supertrend[-1] == prev_upper_band:
            direction = -1 if self.data.close[0] > upper_band else 1
        else:
            direction = 1 if self.data.close[0] < lower_band else -1

        self.lines.supertrend[0] = lower_band if direction == -1 else upper_band
        self.lines.direction[0] = direction