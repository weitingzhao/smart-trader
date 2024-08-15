from argparse import ArgumentParser
from ta.momentum import RSIIndicator
from mplfinance import make_addplot
from pandas import Series

from src import Config


# To be added to src/setting/user.json
# "PLOT_PLUGINS": {
#     "RSI": {
#       "name": "rsi",
#       "overbought": 80,
#       "oversold": 20,
#       "line_color": "teal"
#     }
# }

def load(parser: ArgumentParser):
    parser.add_argument(
        "--rsi", action="store_true", help="Relative strength index"
    )


def main(df, plot_args, args, config: Config):
    if args.rsi:
        opts = config.PLOT_PLUGINS["RSI"]

        df["RSI"] = RSIIndicator(close=df["Close"]).rsi()

        if "addplot" not in plot_args:
            plot_args["addplot"] = []

        ob_line = Series(data=opts["overbought"], index=df.index)
        os_line = Series(data=opts["oversold"], index=df.index)

        plot_args["addplot"].extend(
            [
                make_addplot(
                    df["RSI"],
                    label="RSI",
                    panel="lower",
                    color=opts["line_color"],
                    ylabel="RSI",
                    width=2,
                ),
                make_addplot(
                    ob_line,
                    panel="lower",
                    color=opts["line_color"],
                    linestyle="dashed",
                    width=1.5,
                ),
                make_addplot(
                    os_line,
                    panel="lower",
                    color=opts["line_color"],
                    linestyle="dashed",
                    width=1.5,
                ),
            ]
        )
