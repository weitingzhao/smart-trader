from typing import List, Tuple
import pandas as pd
from core.configures_home import Config


class Utils:

    #<editor-fold desc="get support & resistance levels">
    @staticmethod
    def get_support_resistance_levels(
            df: pd.DataFrame,
            mean_candle_size: float
    ) -> List[Tuple[Tuple[pd.DatetimeIndex, float], Tuple[pd.DatetimeIndex, float]]]:
        """
        Identify potential support and resistance levels in a DataFrame.
        Parameters:
        - df (pd.DataFrame): DataFrame containing at least 'High' and 'Low' columns.
        - mean_candle_size (float): The mean size of a candle, used as a threshold for level clustering.
        Returns:
        - list of tuples: Each tuple represents a horizontal line segment, defined by two points.
          Each point is a tuple containing date and price.
          The list represents identified support and resistance levels.
        Algorithm:
        - The function uses local maxima and minima in the 'High' and 'Low' prices to identify potential reversal points.
        - It filters for rejection from the top (local maxima) and from the bottom (local minima).
        - To avoid clustering of support and resistance lines, it utilizes the isFarFromLevel function.
        - Identified levels are returned as horizontal line segments for visualization.
        Example Usage:
        ```python
        # Example DataFrame df with 'High' and 'Low' columns
        levels = getLevels(df, mean_candle_size=2.0)
        ```
        Note:
        - It is recommended to provide a DataFrame with sufficient historical price data for accurate level identification.
        - The function is designed for use in financial technical analyses.
        """
        levels = []
        # Calculate support and resistance levels
        Utils._calculate_level("High", df, mean_candle_size, levels)
        Utils._calculate_level("Low", df, mean_candle_size, levels)
        # Create horizontal line segments for visualization
        a_lines = []
        last_datetime = df.index[-1]
        for dt, price in levels:
            # a tuple containing start and end point coordinates for a horizontal line
            # Each tuple is composed of date and price.
            seq = ((dt, price), (last_datetime, price))
            a_lines.append(seq)
        return a_lines

    @staticmethod
    def _calculate_level(
            name: str,
            df: pd.DataFrame,
            mean_candle_size: float,
            levels: List):
        # filter for rejection from top
        # 2 successive highs followed by 2 successive lower highs
        local = df[name][
            (df[name].shift(1) < df[name]) & (df[name].shift(2) < df[name].shift(1)) &
            (df[name].shift(-1) < df[name]) & (df[name].shift(-2) < df[name].shift(-1))
            ].dropna()

        for idx in local.index:
            level = local[idx]
            # Prevent clustering of support and resistance lines
            # Only add a level if it at a distance from any other price lines
            if Utils._is_far_from_level(level, levels, mean_candle_size):
                levels.append((idx, level))

    @staticmethod
    def _is_far_from_level(
            level: float,
            levels: List[Tuple[pd.DatetimeIndex, float]],
            mean_candle_size: float,
    ) -> bool:
        """Returns true if difference between the level and any of the price levels
        is greater than the mean_candle_size."""
        # Detection of price support and resistance levels in Python -Gianluca Malato
        # source: https://towardsdatascience.com/detection-of-price-support-and-resistance-levels-in-python-baedc44c34c9
        return sum([abs(level - x[1]) < mean_candle_size for x in levels]) == 0

    #</editor-fold>

    #<editor-fold desc="get delivery levels">
    @staticmethod
    def get_delivery_levels(
            df: pd.DataFrame,
            config: Config):
        # Average of traded quantity
        ave_traded_quantity = Utils.simple_moving_average(df['QTY_PER_TRADE'], config.DLV_AVG_LEN)
        # Average of delivery quantity
        avg_delivery_quantity = Utils.simple_moving_average(df['DLV_QTY'], config.DLV_AVG_LEN)

        # above average delivery days
        df["DQ"] = df["DLV_QTY"] / avg_delivery_quantity
        # above average Traded volume days
        df["TQ"] = df["QTY_PER_TRADE"] / ave_traded_quantity

        # get a combination of above average traded volume and delivery days
        df["IM_F"] = (df["TQ"] > 1.2) & (df["DQ"] > 1.2)

        # see https://github.com/matplotlib/mplfinance/blob/master/examples/marketcolor_overrides.ipynb
        df["MCOverrides"] = None
        df["IM"] = float("nan")

        for idx in df.index:
            dq, im = df.loc[idx, ["DQ", "IM_F"]]

            if im:
                df.loc[idx, "IM"] = df.loc[idx, "Low"] * 0.99

            if dq >= config.DLV_L3:
                df.loc[idx, "MCOverrides"] = config.PLOT_DLV_L1_COLOR
            elif dq >= config.DLV_L2:
                df.loc[idx, "MCOverrides"] = config.PLOT_DLV_L2_COLOR
            elif dq >= config.DLV_L1:
                df.loc[idx, "MCOverrides"] = config.PLOT_DLV_L3_COLOR
            else:
                df.loc[idx, "MCOverrides"] = config.PLOT_DLV_DEFAULT_COLOR

    #</editor-fold>

    @staticmethod
    def arg_parse_dict(dct: dict) -> list:
        """
        Convert a dictionary of arguments and values into a list of command-line arguments.
        Parameters:
        - dct (dict): Dictionary containing argument names and values.
        Returns:
        - list: List of command-line style arguments.
        Example:
        ```python
        args = {'input_file': 'data.txt', 'output_dir': '/output', 'verbose': True}
        command_line_args = arg_parse_dict(args)
        ```
        """
        result = []
        for arg, val in dct.items():
            if val is False or val is None:
                continue
            arg = arg.replace("_", "-")
            result.append(f"--{arg}")
            if val is not True:
                if isinstance(val, list):
                    result.extend(map(str, val))
                else:
                    result.append(str(val))
        return result

    @staticmethod
    def relative_strength(
            close: pd.Series,
            index_close: pd.Series
    ) -> pd.Series:
        return (close / index_close * 100).round(2)

    @staticmethod
    def mansfield_relative_strength(
            close: pd.Series,
            index_close: pd.Series,
            period: int = 40
    ) -> pd.Series:
        rs = Utils.relative_strength(close, index_close)
        sma_rs = rs.rolling(period).mean()
        return ((rs / sma_rs - 1) * 100).round(2)

    @staticmethod
    def simple_moving_average(
            close: pd.Series,
            period: int = 40
    ) -> pd.Series:
        return close.rolling(period).mean().round(2)

    @staticmethod
    def exponential_moving_average(
            close: pd.Series,
            period: int = 40
    ) -> pd.Series:
        alpha = 2 / (period + 1)
        return close.ewm(alpha=alpha).mean().round(2)
