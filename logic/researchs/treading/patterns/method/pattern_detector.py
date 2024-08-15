import numpy as np
import pandas as pd
from logging import Logger
from typing import NamedTuple, Optional, TypeVar, Any

T = TypeVar("T")


class Point(NamedTuple):
    x: pd.Timestamp
    y: float


class Coordinate(NamedTuple):
    start: Point
    end: Point


class Line(NamedTuple):
    line: Coordinate
    slope: float
    y_int: float


class PatternDetector:

    def __init__(self, logger: Logger):
        self.logger = logger

    def get_prev_index(self, index: pd.DatetimeIndex, idx: pd.Timestamp) -> int:
        pos = index.get_loc(idx)

        if isinstance(pos, slice):
            return pos.stop

        if isinstance(pos, int):
            return pos - 1

        raise TypeError("Expected Integer")

    def get_next_index(self, index: pd.DatetimeIndex, idx: pd.Timestamp) -> int:
        pos = index.get_loc(idx)
        if isinstance(pos, slice):
            return pos.stop
        if isinstance(pos, int):
            return pos + 1
        raise TypeError("Expected Integer")

    def get_max_min(self, df: pd.DataFrame, bars_left=6, bars_right=6) -> pd.DataFrame:
        window = bars_left + 1 + bars_right
        l_max_dt = []
        l_min_dt = []
        cols = ["P", "V"]

        for win in df.rolling(window):
            if win.shape[0] < window:
                continue
            idx = win.index[bars_left + 1]  # center candle
            if win["High"].idxmax() == idx:
                l_max_dt.append(idx)
            if win["Low"].idxmin() == idx:
                l_min_dt.append(idx)

        maxima = pd.DataFrame(df.loc[l_max_dt, ["High", "Volume"]])
        maxima.columns = cols
        minima = pd.DataFrame(df.loc[l_min_dt, ["Low", "Volume"]])
        minima.columns = cols
        return pd.concat([maxima, minima]).sort_index()

    def get_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, window=15) -> pd.Series:
        # Calculate true range
        tr = pd.DataFrame(index=high.index)
        tr["h-l"] = high - low
        tr["h-pc"] = abs(high - close.shift(1))
        tr["l-pc"] = abs(low - close.shift(1))
        tr["tr"] = tr[["h-l", "h-pc", "l-pc"]].max(axis=1)
        return tr.tr.rolling(window=window).mean()

    def is_bullish_vcp(self, a: float, b: float, c: float, d: float, e: float, avg_bar_length: float) -> bool:
        r"""Volatility Contraction patterns
           A        C
            \      /\    E
             \    /  \  /
              \  /    \/
               \/      D
                B
        B is the lowest point in patterns
        D is second lowest after B
        """
        if c > a and abs(a - c) >= avg_bar_length * 0.5:
            return False
        return (
                abs(a - c) <= avg_bar_length
                and abs(b - d) >= avg_bar_length * 0.8
                and b < min(a, c, d, e)
                and d < min(a, c, e)
                and e < c
        )

    def is_double_top(
            self, a: float, b: float, c: float, d: float,
            a_vol: int, c_vol: int, avg_bar_length: float, atr: float) -> bool:
        r"""
        Double Top
              A     C
             /\    /\
            /  \  /  \
           /    \/    D
          /      B
         /
        /
        """
        return (
                c - b < atr * 4
                and abs(a - c) <= avg_bar_length * 0.5
                and c_vol < a_vol
                and b < min(a, c)
                and b < d < c
        )

    def is_triangle(
            self, a: float, b: float, c: float, d: float, e: float, f: float,
            avg_bar_length: float) -> Optional[str]:
        r"""
             A
             /\        C
            /  \      /\    E
           /    \    /  \  /\
          /      \  /    \/  F
         /        \/      D
        /         B            Symmetric
           A
           /\      C
          /  \    /\    E
         /    \  /  \  /\
        /      \/    \/  F
               B     D         Descending
             A       C     E
            /\      /\    /\
           /  \    /  \  /  \
          /    \  /    \/    F
         /      \/     D
        /        B             Ascending
        """
        is_ac_straight_line = abs(a - c) <= avg_bar_length
        is_ce_straight_line = abs(c - e) <= avg_bar_length

        if is_ac_straight_line and is_ce_straight_line and b < d < f < e:
            return "Ascending"

        is_bd_straight_line = abs(b - d) <= avg_bar_length

        if is_bd_straight_line and a > c > e > f and f >= d:
            return "Descending"

        if a > c > e and b < d < f and e > f:
            return "Symmetric"

        return None

    def is_double_bottom(
            self, a: float, b: float, c: float, d: float,
            a_vol: int, c_vol: int, avg_bar_length: float, atr: float) -> bool:
        r"""
        Double Bottom
          \
           \
            \      B
             \    /\    D
              \  /  \  /
               \/    \/
                A     C
        """

        return (
                b - c < atr * 4
                and abs(a - c) <= avg_bar_length * 0.5
                and c_vol < a_vol
                and b > max(a, c)
                and b > d > c
        )

    def is_hns(self, a: float, b: float, c: float, d: float, e: float, f: float, avg_bar_length: float) -> bool:
        r"""
        Head and Shoulders
                    C
                    /\
            A      /  \      E
            /\    /    \    /\
           /  \  /      \  /  \
          /    \/________\/____\F__Neckline
         /      B         D     \
        /                        \
        """
        shoulder_height_threshold = round(avg_bar_length * 0.6, 2)

        return (
                c > max(a, e)
                and max(b, d) < min(a, e)
                and f < e
                and abs(b - d) < avg_bar_length
                and abs(c - e) > shoulder_height_threshold
        )

    def is_reverse_hns(self, a: float, b: float, c: float, d: float, e: float, f: float, avg_bar_length: float) -> bool:
        r"""
        Reverse Head and Shoulders
        \
         \                  /
          \   _B_______D___/___
           \  /\      /\  /F   Neckline
            \/  \    /  \/
            A    \  /    E
                  \/
                  C
        """
        shoulder_height_threshold = round(avg_bar_length * 0.6, 2)

        return (
                c < min(a, e)
                and min(b, d) > max(a, e)
                and f > e
                and abs(b - d) < avg_bar_length
                and abs(c - e) > shoulder_height_threshold
        )

    def is_bearish_vcp(self, a: float, b: float, c: float, d: float, e: float, avg_bar_length: float) -> bool:
        r"""
        Volatility Contraction patterns
              B
             /\      D
            /  \    /\
           /    \  /  \
          /      \/    E
         A       C
        B is the highest point in patterns
        D is second highest after B
        """
        if c < a and abs(a - c) >= avg_bar_length * 0.5:
            return False

        return (
                abs(a - c) <= avg_bar_length
                and abs(b - d) >= avg_bar_length * 0.8
                and b > max(a, c, d, e)
                and d > max(a, c, e)
                and e > c
        )


    def generate_trend_line(self, series: pd.Series, date1: pd.Timestamp, date2: pd.Timestamp) -> Line:
        """Return the end coordinates for a trend-line along with slope and y-intercept
        Input: Pandas series with a pandas.DatetimeIndex, and two dates:
               The two dates are used to determine two "prices" from the series

        Output: tuple(tuple(coord, coord), slope, y-intercept)
        source: https://github.com/matplotlib/mplfinance/blob/master/examples/scratch_pad/trend_line_extrapolation.ipynb

        """
        index = series.index

        p1 = float(series[date1])
        p2 = float(series[date2])

        d1 = index.get_loc(date1)
        d2 = index.get_loc(date2)

        last_idx = index[-1]
        last_idx_pos = index.get_loc(last_idx)

        assert isinstance(last_idx, pd.Timestamp)
        assert isinstance(d1, int)
        assert isinstance(d2, int)
        assert isinstance(last_idx_pos, int)
        assert isinstance(p1, float)
        assert isinstance(p2, float)

        # b = y - mx
        # where m is slope,
        # b is y-intercept
        # slope m = change in y / change in x
        m = (p2 - p1) / (d2 - d1)

        y_intercept = p1 - m * d1  # b = y - mx

        return Line(
            line=Coordinate(
                start=Point(x=date1, y=m * d1 + y_intercept),  # y = mx + b
                end=Point(x=last_idx, y=m * last_idx_pos + y_intercept),
            ),
            slope=m,
            y_int=y_intercept,
        )

    def make_serializable(self, obj: T) -> T:
        """Convert pandas.Timestamp and numpy.Float32 objects in obj
        to serializable native types"""
        def serialize(obj: Any) -> Any:
            if isinstance(obj, (pd.Timestamp, np.generic)):
                # Convert Pandas' Timestamp to Python datetime or NumPy item
                return obj.isoformat() if isinstance(obj, pd.Timestamp) else obj.item()
            elif isinstance(obj, (list, tuple)):
                # Recursively convert lists and tuples
                return tuple(serialize(item) for item in obj)
            elif isinstance(obj, dict):
                # Recursively convert dictionaries
                return {key: serialize(value) for key, value in obj.items()}
            return obj
        return serialize(obj)
