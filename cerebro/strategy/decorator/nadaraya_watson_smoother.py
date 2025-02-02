import backtrader as bt
import numpy as np

# Gaussian kernel function for Nadaraya-Watson smoother
def gaussian_kernel(x, h):
    return np.exp(-0.5 * (x / h) ** 2) / (np.sqrt(2 * np.pi) * h)

# Custom Nadaraya-Watson Smoother
class NadarayaWatsonSmoother(bt.Indicator):
    lines = ('smoothed',)  # Smoothed line
    params = (
        ('window', 20),  # Lookback window size
        ('bandwidth', 5),  # Kernel bandwidth
    )

    def __init__(self):
        self.addminperiod(self.params.window)

    def next(self):
        n = self.params.window
        h = self.params.bandwidth
        weights = np.zeros(n)
        smoothed = 0.0

        # Ensure we have enough data to perform smoothing
        if len(self.data) < n:
            self.lines.smoothed[0] = self.data[0]
            return

        # Calculate weights and smoothed value
        for i in range(-n + 1, 1):
            x = -i
            weights[-i] = gaussian_kernel(x, h)
            smoothed += self.data[i] * weights[-i]

        # Normalize by sum of weights
        weight_sum = np.sum(weights)
        if weight_sum > 0:
            self.lines.smoothed[0] = smoothed / weight_sum
        else:
            self.lines.smoothed[0] = self.data[0]  # Fallback

