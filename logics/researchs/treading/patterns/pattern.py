import pandas as pd
from logics.researchs.treading.patterns.method import PatternDetector
from typing import Optional, Dict, Union, Callable, Tuple


def get_pattern_list() -> list:
    return list(get_pattern_dict().keys())


def get_pattern_dict() -> Dict[str, Union[str, Callable]]:
    return {
        "all": "all",
        "bull": "bull",
        "bear": "bear",
        "vcpu": find_bullish_vcp,
        "vcpd": find_bearish_vcp,
        "dbot": find_double_bottom,
        "dtop": find_double_top,
        "hnsd": find_hns,
        "hnsu": find_reverse_hns,
        "trng": find_triangles,
    }


def get_pattern_tuple(pattern_name: str) -> Tuple[Callable, ...]:
    # get all support patterns
    fn_dict = get_pattern_dict()
    # get function out
    fn = fn_dict[pattern_name]
    # base on fn style and name return patterns tuples
    if callable(fn):
        return (fn,)
    elif fn == "bull":
        bull_list = ("vcpu", "hnsu", "dbot")
        return tuple(v for k, v in fn_dict.items() if k in bull_list and callable(v))
    elif fn == "bear":
        bear_list = ("vcpd", "hnsd", "dtop")
        return tuple(v for k, v in fn_dict.items() if k in bear_list and callable(v))
    else:
        return tuple(v for k, v in fn_dict.items() if k in fn_dict.keys()[3:] and callable(v))


def find_bullish_vcp(_: PatternDetector, sym: str, df: pd.DataFrame, pivots: pd.DataFrame) -> Optional[dict]:
    """Find Volatility Contraction Pattern Bullish.
    Returns None if no patterns found.
    Else returns a Tuple of dicts containing local arguments and patterns data.
    """
    assert isinstance(pivots.index, pd.DatetimeIndex)
    pivot_len = pivots.shape[0]
    # P = Price V = Volume
    # a 1st high position, also Max high point in treading
    a_idx = pivots["P"].idxmax()
    a = pivots.at[a_idx, "P"]
    # e
    assert isinstance(a_idx, pd.Timestamp)
    e_idx = df.index[-1]
    e = df.at[e_idx, "Close"]

    while True:
        pos_after_a = _.get_next_index(pivots.index, a_idx)
        if pos_after_a >= pivot_len:
            break
        # b 1st low position
        b_idx = pivots.loc[pivots.index[pos_after_a]:, "P"].idxmin()
        b = pivots.at[b_idx, "P"]
        pos_after_b = _.get_next_index(pivots.index, b_idx)
        if pos_after_b >= pivot_len:
            break
        # d 2nd low position
        d_idx = pivots.loc[pivots.index[pos_after_b]:, "P"].idxmin()
        d = pivots.at[d_idx, "P"]
        # c 2nd high position
        c_idx = pivots.loc[b_idx:d_idx, "P"].idxmax()
        c = pivots.at[c_idx, "P"]

        df_slice = df.loc[a_idx:c_idx]
        avg_bar_length = (df_slice["High"] - df_slice["Low"]).mean()

        if pivots.index.has_duplicates:
            if isinstance(a, (pd.Series, str)):
                a = pivots.at[a_idx, "P"].iloc[0]
            if isinstance(b, (pd.Series, str)):
                b = pivots.at[b_idx, "P"].iloc[1]
            if isinstance(c, (pd.Series, str)):
                c = pivots.at[c_idx, "P"].iloc[0]
            if isinstance(d, (pd.Series, str)):
                d = pivots.at[d_idx, "P"].iloc[1]

        if _.is_bullish_vcp(a, b, c, d, e, avg_bar_length):
            # check if Level C has been breached after it was formed
            if (
                    c_idx != df.loc[c_idx:, "Close"].idxmax()
                    or d_idx != df.loc[d_idx:, "Close"].idxmin()
            ):
                # Level C is breached, current patterns is not valid
                # check if C is the last pivot formed
                if pivots.index[-1] == c_idx or pivots.index[-1] == d_idx:
                    break
                # continue search for patterns
                a_idx, a = c_idx, c
                continue

            entry_line = ((c_idx, c), (e_idx, c))
            ab = ((a_idx, a), (b_idx, b))
            bc = ((b_idx, b), (c_idx, c))
            cd = ((c_idx, c), (d_idx, d))
            de = ((d_idx, d), (e_idx, e))

            _.logger.debug(f"{sym} - VCPU")
            return dict(
                sym=sym,
                pattern="VCPU",
                start=a_idx,
                end=e_idx,
                df_start=df.index[0],
                df_end=df.index[-1],
                lines=(entry_line, ab, bc, cd, de),
            )

        a_idx, a = c_idx, c


def find_double_bottom(_: PatternDetector, sym: str, df: pd.DataFrame, pivots: pd.DataFrame) -> Optional[dict]:
    """Find Double bottom.
    Returns None if no patterns found.
    Else returns a Tuple of dicts containing local arguments and patterns data.
    """
    assert isinstance(pivots.index, pd.DatetimeIndex)
    pivot_len = pivots.shape[0]
    # a
    a_idx = pivots["P"].idxmin()
    a, a_vol = pivots.loc[a_idx, ["P", "V"]]
    # d
    d_idx = df.index[-1]
    d = df.at[d_idx, "Close"]

    atr_ser = _.get_atr(df.High, df.Low, df.Close)
    assert isinstance(a_idx, pd.Timestamp)

    while True:
        pos_after_a = _.get_next_index(pivots.index, a_idx)
        if pos_after_a >= pivot_len:
            break
        # c
        c_idx = pivots.loc[pivots.index[pos_after_a]:, "P"].idxmin()
        c, c_vol = pivots.loc[c_idx, ["P", "V"]]
        # b
        b_idx = pivots.loc[a_idx:c_idx, "P"].idxmax()
        b = pivots.at[b_idx, "P"]

        atr = atr_ser.at[c_idx]
        if pivots.index.has_duplicates:
            if isinstance(a, (pd.Series, str)):
                a = pivots.at[a_idx, "P"].iloc[1]
            if isinstance(a_vol, (pd.Series, str)):
                a_vol = pivots.at[a_idx, "V"].iloc[1]
            if isinstance(b, (pd.Series, str)):
                b = pivots.at[b_idx, "P"].iloc[0]
            if isinstance(c, (pd.Series, str)):
                c = pivots.at[c_idx, "P"].iloc[1]
            if isinstance(c_vol, (pd.Series, str)):
                c_vol = pivots.at[c_idx, "V"].iloc[1]

        df_slice = df.loc[a_idx:c_idx]
        avg_bar_length = (df_slice["High"] - df_slice["Low"]).mean()

        if _.is_double_bottom(a, b, c, d, a_vol, c_vol, avg_bar_length, atr):
            if a == df.at[a_idx, "High"] or b == df.at[b_idx, "Low"] or c == df.at[c_idx, "High"]:
                # check that the patterns is well-formed
                a_idx, a, a_vol = c_idx, c, c_vol
                continue

            # check if Level C has been breached after it was formed
            if c_idx != df.loc[c_idx:, "Close"].idxmin() or b_idx != df.loc[b_idx:, "Close"].idxmax():
                a_idx, a, a_vol = c_idx, c, c_vol
                continue

            if df.loc[c_idx:, "Close"].max() > b:
                a_idx, a, a_vol = c_idx, c, c_vol
                continue

            entry_line = ((b_idx, b), (d_idx, b))
            ab = ((a_idx, a), (b_idx, b))
            bc = ((b_idx, b), (c_idx, c))
            cd = ((c_idx, c), (d_idx, d))

            _.logger.debug(f"{sym} - DBOT")

            return dict(
                sym=sym,
                pattern="DBOT",
                start=a_idx,
                end=d_idx,
                df_start=df.index[0],
                df_end=df.index[-1],
                lines=(entry_line, ab, bc, cd),
            )

        a_idx, a, a_vol = c_idx, c, c_vol


def find_reverse_hns(_: PatternDetector, sym: str, df: pd.DataFrame, pivots: pd.DataFrame) -> Optional[dict]:
    """Find Head and Shoulders - Bullish
    Returns None if no patterns found.
    Else returns an Tuple of dicts containing local arguments and patterns data.
    """
    assert isinstance(pivots.index, pd.DatetimeIndex)

    pivot_len = pivots.shape[0]
    f_idx = df.index[-1]
    f = df.at[f_idx, "Close"]

    c_idx = pivots["P"].idxmin()
    c = pivots.at[c_idx, "P"]
    assert isinstance(c_idx, pd.Timestamp)

    while True:
        pos = _.get_prev_index(pivots.index, c_idx)
        if pos >= pivot_len:
            break
        idx_before_c = pivots.index[pos]

        a_idx = pivots.loc[:idx_before_c, "P"].idxmin()
        a = pivots.at[a_idx, "P"]
        b_idx = pivots.loc[a_idx:c_idx, "P"].idxmax()
        b = pivots.at[b_idx, "P"]

        pos = _.get_next_index(pivots.index, c_idx)
        if pos >= pivot_len:
            break

        idx_after_c = pivots.index[pos]
        e_idx = pivots.loc[idx_after_c:, "P"].idxmin()
        e = pivots.at[e_idx, "P"]
        d_idx = pivots.loc[c_idx:e_idx, "P"].idxmax()
        d = pivots.at[d_idx, "P"]

        if pivots.index.has_duplicates:
            if isinstance(a, (pd.Series, str)):
                a = pivots.loc[a_idx, "P"].iloc[1]
            if isinstance(b, (pd.Series, str)):
                b = pivots.loc[b_idx, "P"].iloc[0]
            if isinstance(c, (pd.Series, str)):
                c = pivots.loc[c_idx, "P"].iloc[1]
            if isinstance(d, (pd.Series, str)):
                d = pivots.loc[d_idx, "P"].iloc[0]
            if isinstance(e, (pd.Series, str)):
                e = pivots.loc[e_idx, "P"].iloc[1]

        df_slice = df.loc[b_idx:d_idx]
        avgBarLength = (df_slice["High"] - df_slice["Low"]).mean()

        if _.is_reverse_hns(a, b, c, d, e, f, avgBarLength):
            if (
                    a == df.at[a_idx, "High"]
                    or b == df.at[b_idx, "Low"]
                    or c == df.at[c_idx, "High"]
                    or d == df.at[d_idx, "Low"]
                    or e == df.at[e_idx, "High"]
            ):
                # Make sure patterns is well formed
                c_idx, c = e_idx, e
                continue

            neckline_price = min(b, d)
            highest_after_e = df.loc[e_idx:, "High"].max()
            if (
                    highest_after_e > neckline_price
                    and abs(highest_after_e - neckline_price) > avgBarLength
            ):
                # check if neckline was breached after patterns formation
                c_idx, c = e_idx, e
                continue

            # bd is the trendline coordinates from B to D (neckline)
            tline = _.generate_trend_line(df.High, b_idx, d_idx)

            # Get the y coordinate of the trendline at the end of the chart
            # With the given slope(m) and y-intercept(b) as y_int,
            # Get the x coordinate (index position of last date in DataFrame)
            # and calculate value of y coordinate using y = mx + b
            x = df.index.get_loc(df.index[-1])

            assert isinstance(x, int)
            y = tline.slope * x + tline.y_int
            # if close price is greater than neckline (trendline), skip
            if f > y:
                c_idx, c = e_idx, e
                continue

            # lines
            ab = ((a_idx, a), (b_idx, b))
            bc = ((b_idx, b), (c_idx, c))
            cd = ((c_idx, c), (d_idx, d))
            de = ((d_idx, d), (e_idx, e))
            ef = ((e_idx, e), (f_idx, f))

            if tline.slope > 0:
                entry_line = ((b_idx, b), (f_idx, b))

                lines = (entry_line, tline.line, ab, bc, cd, de, ef)
            else:
                lines = (tline.line, ab, bc, cd, de, ef)
            _.logger.debug(f"{sym} - HNSU")

            return dict(
                sym=sym,
                pattern="HNSU",
                start=a_idx,
                end=f_idx,
                df_start=df.index[0],
                df_end=df.index[-1],
                slope=tline.line,
                y_intercept=tline.y_int,
                lines=lines,
            )
        c_idx, c = e_idx, e


def find_bearish_vcp(_: PatternDetector, sym: str, df: pd.DataFrame, pivots: pd.DataFrame) -> Optional[dict]:
    """Find Volatility Contraction Pattern Bearish.
    Returns None if no patterns found.
    Else returns a Tuple of dicts containing local arguments and patterns data.
    """

    assert isinstance(pivots.index, pd.DatetimeIndex)

    pivot_len = pivots.shape[0]
    a_idx = pivots["P"].idxmin()
    a = pivots.at[a_idx, "P"]

    assert isinstance(a_idx, pd.Timestamp)

    e_idx = df.index[-1]
    e = df.at[e_idx, "Close"]

    while True:
        pos_after_a = _.get_next_index(pivots.index, a_idx)

        if pos_after_a >= pivot_len:
            break

        b_idx = pivots.loc[pivots.index[pos_after_a]:, "P"].idxmax()
        b = pivots.at[b_idx, "P"]
        pos_after_b = _.get_next_index(pivots.index, b_idx)
        if pos_after_b >= pivot_len:
            break

        d_idx = pivots.loc[pivots.index[pos_after_b]:, "P"].idxmax()
        d = pivots.at[d_idx, "P"]
        c_idx = pivots.loc[b_idx:d_idx, "P"].idxmin()
        c = pivots.at[c_idx, "P"]
        df_slice = df.loc[a_idx:c_idx]
        avgBarLength = (df_slice["High"] - df_slice["Low"]).mean()

        if pivots.index.has_duplicates:
            if isinstance(a, (pd.Series, str)):
                a = pivots.at[a_idx, "P"].iloc[1]
            if isinstance(b, (pd.Series, str)):
                b = pivots.at[b_idx, "P"].iloc[0]
            if isinstance(c, (pd.Series, str)):
                c = pivots.at[c_idx, "P"].iloc[1]
            if isinstance(d, (pd.Series, str)):
                d = pivots.at[d_idx, "P"].iloc[0]

        if _.is_bearish_vcp(a, b, c, d, e, avgBarLength):
            if (
                    d_idx != df.loc[d_idx:, "Close"].idxmax()
                    or c_idx != df.loc[c_idx:, "Close"].idxmin()
            ):
                # check that the patterns is well formed
                if pivots.index[-1] == d_idx or pivots.index[-1] == c_idx:
                    break
                a_idx, a = c_idx, c
                continue

            entry_line = ((c_idx, c), (e_idx, c))
            ab = ((a_idx, a), (b_idx, b))
            bc = ((b_idx, b), (c_idx, c))
            cd = ((c_idx, c), (d_idx, d))
            de = ((d_idx, d), (e_idx, e))

            _.logger.debug(f"{sym} - VCPD")

            return dict(
                sym=sym,
                pattern="VCPD",
                start=a_idx,
                end=e_idx,
                df_start=df.index[0],
                df_end=df.index[-1],
                lines=(entry_line, ab, bc, cd, de),
            )

        # We assign pivot level C to be the new
        # This may not be the lowest pivot, so additional checks are required.
        a_idx, a = c_idx, c


def find_double_top(_: PatternDetector, sym: str, df: pd.DataFrame, pivots: pd.DataFrame) -> Optional[dict]:
    """Find Double Top.
    Returns None if no patterns found.
    Else returns a Tuple of dicts containing local arguments and patterns data.
    """
    assert isinstance(pivots.index, pd.DatetimeIndex)

    pivot_len = pivots.shape[0]
    # a
    a_idx = pivots["P"].idxmax()
    a, a_vol = pivots.loc[a_idx, ["P", "V"]]
    # d
    d_idx = df.index[-1]
    d = df.at[d_idx, "Close"]

    atr_ser = _.get_atr(df.High, df.Low, df.Close)
    assert isinstance(a_idx, pd.Timestamp)

    while True:
        idx = _.get_next_index(pivots.index, a_idx)
        if idx >= pivot_len:
            break
        # c
        c_idx = pivots.loc[pivots.index[idx]:, "P"].idxmax()
        c, c_vol = pivots.loc[c_idx, ["P", "V"]]
        # b
        b_idx = pivots.loc[a_idx:c_idx, "P"].idxmin()
        b = pivots.at[b_idx, "P"]

        atr = atr_ser.at[c_idx]

        if pivots.index.has_duplicates:
            if isinstance(a, (pd.Series, str)):
                a = pivots.at[a_idx, "P"].iloc[0]
            if isinstance(a_vol, (pd.Series, str)):
                a_vol = pivots.at[a_idx, "V"].iloc[0]
            if isinstance(b, (pd.Series, str)):
                b = pivots.at[b_idx, "P"].iloc[1]
            if isinstance(c, (pd.Series, str)):
                c = pivots.at[c_idx, "P"].iloc[0]
            if isinstance(c_vol, (pd.Series, str)):
                c_vol = pivots.at[c_idx, "V"].iloc[0]

        df_slice = df.loc[a_idx:c_idx]
        avg_bar_length = (df_slice["High"] - df_slice["Low"]).mean()
        if _.is_double_top(a, b, c, d, a_vol, c_vol, avg_bar_length, atr):
            if (
                    a == df.at[a_idx, "Low"]
                    or b == df.at[b_idx, "High"]
                    or c == df.at[c_idx, "Low"]
            ):
                a_idx, a, a_vol = c_idx, c, c_vol
                continue

            # check if Level C has been breached after it was formed
            if (
                    c_idx != df.loc[c_idx:, "Close"].idxmax()
                    or b_idx != df.loc[b_idx:, "Close"].idxmin()
            ):
                # Level C is breached, current patterns is not valid
                a_idx, a, a_vol = c_idx, c, c_vol
                continue

            entry_line = ((b_idx, b), (d_idx, b))
            ab = ((a_idx, a), (b_idx, b))
            bc = ((b_idx, b), (c_idx, c))
            cd = ((c_idx, c), (d_idx, d))

            _.logger.debug(f"{sym} - DTOP")
            return dict(
                sym=sym,
                pattern="DTOP",
                start=a_idx,
                end=d_idx,
                df_start=df.index[0],
                df_end=df.index[-1],
                lines=(entry_line, ab, bc, cd),
            )
        a_idx, a, a_vol = c_idx, c, c_vol


def find_hns(_: PatternDetector, sym: str, df: pd.DataFrame, pivots: pd.DataFrame) -> Optional[dict]:
    """Find Head and Shoulders - Bearish
    Returns None if no patterns found.
    Else returns a Tuple of dicts containing local arguments and patterns data.
    """
    assert isinstance(pivots.index, pd.DatetimeIndex)
    pivot_len = pivots.shape[0]
    # f
    f_idx = df.index[-1]
    f = df.at[f_idx, "Close"]
    # c
    c_idx = pivots["P"].idxmax()
    c = pivots.at[c_idx, "P"]
    assert isinstance(c_idx, pd.Timestamp)

    while True:
        pos = _.get_prev_index(pivots.index, c_idx)
        if pos >= pivot_len:
            break
        idx_before_c = pivots.index[pos]
        # a
        a_idx = pivots.loc[:idx_before_c, "P"].idxmax()
        a = pivots.at[a_idx, "P"]
        # b
        b_idx = pivots.loc[a_idx:c_idx, "P"].idxmin()
        b = pivots.at[b_idx, "P"]
        # c
        pos = _.get_next_index(pivots.index, c_idx)
        if pos >= pivot_len:
            break
        idx_after_c = pivots.index[pos]
        # e
        e_idx = pivots.loc[idx_after_c:, "P"].idxmax()
        e = pivots.at[e_idx, "P"]
        # d
        d_idx = pivots.loc[c_idx:e_idx, "P"].idxmin()
        d = pivots.at[d_idx, "P"]

        if pivots.index.has_duplicates:
            if isinstance(a, (pd.Series, str)):
                a = pivots.at[a_idx, "P"].iloc[0]
            if isinstance(b, (pd.Series, str)):
                b = pivots.at[b_idx, "P"].iloc[1]
            if isinstance(c, (pd.Series, str)):
                c = pivots.at[c_idx, "P"].iloc[0]
            if isinstance(d, (pd.Series, str)):
                d = pivots.at[d_idx, "P"].iloc[1]
            if isinstance(e, (pd.Series, str)):
                e = pivots.at[e_idx, "P"].iloc[0]

        df_slice = df.loc[b_idx:d_idx]
        avg_bar_length = (df_slice["High"] - df_slice["Low"]).mean()

        if _.is_hns(a, b, c, d, e, f, avg_bar_length):
            if (
                    a == df.at[a_idx, "Low"]
                    or b == df.at[b_idx, "High"]
                    or c == df.at[c_idx, "Low"]
                    or d == df.at[d_idx, "High"]
                    or e == df.at[e_idx, "Low"]
            ):
                # Make sure the patterns is well-formed and
                # pivots are correctly anchored to highs and lows
                c_idx, c = e_idx, e
                continue

            neckline_price = min(b, d)
            lowest_after_e = df.loc[e_idx:, "Low"].min()

            if (
                    lowest_after_e < neckline_price
                    and abs(lowest_after_e - neckline_price) > avg_bar_length
            ):
                # check if the neckline was breached after patterns formation
                c_idx, c = e_idx, e
                continue

            # bd is the line coordinate for points B and D
            tline = _.generate_trend_line(df.Low, b_idx, d_idx)

            # Get the y coordinate of the trend-line at the end of the chart
            # With the given slope(m) and y-intercept(b) as y_int,
            # Get the x coordinate (index position of last date in DataFrame)
            # and calculate value of y coordinate using y = mx + b
            x = df.index.get_loc(f_idx)

            assert isinstance(x, int)
            y = tline.slope * x + tline.y_int
            # if the close price is below the neckline (trend-line), skip
            if f < y:
                c_idx, c = e_idx, e
                continue

            # lines
            ab = ((a_idx, a), (b_idx, b))
            bc = ((b_idx, b), (c_idx, c))
            cd = ((c_idx, c), (d_idx, d))
            de = ((d_idx, d), (e_idx, e))
            ef = ((e_idx, e), (f_idx, f))

            if tline.slope < 0:
                entry_line = ((b_idx, b), (f_idx, b))
                lines = (entry_line, tline.line, ab, bc, cd, de, ef)
            else:
                lines = (tline.line, ab, bc, cd, de, ef)

            _.logger.debug(f"{sym} - HNSD")

            return dict(
                sym=sym,
                pattern="HNSD",
                start=a_idx,
                end=f_idx,
                df_start=df.index[0],
                df_end=df.index[-1],
                slope=tline.slope,
                y_intercept=tline.y_int,
                lines=lines,
            )

        c_idx, c = e_idx, e


def find_triangles(_: PatternDetector, sym: str, df: pd.DataFrame, pivots: pd.DataFrame) -> Optional[dict]:
    """Find Triangles - Symmetric, Ascending, Descending.
    Returns None if no patterns found.
    Else returns a Tuple of dicts containing local arguments and patterns data.
    """
    assert isinstance(pivots.index, pd.DatetimeIndex)

    pivot_len = pivots.shape[0]
    a_idx = pivots["P"].idxmax()
    a = pivots.loc[a_idx, "P"]

    f_idx = df.index[-1]
    f = df.at[f_idx, "Close"]

    while True:
        b_idx = pivots.loc[a_idx:, "P"].idxmin()
        b = pivots.at[b_idx, "P"]

        assert isinstance(a_idx, pd.Timestamp)

        pos_after_a = _.get_next_index(pivots.index, a_idx)
        if pos_after_a >= pivot_len:
            break

        # A is already the lowest point
        if a_idx == b_idx:
            a_idx = pivots.index[pos_after_a]
            a = pivots.at[a_idx, "P"]
            continue

        pos_after_b = _.get_next_index(pivots.index, b_idx)
        if pos_after_b >= pivot_len:
            break

        d_idx = pivots.loc[pivots.index[pos_after_b]:, "P"].idxmin()
        d = pivots.at[d_idx, "P"]
        c_idx = pivots.loc[pivots.index[pos_after_a]:, "P"].idxmax()
        c = pivots.at[c_idx, "P"]
        pos_after_c = _.get_next_index(pivots.index, c_idx)
        if pos_after_c >= pivot_len:
            break

        e_idx = pivots.loc[pivots.index[pos_after_c]:, "P"].idxmax()
        e = pivots.at[e_idx, "P"]
        if pivots.index.has_duplicates:
            if isinstance(a, (pd.Series, str)):
                a = pivots.at[a_idx, "P"].iloc[0]
            if isinstance(b, (pd.Series, str)):
                b = pivots.at[b_idx, "P"].iloc[1]
            if isinstance(c, (pd.Series, str)):
                c = pivots.at[c_idx, "P"].iloc[0]
            if isinstance(d, (pd.Series, str)):
                d = pivots.at[d_idx, "P"].iloc[1]
            if isinstance(e, (pd.Series, str)):
                e = pivots.at[e_idx, "P"].iloc[0]

        df_slice = df.loc[a_idx:d_idx]
        avg_bar_length = (df_slice["High"] - df_slice["Low"]).mean()
        triangle = _.is_triangle(a, b, c, d, e, f, avg_bar_length)
        if triangle is not None:
            # check if high of C or low of D has been breached
            # Check if A is indeed the pivot high
            if (
                    a == df.at[a_idx, "Low"]
                    or c_idx != df.loc[c_idx:, "Close"].idxmax()
                    or d_idx != df.loc[d_idx:, "Close"].idxmin()
            ):
                a_idx, a = c_idx, c
                continue

            upper = _.generate_trend_line(df.High, a_idx, c_idx)
            lower = _.generate_trend_line(df.Low, b_idx, d_idx)
            # If trendlines have intersected, patterns has played out
            if upper.line.end.y < lower.line.end.y:
                break

            if triangle == "Ascending" and (
                    upper.slope > 0.1 and lower.slope < 0.2
            ):
                break
            if triangle == "Descending" and (
                    lower.slope < -0.1 and upper.slope > -0.2
            ):
                break
            if triangle == "Symmetric" and (
                    upper.slope > -0.2 and lower.slope < 0.2
            ):
                break

            _.logger.debug(f"{sym} - {triangle}")
            return dict(
                sym=sym,
                pattern=triangle,
                start=a_idx,
                end=f_idx,
                df_start=df.index[0],
                df_end=df.index[-1],
                slope_upper=upper.slope,
                slope_lower=lower.slope,
                lines=(upper.line, lower.line),
            )
        a_idx, c = c_idx, c
