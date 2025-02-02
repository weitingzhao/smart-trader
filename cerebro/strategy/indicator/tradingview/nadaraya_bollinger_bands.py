import backtrader as bt
import numpy as np

class Palette:
    def __init__(self, bear, bull, shade1_bear, shade1_bull, shade2_bear, shade2_bull):
        self.bear = bear
        self.bull = bull
        self.shade1_bear = shade1_bear
        self.shade1_bull = shade1_bull
        self.shade2_bear = shade2_bear
        self.shade2_bull = shade2_bull

def create_palette(bear, bull, alpha1=1, alpha2=2):
    shade1 = int(100 * alpha1)
    shade2 = int(100 * alpha2)
    shade1_bear = (bear[0], bear[1], bear[2], shade1)
    shade1_bull = (bull[0], bull[1], bull[2], shade1)
    shade2_bear = (bear[0], bear[1], bear[2], shade2)
    shade2_bull = (bull[0], bull[1], bull[2], shade2)
    return Palette(bear, bull, shade1_bear, shade1_bull, shade2_bear, shade2_bull)

class NadarayaBollingerBands(bt.Indicator):
    lines = ('upper_band_1', 'lower_band_1',
             'upper_band_2', 'lower_band_2',
             'upper_band_3', 'lower_band_3',
             'upper_band_4', 'lower_band_4')

    params = dict(
        # group_smoothing="smoothing"
        smoothing_factor=6,
        repaint=False,
        sens=4,

        # group_boll = "Bollinger Bands Settings (Short, Medium, Long)"
        short_period=20,
        short_stdev=3,

        med_period=75,
        med_stdev=4,

        long_period=100,
        long_stdev=4.25,

        # group_graphics="Plots and Labels"
        label_src='Close',
        labels=True,
        plots=True,
        plot_thickness=2,

        bands_lvl1=True,
        bands_lvl2=True,

        # grp="Color Theme"
        pallete_bear='red',
        pallete_bull='green',
        alpha1=0.90,
        alpha2=0.85,

        # grp_n="Notifications"
        notifs=False,
    )


    def gaussian_kernel(self, x, h):
        return np.exp(-1 * ((x ** 2) / (2 * (h ** 2))))


    def bollingers(self, tp, n, factor=3):
        bolu = bt.indicators.SimpleMovingAverage(tp, period=n) + (factor * bt.indicators.StandardDeviation(tp, period=n))
        bold = bt.indicators.SimpleMovingAverage(tp, period=n) - (factor * bt.indicators.StandardDeviation(tp, period=n))
        return bolu, bold

    def add_cols(self, mat, h_n=1):
        sum_array = []
        for i in range(len(mat)):
            sum_array.append(np.sum(mat[i]) / h_n)
        return sum_array

    def nadaraya(self, src, color):
        smoothed = []
        if self.p.repaint:
            for i in range(500):
                sum_val = 0.0
                gk = [self.gaussian_kernel(y - i, self.p.smoothing_factor) for y in range(500)]
                gk_sum = np.sum(gk)
                for y in range(500):
                    sum_val += src[y] * (gk[y] / gk_sum)
                smoothed.append(sum_val)
                if i % 2 == 0 and i != 0:
                    self.plot_line(i-1, smoothed[i-1], i, smoothed[i], color)
                    # Plotting lines is not directly supported in backtrader, so this part is omitted
                    pass
        return smoothed

    def plot_line(self, x1, y1, x2, y2, color):
        # This method should plot a line between (x1, y1) and (x2, y2) with the given color
        # Backtrader does not support direct line plotting, so this is a placeholder
        a = ""
        pass

    def running_nadaraya(self, src, n):
        gk = []
        gk_sum = 0.0
        smoothed = 0.0
        if self.p.repaint:
            for i in range(n + 1):
                gk.append(self.gaussian_kernel(i, self.p.smoothing_factor))
            gk_sum = np.sum(gk)
        if not self.p.repaint:
            for i in range(n + 1):
                smoothed += src[i] * (gk[i] / gk_sum)
        return smoothed


    def __init__(self):
        # Create the theme
        self.theme = create_palette(self.p.pallete_bear, self.p.pallete_bull, self.p.alpha1, self.p.alpha2)

        # Define constants
        bollinger_bands_lvl1 = True
        bollinger_bands_lvl2 = True
        tp = (self.data.high + self.data.low + self.data.close) / 3

        n_first = 20
        n_second = 75
        n_third = 100

        # Calculate Bollinger Bands and gaps
        self.bolu_1, self.bold_1 = self.bollingers(tp, n_first, self.p.short_stdev)
        bol_first_gap = self.bolu_1 - self.bold_1

        self.bolu_2, self.bold_2 = self.bollingers(tp, n_second, self.p.short_stdev)
        bol_second_gap = self.bolu_2 - self.bold_2

        self.bolu_3, self.bold_3 = self.bollingers(tp, n_third, self.p.med_stdev)
        bol_third_gap = self.bolu_3 - self.bold_3

        self.bolu_4, self.bold_4 = self.bollingers(tp, n_third, self.p.long_stdev)

        # Define pivot variables
        self.pivots = []
        self.pivots2 = []

        pivot_rad = self.p.sens

        # Calculate pivot high and low
        self.pivot_high = bt.indicators.Highest(self.data.high, period=pivot_rad)
        self.pivot_low = bt.indicators.Lowest(self.data.low, period=pivot_rad)


        n = 499

        smoothed_bolu_1 = self.running_nadaraya(self.bolu_1.array, n)
        smoothed_bold_1 = self.running_nadaraya(self.bold_1.array, n)

        smoothed_bolu_2 = self.running_nadaraya(self.bolu_2.array, n)
        smoothed_bold_2 = self.running_nadaraya(self.bold_2.array, n)

        smoothed_bolu_3 = self.running_nadaraya(self.bolu_3.array, n)
        smoothed_bold_3 = self.running_nadaraya(self.bold_3.array, n)

        smoothed_bolu_4 = self.running_nadaraya(self.bolu_4.array, n)
        smoothed_bold_4 = self.running_nadaraya(self.bold_4.array, n)

        # Assign smoothed bands to lines
        self.lines.upper_band_1 = smoothed_bolu_1
        self.lines.lower_band_1 = smoothed_bold_1

        self.lines.upper_band_2 = smoothed_bolu_2
        self.lines.lower_band_2 = smoothed_bold_2

        self.lines.upper_band_3 = smoothed_bolu_3
        self.lines.lower_band_3 = smoothed_bold_3

        self.lines.upper_band_4 = smoothed_bolu_4
        self.lines.lower_band_4 = smoothed_bold_4

        if self.p.repaint:
            self.nadaraya(self.bolu_1.array, self.theme.bear)
            self.nadaraya(self.bold_1.array, self.theme.bull)

        spacing = bt.indicators.ATR(self.data, period=300)

        band_test_upper_source = self.data.close if self.p.label_src == "Close" else self.data.high
        band_test_lower_source = self.data.close if self.p.label_src == "Close" else self.data.low

        offset = self.p.sens if self.p.label_src == "Pivots" else 0

        upper_band_test = (band_test_upper_source >= smoothed_bolu_1[offset] and
                           (band_test_upper_source[-1] <= smoothed_bolu_1[offset] or np.isnan(band_test_upper_source[-1])) and
                           not self.p.repaint) * (band_test_upper_source + spacing[0] * 1.01)

        lower_band_test = (band_test_lower_source <= smoothed_bold_1[offset] and
                           (band_test_lower_source[-1] >= smoothed_bold_1[offset] or np.isnan(band_test_upper_source[-1])) and
                           not self.p.repaint) * (band_test_lower_source - spacing[0] * 1.01)

        if self.p.notifs:
            if self.data.close[0] > smoothed_bolu_1[0]:
                self.log("Upper Band Crossed")
            elif self.data.close[0] < smoothed_bold_1[0]:
                self.log("Lower Band Crossed")


        # Plot shapes
        self.plotshape(self.p.labels and upper_band_test, style='triangledown', location='absolute', color=self.theme.bear, offset=-1 * offset, size='tiny')
        self.plotshape(self.p.labels and lower_band_test, style='triangleup', location='absolute', color=self.theme.bull, offset=-1 * offset, size='tiny')

        # Plot smoothed bands
        self.plot(not self.p.repaint and self.p.plots and smoothed_bolu_1, linewidth=self.p.plot_thickness, color=self.theme.bear)
        self.plot(not self.p.repaint and self.p.plots and smoothed_bold_1, linewidth=self.p.plot_thickness, color=self.theme.bull)

        # Fill areas between bands
        self.fill_between(self.lines.upper_band_1, self.lines.upper_band_2, color=self.theme.shade1_bear, alpha=0.5)
        self.fill_between(self.lines.lower_band_1, self.lines.lower_band_2, color=self.theme.shade1_bull, alpha=0.5)
        self.fill_between(self.lines.upper_band_2, self.lines.upper_band_3, color=self.theme.shade2_bear, alpha=0.5)
        self.fill_between(self.lines.lower_band_2, self.lines.lower_band_3, color=self.theme.shade2_bull, alpha=0.5)

