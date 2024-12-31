import pickle
import numpy as np
import pandas as pd
import mplfinance as mpl
from datetime import timedelta
from functools import lru_cache
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from argparse import ArgumentParser

from ...research import Research
from ...utilities.utils import Utils
from ..base_chart import BaseChart
from matplotlib.collections import LineCollection

HELP = """
## Help ##
Shift + H   Toggle help text                 
R               Reset to original view
N               Next chart                          
F                Fullscreen
P               Previous chart
G               Toggle Major Grids
Q               Quit trading_pattern_chart.py
O               Zoom to Rect
D               Toggle draw mode

## Draw mode controls ##
Horizontal Line :            Left Mouse click
(AxHLine)
Trend Line (TLine) :       Hold Shift key + left mouse click two points on chart
Segments (ALine) :        Hold Control key + left mouse click two or more points
Horizontal Segment :     Hold Ctrl + Shift key + left mouse click two points
(HLine)
Delete Line: Right mouse click on line
Delete all lines: Hold Shift key + right mouse click
"""


def format_coordination(x, _):
    s = " " * 5
    if df is None:
        return
    if not x or round(x) >= df.shape[0]:
        return ""

    dt = df.index[round(x)]
    dt_str = f"{dt:%d %b %Y}".upper()
    open, high, low, close, vol = df.loc[dt, ["Open", "High", "Low", "Close", "Volume"]]
    _str = f"{dt_str}{s}O: {open}{s}H: {high}{s}L: {low}{s}C: {close}{s}V: {vol:,.0f}"

    if "M_RS" in df.columns:
        _str += f'{s}MRS: {df.loc[dt, "M_RS"]}'
    elif "RS" in df.columns:
        _str += f'{s}RS: {df.loc[dt, "RS"]}'
    return _str


def auto_redraw(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        self.fig.canvas.draw_idle()
        return result

    return wrapper


class TradingPatternChart(BaseChart):
    idx = len = 0
    line = []
    events = []
    title = None
    draw_mode = False
    helpText = None

    line_args = {
        "linewidth": 1,
        "mouseover": True,
        "pickradius": 3,
        "picker": True
    }

    segment_args = {
        "pickradius": 3,
        "picker": True,
        "colors": ["crimson"]
    }

    title_args = {
        "loc": "right",
        "fontdict": {"fontweight": "bold"}
    }

    def __init__(
            self,
            analyse: Research,
            args,
            plugins,
            parser: ArgumentParser):
        super().__init__(analyse)
        plt.ioff()
        self.args = args
        self.plugins = plugins
        self.parser = parser
        self.daily_dir = self.config.FOLDER_Daily
        # set parameters for args preset
        if args.preset and args.preset_save:
            exit("trading_pattern_chart.py: error: argument --preset: not allowed with argument --preset-save")
        if args.preset:
            args = self._load_preset(args.preset)
            self.args = args
        self.tf = args.tf

        # watch & preset
        if args.watch_add:
            self._save_watch(*args.watch_add)
        if args.preset_save:
            self._save_preset(args.preset_save)
        if args.watch_rm:
            self._remove_watch(args.watch_rm)
        if args.preset_rm:
            self._remove_preset(args.preset_rm)
        # watch_list & preset_list
        if args.ls:
            self._list_watch_and_preset()
        # period & local period
        if args.period:
            self.period = args.period
        else:
            if self.tf == "Weekly":
                self.period = self.config.PLOT_WEEKS
            else:
                self.period = self.config.PLOT_DAYS
        self.plot_args = {
            "type": self.config.PLOT_CHART_TYPE,
            "style": self.config.PLOT_CHART_STYLE,
            "volume": args.volume,
            "xrotation": 0,
            "datetime_format": "%d %b %y",
            "figscale": 2,
            "returnfig": True,
            "scale_padding": {
                "left": 0.28,
                "right": 0.65,
                "top": 0.3,
                "bottom": 0.38,
            }
        }
        # save
        if args.save:
            # set parameters
            self.plot_args["figsize"] = self.config.PLOT_SIZE \
                if hasattr(self.config, "PLOT_SIZE") else (12, 6)
            self.plot_args["figscale"] = 1
            self.save_dir = self.config.FOLDER_Charts
            # set save directory
            if args.preset:
                self.save_dir = self.save_dir / args.preset
            elif args.preset_save:
                self.save_dir = self.save_dir / args.preset_save
            elif args.watch:
                self.save_dir = self.save_dir / args.watcb
            # create directory
            if not self.save_dir.exists():
                self.save_dir.mkdir(parents=True)
        # watch
        if args.watch:
            self.symbol_list = self._load_watch_list(args.watch)
        # symbol
        if args.sym:
            self.symbol_list = args.sym
        # add some period for sma, ema calculation
        self.max_period = self._get_max_period()
        if args.rs or args.m_rs:
            idx_path = self.daily_dir / f"{self.config.PLOT_RS_INDEX}.csv"
            if not idx_path.is_file():
                exit(f"Index file not found: {idx_path}")
            self.idx_cl = self.service.loading().trading(idx_path).get_data_frame(
                tf=self.tf,
                period=self.max_period,
                column="Close",
                to_date=self.args.date
            )

    def plot(self, symbol):
        # Step 1. Prepare data
        global df
        self.draw_mode = False
        self.has_updated = False
        # Step 1.a meta
        symbol = symbol.upper()
        meta = None
        if "," in symbol:
            symbol, *meta = symbol.split(",")
        # Step 1.b. data frame
        df = self._prep_data(symbol)
        if df is None:
            self.key = "n"
            print(f"WARN: Could not find symbol - {symbol.upper()}")
            return
        # Step 1.c. arguments
        self._prep_arguments(symbol, df, meta)

        # Step 2. run plugins
        self.plugins.process_by_pattern_name(df, self)
        if self.args.save:
            return df

        # Step 3. local
        fig, axs = mpl.plot(df, **self.plot_args)
        # A workaround using ConciseDateFormatter and AutoDateLocator
        # with mplfinance
        # See github issue https://github.com/matplotlib/mplfinance/issues/643

        # Step 4. set xaxis locator and formatter
        # locator sets the major tick locations on xaxis
        locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
        # Formatter set the tick labels for the xaxis
        concise_formatter = mdates.ConciseDateFormatter(locator=locator)

        # Extract the tick values from locator.
        # These are matplotlib dates not python datetime
        tick_mdates = locator.tick_values(df.index[0], df.index[-1])

        # Extract the tick labels from the ConciseDateFormatter
        labels = concise_formatter.format_ticks(tick_mdates)
        ticks = self._get_tick_locations(tick_mdates, df.index)

        # Initialise Fixed Formatter and Fixed Locator
        # passing the tick labels and tick positions
        fixed_formatter = ticker.FixedFormatter(labels)
        fixed_locator = ticker.FixedLocator(ticks)

        fixed_formatter.set_offset_string(concise_formatter.get_offset())

        for ax in axs:
            ax.xaxis.set_major_locator(fixed_locator)
            ax.xaxis.set_major_formatter(fixed_formatter)
            ax.format_coord = format_coordination

        self.connection_id = fig.canvas.mpl_connect("key_press_event", self._on_key_press)
        self.fig = fig
        self.main_ax = axs[0]

        self.main_ax.set_title(
            f"#{self.idx + 1} of {self.len}",
            loc="left",
            color="black",
            fontdict={"fontweight": "bold"}
        )

        lines_path = self.config.FOLDER_Lines / f"{symbol}.p"

        default_lines = {
            "artists": [],
            "daily": {"length": 0, "lines": {}},
            "weekly": {"length": 0, "lines": {}},
        }

        lines = pickle.loads(lines_path.read_bytes()) if lines_path.exists() else default_lines
        if lines[self.tf]["length"] > 0:
            self._load_lines(lines)
        else:
            self.lines = lines

        print(f"Plotting [{symbol.upper()}]")
        mpl.show(block=True)
        print(f"show [{symbol.upper()}]")

        if "addplot" in self.plot_args:
            self.plot_args["addplot"].clear()

        daily_len = self.lines["daily"]["length"]
        weakly_len = self.lines["weekly"]["length"]

        if daily_len == 0 and weakly_len == 0 and lines_path.is_file():
            return lines_path.unlink()

        if self.has_updated:
            if not lines_path.parent.exists():
                lines_path.parent.mkdir(parents=True)
            lines_path.write_bytes(pickle.dumps(self.lines))

    # <editor-fold desc="Watch">
    def _load_watch_list(self, watch):
        if watch.upper() not in self.config.WATCH:
            exit(f"Error: No watchlist named '{watch}'")
        file = self.config.FOLDER_Watch / self.config.WATCH[watch.upper()]
        if not file.is_file():
            exit(f"Error: File not found {file}")
        return file.read_text().strip("\n").split("\n")

    def _save_watch(self, watch_name, watch_value):
        # Add
        data = self.engine.json_user().load_symbol_history() if self.engine.json_user().is_file() else {}
        if "WATCH" not in data:
            data["WATCH"] = {}
        data["WATCH"][watch_name.upper()] = watch_value
        # Save
        self.engine.json_user().save(data)
        exit(f"Added watchlist '{watch_name}' with value '{watch_value}'")

    def _remove_watch(self, name):
        # Check
        if name.upper() not in getattr(self.config, "WATCH"):
            exit(f"Error: No watchlist named: '{name}'")
        if not self.engine.json_user().is_file():
            exit("No config file")
        # Delete
        data = self.engine.json_user().load_symbol_history()
        if "WATCH" not in data or name.upper() not in data["WATCH"]:
            exit(f"Error: No watchlist named: '{name}'")
        del data["WATCH"][name.upper()]
        # Save
        self.engine.json_user().save(data)
        exit(f"Watchlist '{name}' removed.")

    # </editor-fold>

    # <editor-fold desc="Preset">
    def _load_preset(self, preset):
        # Check
        if preset not in getattr(self.config, "PRESET"):
            exit(f"Error: No preset named: '{preset}'")
        # Load
        args_dct = getattr(self.config, "PRESET")[preset]
        if self.args.resume:
            args_dct["resume"] = True
        return self.parser.parse_args(Utils.arg_parse_dict(args_dct))

    def _save_preset(self, preset):
        # Check
        if self.args.watch and self.args.watch.upper() not in self.config.WATCH:
            exit(f"Error: No watchlist named: '{self.args.watch}'")
        # Prepare
        data = self.engine.json_user() if self.engine.json_user().is_file() else {}
        # get a copy of __dict__ and filter only truthy values into a dict
        opts = {k: v for k, v in self.args.__dict__.items() if v}
        del opts["preset_save"]
        if "PRESET" not in data:
            data["PRESET"] = {}
        data["PRESET"][preset] = opts
        # Save
        self.engine.json_user().save(data)
        print(f"Preset saved as '{preset}'")

    def _remove_preset(self, preset):
        # Check
        if preset not in getattr(self.engine.config, "PRESET"):
            exit(f"Error: No preset named: '{preset}'")
        if not self.engine.json_user().is_file():
            exit(f"File not found: {self.engine.json_user().Path}")
        # Delete
        data = self.engine.json_user().load_symbol_history()
        if "PRESET" not in data or preset not in data["PRESET"]:
            exit(f"Error: No preset named: '{preset}'")
        del data["PRESET"][preset]
        # Save
        self.engine.json_user().save(data)
        exit(f"Preset '{preset}' removed.")

    # </editor-fold>

    # <editor-fold desc="Watch & Preset List">
    def _list_watch_and_preset(self):
        # setup watch list and preset list
        self.watch_list = [i.lower() for i in self.config.WATCH.keys()] \
            if hasattr(self.engine.config, "WATCH") else []
        self.preset_lst = [i.lower() for i in self.config.PRESET.keys()] \
            if hasattr(self.engine.config, "PRESET") else []

        # check & result
        if not len(self.watch_list):
            print("No Watch lists")
        else:
            print(f"Watch lists: {','.join(self.watch_list)}")
        if not len(self.preset_lst):
            print("No Presets")
        else:
            print(f"Presets: {','.join(self.preset_lst)}")
        exit()

    # </editor-fold>

    # <editor-fold desc="line">
    def _load_lines(self, lines):
        if df is None:
            return

        self.lines = lines
        if self.tf not in self.lines:
            return

        for url in self.lines[self.tf]["lines"]:
            _type, _value = url.split(":")
            coord = self.lines[self.tf]["lines"][url]

            if _type == "axhline":
                self._add_hline(self.main_ax, coord, url=url)
                continue
            if _type == "hline":
                y, x_min, x_max = coord
                # check for DataFrame index out of bounds errors
                try:
                    # Draw line to specified point on x-axis else draw to end
                    if x_max is not None:
                        x_max = df.index.get_loc(x_max)
                    coord = (y, df.index.get_loc(x_min), x_max)
                except KeyError:
                    continue

                self._add_horizontal_segment(self.main_ax, *coord, url=url)
                continue

            try:
                coord = tuple((df.index.get_loc(x), y) for x, y in coord)
            except KeyError:
                continue

            if _type == "tline":
                self._add_tline(self.main_ax, coord, url=url)
            elif _type == "aline":
                self._add_aline(self.main_ax, coord, url=url)

    def _add_hline(self, axes, y, url=None):
        """Draw a horizontal that extends both sides"""

        if url is None:
            # increment only if its newly drawn line
            self.lines[self.tf]["length"] += 1
            url = f"axhline:{self.tools.random_char(6)}"
            self.lines[self.tf]["lines"][url] = y
            self.has_updated = True

        self.line_args["color"] = self.config.PLOT_AXHLINE_COLOR
        line = axes.axhline(y, url=url, **self.line_args)
        self.lines["artists"].append(line)

    def _add_horizontal_segment(self, axes, y, x_min, x_max=None, url=None):
        """Draw a horizontal line segment"""
        if df is None:
            return

        if url is None:
            # increment only if its newly drawn line
            self.lines[self.tf]["length"] += 1
            url = f"hline:{self.tools.random_char(6)}"
            self.lines[self.tf]["lines"][url] = (
                y,
                df.index[x_min],
                df.index[x_max] if x_max else None
            )
            self.has_updated = True

        if x_max is None:
            # draw line till end of x-axis
            x_max = df.index.get_loc(df.index[-1])

        self.segment_args["colors"] = (self.config.PLOT_HLINE_COLOR)
        line = axes.hlines(y, x_min, x_max, url=url, **self.segment_args)
        self.lines["artists"].append(line)

    def _add_tline(self, axes, coords, url=None):
        """Draw trendlines passing through 2 points"""
        if df is None:
            return

        if url is None:
            # increment only if its newly drawn line
            self.lines[self.tf]["length"] += 1
            url = f"tline:{self.tools.random_char(6)}"
            self.lines[self.tf]["lines"][url] = tuple(
                (df.index[x], y) for x, y in coords
            )
            self.has_updated = True

        self.line_args["color"] = self.config.PLOT_TLINE_COLOR
        # Second click to get ending coordinates
        line = axes.axline(*coords, url=url, **self.line_args)
        self.lines["artists"].append(line)

    def _add_aline(self, axes, coords, url=None):
        """Draw arbitrary line connecting 2 points"""
        if df is None:
            return

        if url is None:
            # increment only if its newly drawn line
            self.lines[self.tf]["length"] += 1
            url = f"aline:{self.tools.random_char(6)}"
            self.lines[self.tf]["lines"][url] = tuple(
                (df.index[x], y) for x, y in coords
            )
            self.has_updated = True

        self.segment_args["colors"] = (self.config.PLOT_ALINE_COLOR,)
        line = LineCollection([coords], url=url, **self.segment_args)
        axes.add_collection(line)
        self.lines["artists"].extend(line)

    # </editor-fold>

    # <editor-fold desc="Key Press">
    @auto_redraw
    def _on_key_press(self, event):
        if event.key not in ("n", "p", "q", "d", "h"):
            return
        if event.key == "d":
            return self._toggle_draw_mode()
        if event.key == "h":
            if self.helpText is None:
                x = self.main_ax.get_xlim()[0]
                y = self.main_ax.get_ylim()[0]
                self.helpText = self.main_ax.text(
                    x, y, HELP,
                    color="darkslategrey",
                    backgroundcolor="mintcream",
                    fontweight="bold"
                )
            else:
                self.helpText.remove()
                self.helpText = None
            return

        # artists are not json serializable
        self.lines["artists"].clear()
        if event.key == "p" and self.idx == 0:
            print("\nAt first Chart")
            return
        self.key = event.key
        plt.close("all")

    @auto_redraw
    def _toggle_draw_mode(self):
        if self.draw_mode:
            self.draw_mode = False
            for event in self.events:
                self.fig.canvas.mpl_disconnect(event)
            self.main_ax.set_title("", **self.title_args)
            self.events.clear()
        else:
            self.draw_mode = True
            self.main_ax.set_title("DRAW MODE", **self.title_args)

            if self.connection_id is not None:
                self.fig.canvas.mpl_disconnect(self.connection_id)
            else:
                self.events.append(self.fig.canvas.mpl_disconnect("key_release_event", self._on_key_release))
            self.events.append(self.fig.canvas.mpl_connect("button_press_event", self._on_button_press))
            self.events.append(self.fig.canvas.mpl_connect("pick_event", self._on_pick))

    @auto_redraw
    def _on_key_release(self, event, *args, **kwargs):
        if event.key not in ("control", "shift", "ctrl+shift"):
            return
        if event.key == "ctrl+shift" and len(self.line) == 2:
            # On release after first click,
            # Draw a horizontal line segment from x_min to x_-axis end
            y, x_min = self.line
            self._add_horizontal_segment(event.inaxes, y, x_min)
        self.main_ax.set_title("DRAW MODE", **self.title_args)
        self.line.clear()

    @auto_redraw
    def _on_button_press(self, event):
        if df is None:
            return
        # right mouse click to delete lines
        if event.button == 3:
            return self._delete_line(event.key)
        # add horizontal line
        # return if data is out of bounds
        if event.xdata is None or event.xdata > df.shape[0]:
            return

        x = round(event.xdata)
        y: object = round(event.ydata, 2)

        if self.config.MAGNET_MODE:
            y = self._get_closest_price(x, y)
        if event.key is None:
            self._add_hline(event.inaxes, y)

        if event.key not in ("control", "shift", "ctrl+shift"):
            return

        # shift + mouse click to assign coord for trend line
        # draw trend line
        # first click to get starting coordinates
        self.main_ax.set_title("LINE MODE", **self.title_args)

        if event.key == "control":
            if len(self.line) == 0:
                return self.line.append((x, y))
            self.line.append((x, y))

            if len(self.line) == 2:
                coord = self.line.copy()
                self.line[0] = self.line.pop()
                return self._add_aline(event.inaxes, coord)

        if event.key == "ctrl+shift":
            if len(self.line) == 0:
                return self.line.append((y, x))
            self.line.append(x)
            # ctrl + shift to add a horizontal segment between two dates
            self._add_horizontal_segment(event.inaxes, *self.line)
            return self.line.clear()

        if event.key == "shift":
            # Cannot draw a line through identical points
            if len(self.line) == 1 and y == self.line[0][1]:
                return
            self.line.append((x, y))
            if len(self.line) == 2:
                self._add_tline(event.inaxes, self.line)
                self.line.clear()
                self.main_ax.set_title("DRAW MODE", **self.title_args)

    @auto_redraw
    def _on_pick(self, event):
        if event.mouseevent.button == 3:
            return self._delete_line("", artist=event.artist)
        return

    def _delete_line(self, key, artist=None):
        if key == "shift":
            for lineArtist in self.lines["artists"].copy():
                lineArtist.remove()

            self.lines[self.tf]["length"] = 0
            self.lines["artists"].clear()
            self.lines[self.tf]["lines"].clear()
            self.has_updated = True
            return

        if artist and artist in self.lines["artists"]:
            url = artist.get_url()

            artist.remove()
            self.lines["artists"].remove(artist)
            self.lines[self.tf]["lines"].pop(url)
            self.lines[self.tf]["length"] -= 1
            self.has_updated = True

        return

    def _get_closest_price(self, x, y):
        if df is None:
            return
        _open, _high, _low, _close, *_ = df.iloc[x]
        if y >= _high:
            # if a pointer is at or above, high snap to high
            closest = _high
        elif y <= _low:
            # if a pointer is at or below, low snap to low
            closest = _low
        else:
            # else if a pointer is inside the candle and
            # snap to the nearest open or close (absolute distance)
            o_dist = abs(_open - y)
            c_dist = abs(_close - y)
            closest = _open if o_dist < c_dist else _close
        return closest

    # </editor-fold>

    # <editor-fold desc="Prepare data * arguments">
    @lru_cache(maxsize=6)
    def _prep_data(self, symbol):
        # Step 1. check data source
        f_path = self.config.FOLDER_Daily / f"{symbol}.csv"
        if not f_path.is_file():
            f_path = self.daily_dir / f"{symbol.lower()}_sme.csv"
            if not f_path.is_file():
                return None
        # Step 2. load data into data frame
        df = self.service.loading().trading(f_path).get_data_frame(
            tf=self.tf,
            period=self.max_period,
            to_date=self.args.date
        )
        # Step 3. calculate indicators
        df_len = df.shape[0]
        plot_period = min(self.period, df_len)
        # Step 3.a calculate relative strength
        if self.args.rs:
            df["RS"] = Utils.relative_strength(df["Close"], self.idx_cl)
        # Step 3.b. calculate mansfield relative strength
        if self.args.m_rs:
            rs_period = self.config.PLOT_M_RS_LEN_W if self.tf == "weekly" else self.config.PLOT_M_RS_LEN_D
            # check: prevent crash if local period is less than RS period
            if df_len < rs_period:
                print(f"WARN: {symbol.upper()} - Inadequate data to plot Mansfield RS. less than {rs_period} candles")
            df["M_RS"] = Utils.mansfield_relative_strength(df["Close"], self.idx_cl, rs_period)
        # Step 3.c. calculate simple moving average
        if self.args.sma:
            for period in self.args.sma:
                if df_len < period:
                    print(f"WARN: {symbol.upper()} - Inadequate data to plot SMA. less than {period} candles")
                df[f"SMA_{period}"] = Utils.simple_moving_average(df["Close"], period=period)
        # Step 3.d. calculate exponential moving average
        if self.args.ema:
            for period in self.args.ema:
                if df_len < period:
                    print(f"WARN: {symbol.upper()} - Inadequate data to plot EMA. less than {period} candles")
                df[f"EMA_{period}"] = Utils.exponential_moving_average(df["Close"], period=period)
        # Step 3.e. calculate volume moving average
        if self.args.vol_sma:
            for period in self.args.vol_sma:
                if df_len < period:
                    print(f"WARN: {symbol.upper()} - Inadequate data to plot Volume SMA. less than {period} candles")
                df[f"VMA_{period}"] = Utils.simple_moving_average(df["Volume"], period=period)

        # Step 4. prepare data for plotting
        start_dt = df.index[-plot_period] - timedelta(days=7) \
            if self.tf == "weekly" else df.index[-plot_period] - timedelta(days=1)
        df.loc[start_dt] = np.nan
        df = df.sort_index()
        return df[start_dt:]

    def _prep_arguments(self, symbol, df, meta):
        # Step 1. check parameters
        added_plots = []
        # Step 1.a. title
        self.title = f"{symbol.upper()} - {self.tf.capitalize()}"
        if meta is not None:
            self.title += f" | {'  '.join(meta).upper()}"
        self.plot_args["title"] = self.title
        self.plot_args["xlim"] = (0, df.shape[0] + 15)

        if self.args.save:
            img_name = f'"{symbol.repalce(" ", "-")}.png'
            self.plot_args["savefig"] = dict(fname=self.save_dir / img_name, dpi=300)
        # Step 2. add support and resistance line
        if self.args.snr:
            mean_candle_size = (df["High"] - df["Low"]).mean()
            self.plot_args["alines"] = {
                "alines": Utils.get_support_resistance_levels(df, mean_candle_size),
                "linewidths": 0.7,
            }
        # Step 3. draw Plot
        # Step 3.a. draw Dorsey Relative Strength local
        if self.args.rs:
            added_plots.append(
                mpl.make_addplot(
                    data=df["RS"], panel=1, ylabel="Dorsey RS",
                    color=self.config.PLOT_RS_COLOR, width=2.5
                )
            )
        # Step 3.b. draw Mansfield Relative Strength local
        if self.args.m_rs and "M_RS" in df.columns:
            zero_line = pd.Series(data=0, index=df.index)
            added_plots.extend(
                [
                    mpl.make_addplot(
                        data=df["M_RS"], panel="lower", ylabel="Mansfield RS",
                        color=self.config.PLOT_M_RS_COLOR, width=2.5
                    ),
                    mpl.make_addplot(
                        data=zero_line, panel="lower", linestyle="dashed",
                        color=self.config.PLOT_M_RS_COLOR, width=1.5),
                ]
            )
        # Step 3.c. draw simple moving average
        if self.args.sma:
            for period in self.args.sma:
                if f"SMA_{period}" in df.columns:
                    added_plots.append(
                        mpl.make_addplot(data=df[f"SMA_{period}"], label=f"SMA{period}")
                    )
        # Step 3.d. draw exponential moving average
        if self.args.ema:
            for period in self.args.ema:
                if f"EMA_{period}" in df.columns:
                    added_plots.append(
                        mpl.make_addplot(data=df[f"EMA_{period}"], label=f"EMA{period}")
                    )
        # Step 3.e. draw volume moving average
        if self.args.vol_sma:
            for period in self.args.vol_sma:
                if f"VMA_{period}" not in df.columns:
                    continue
                added_plots.append(
                    mpl.make_addplot(
                        data=df[f"VMA_{period}"], panel="lower", label=f"VMA{period}", linewidths=0.7)
                )
        # Step 3.f. draw delivery levels
        if self.args.dlv and not df["DLV_QTY"].dropna().empty:
            Utils.get_delivery_levels(df, self.config)

            self.plot_args["marketcolor_overrides"] = df["MCOverrides"].values

            added_plots.append(
                mpl.make_addplot(
                    data=df["IM"], label="IM", type="scatter", color="midnightblue", marker="*"
                )
            )

        # Step 4. Add plots to plot_args
        if len(added_plots) > 0:
            self.plot_args["addplot"] = added_plots

    # </editor-fold>

    def _get_max_period(self):
        if self.tf == "Weekly":
            return self.config.PLOT_WEEKS
        else:
            return self.config.PLOT_DAYS

    def _get_tick_locations(self, tick_mdates, dtix: pd.DatetimeIndex):
        """Return the tick locations to be passed to Locator instance."""
        ticks = []

        # Convert the matplotlib dates to python datetime and iterate
        for dt in mdates.num2date(tick_mdates):
            # remove the timezone info to match the dataFrame index
            dt = dt.replace(tzinfo=None)

            # Get the index position if available
            # else get the next available index position
            idx = dtix.get_loc(dt) if dt in dtix else dtix.searchsorted(dt, side="right")
            # store the tick positions to be displayed on chart
            ticks.append(idx)

        return ticks
