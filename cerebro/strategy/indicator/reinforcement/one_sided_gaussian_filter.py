import logging
import backtrader as bt
import numpy as np

class OneSidedGaussianFilter(bt.Indicator):
    lines = ('out', 'smax', 'smin', 'sig')
    params = (
        ('smthper', 10),
        ('extrasmthper', 10),
        ('atrper', 21),
        ('mult', 0.628),
    )

    plotinfo = dict(subplot=False)  # Plot in the main chart

    def __init__(self):
        self.addminperiod(self.params.smthper + self.params.extrasmthper + self.params.atrper)
        self.atr = bt.indicators.ATR(self.data, period=self.params.atrper)

    def _twopoless(self, src, length):
        a1 = np.exp(-1.414 * np.pi / length)
        b1 = 2 * a1 * np.cos(1.414 * np.pi / length)
        coef2 = b1
        coef3 = -a1 * a1
        coef1 = 1 - coef2 - coef3
        filt = np.zeros_like(src)
        filt[0] = src[0]
        filt[1] = src[1]
        for i in range(2, len(src)):
            filt[i] = coef1 * src[i] + coef2 * filt[i - 1] + coef3 * filt[i - 2]
        return filt

    def _gaussian(self, size, x):
        return np.exp(-x * x * 9 / ((size + 1) * (size + 1)))

    def _fiblevels(self, length):
        levels = [0, 1]
        for _ in range(2, length):
            levels.append(levels[-1] + levels[-2])
        return levels

    def _gaussout(self, levels):
        perin = len(levels)
        arr_gauss = np.zeros((perin, perin))
        for k in range(perin):
            sum = 0
            for i in range(perin):
                if i >= levels[k]:
                    break
                arr_gauss[i, k] = self._gaussian(levels[k], i)
                sum += arr_gauss[i, k]
            for i in range(perin):
                if i >= levels[k]:
                    break
                arr_gauss[i, k] /= sum
        return arr_gauss

    def _smthMA(self, level, src, per):
        sum = 0
        levels = self._fiblevels(per)
        gtemp = self._gaussout(levels)
        for i in range(len(gtemp)):
            sum += gtemp[i, level] * np.roll(src, i)
        return sum

    def next(self):
        src = self.data.close.get(size=len(self.data))
        lmax = self.params.smthper + 1
        out1 = self._smthMA(self.params.smthper, src, lmax)
        out = self._twopoless(out1, self.params.extrasmthper)

        self.lines.out[0] = out[-1]  # Corrected to match Pine Script logic
        self.lines.sig[0] = out[-2] if len(out) > 1 else float('nan')

        if len(self) >= self.params.atrper:
            atr_value = self.atr[0]
            self.lines.smax[0] = self.lines.out[0] + atr_value * self.params.mult
            self.lines.smin[0] = self.lines.out[0] - atr_value * self.params.mult

            # self.log(
            #     f"out: {self.lines.out[0]}, sig: {self.lines.sig[0]}, smax: {self.lines.smax[0]}, smin: {self.lines.smin[0]}")
        else:
            self.lines.smax[0] = float('nan')
            self.lines.smin[0] = float('nan')
