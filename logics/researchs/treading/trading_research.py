import json
import importlib
import pandas as pd
import concurrent
from tqdm import tqdm
from pathlib import Path
from datetime import datetime, timedelta
from argparse import ArgumentParser
from concurrent.futures import Future
from apps.common.models import *
from logics.researchs.treading.patterns import pattern
from logics.service import Service
from logics.researchs.base_research import BaseResearch
from typing import Tuple, Callable, List, Optional
from logics.services.loading.loader import AbstractLoader
from logics.researchs.treading.patterns.method import PatternDetector


class TradingResearch(BaseResearch):

    def __init__(self, service: Service, args: ArgumentParser):
        super().__init__(service)
        # Setup instance, args, etc.
        self.args: ArgumentParser = args
        self.PatternDetector = PatternDetector(self.logger)

        # Dynamically initialize the loader
        if args is not None:
            loader_name = self.config.__dict__.get("LOADER", "csv_engine:CsvEngine")
            module_name, class_name = loader_name.split(":")
            loader_module = importlib.import_module(f"src.services.loading.loader.{module_name}")
            self.loader = getattr(loader_module, class_name)(
                config=self.config.__dict__,
                tf=args.tf,
                end_date=args.date)

    def _cleanup(self, loader: AbstractLoader, futures: List[concurrent.futures.Future]):
        if futures:
            for future in futures:
                future.cancel()
            concurrent.futures.wait(futures)
        if loader.closed:
            loader.close()

    def _scan_pattern(
            self,
            symbol: str,
            functions: Tuple[Callable, ...],
            loader: AbstractLoader,
            bars_left: int = 6,
            bars_right: int = 6
    ) -> List[dict]:
        # initialize result: patterns
        patterns: List[dict] = []

        # Load symbol (default loader is csv trading_data_loader)
        df = loader.get(symbol)

        if df is None or df.empty:
            return patterns

        if df.index.has_duplicates:
            df = df[~df.index.duplicated()]
        # get feature points
        pivots = self.PatternDetector.get_max_min(
            df=df,
            bars_left=bars_left,
            bars_right=bars_right)

        if not pivots.shape[0]:
            return patterns

        # main loop to scan for patterns
        for function in functions:
            if not callable(function):
                raise TypeError(f"Expected callable. Got {type(function)}")
            try:
                result = function(self.PatternDetector, symbol, df, pivots)
            except Exception as e:
                self.logger.exception(f"SYMBOL name: {symbol}", exc_info=e)
                return patterns
            # add detected patterns into result
            if result:
                patterns.append(self.PatternDetector.make_serializable(result))

        return patterns

    def _process_by_pattern(
            self,
            symbol_list: List,
            fns: Tuple[Callable, ...],
            futures: List[concurrent.futures.Future]
    ) -> List[dict]:
        patterns: List[dict] = []
        # Load or initialize state dict for storing previously detected patterns
        state = None
        state_file = None
        filtered = None

        if self.config.__dict__.get("SAVE_STATE", False) and self.args.file and not self.args.date:
            state_file = self.config.FOLDER_States / f"{self.args.file.stem}_{self.args.pattern}.json"
            if not state_file.parent.is_dir():
                state_file.parent.mkdir(parents=True)
            state = json.loads(state_file.read_bytes()) if state_file.exists() else {}

        # determine the folder to save to in a case save option is set
        save_folder: Optional[Path] = None
        image_folder = f"{datetime.now():%d_%b_%y_%H%M}"
        if "SAVE_FOLDER" in self.config.__dict__:
            save_folder = Path(self.config.__dict__["SAVE_FOLDER"]) / image_folder
        if self.args.save:
            save_folder = self.args.save / image_folder
        if save_folder and not save_folder.exists():
            self.path_exist(save_folder)

        # begin a scan process
        with concurrent.futures.ProcessPoolExecutor() as executor:
            # load concurrent task
            for sym in symbol_list:
                future = executor.submit(
                    self._scan_pattern,
                    symbol=sym,
                    functions=fns,
                    loader=self.loader,
                    bars_left=self.args.left,
                    bars_right=self.args.right)
                futures.append(future)

            for future in tqdm(
                    iterable=concurrent.futures.as_completed(futures),
                    total=len(futures)
            ):
                try:
                    result = future.result()
                except Exception as e:
                    self._cleanup(self.loader, futures)
                    self.logger.exception("Error in Future - scanning patterns", exc_info=e)
                    return []
                patterns.extend(result)
            futures.clear()

            if state is not None:
                # if no args.file option, no need to save state, return patterns
                # Filter for newly detected patterns and remove stale patterns

                # list for storing newly detected patterns
                filtered = []
                # initial length of state dict
                len_state = len(state)
                # Will contain keys to all patterns currently detected
                detected = set()
                for dct in patterns:
                    # unique identifier
                    key = f'{dct["sym"]}-{dct["patterns"]}'
                    detected.add(key)
                    if not len_state:
                        # if the state is empty, this is a first run
                        # no need to filter
                        state[key] = dct
                        filtered.append(dct)
                        continue
                    if key in state:
                        if dct["start"] == state[key]["start"]:
                            # if the patterns starts on the same date,
                            # they are the same previously detected patterns
                            continue
                        # Else there is a new patterns for the same key
                        state[key] = dct
                        filtered.append(dct)
                    # new patterns
                    filtered.append(dct)
                    state[key] = dct
                # set difference - get keys in state dict not existing in detected
                # These are patterns keys no longer detected and can be removed
                invalid_patterns = set(state.keys()) - detected
                # Clean up stale patterns in state dict
                for key in invalid_patterns:
                    state.pop(key)
                if state_file:
                    state_file.write_text(json.dumps(state, indent=2))
                    self.logger.info(
                        f"\nTo view all current market patterns, run `py init.py --plot state/{state_file.name}\n"
                    )

            patterns_to_output = patterns if state is None else filtered
            if not patterns_to_output:
                return []
            # Save the images if required
            if save_folder:
                plotter = self.service.saving().plot_trading(
                    data=None,
                    loader=self.loader,
                    save_folder=save_folder)
                for i in patterns_to_output:
                    future = executor.submit(plotter.save, i.copy())
                    futures.append(future)

                self.logger.info("Saving images")

                for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
                    try:
                        future.result()
                    except Exception as e:
                        self._cleanup(self.loader, futures)
                        self.logger.exception("Error in Futures - Saving images ", exc_info=e)
                        return []

        patterns_to_output.append({
            "timeframe": self.loader.timeframe,
            "end_date": self.args.date.isoformat() if self.args.date else None,
        })
        return patterns_to_output

    # Public methods
    def process_by_pattern_name(
            self,
            symbol_list: List,
            pattern_name: str,
            futures: List[concurrent.futures.Future]
    ) -> List[dict]:

        fn_dict = pattern.get_pattern_dict()
        key_list = pattern.get_pattern_list()
        # Get function out
        fn = fn_dict[pattern_name]

        # check functions
        if callable(fn):
            fns = (fn,)
        elif fn == "bull":
            bull_list = ("vcpu", "hnsu", "dbot")
            fns = tuple(v for k, v in fn_dict.items() if k in bull_list and callable(v))
        elif fn == "bear":
            bear_list = ("vcpd", "hnsd", "dtop")
            fns = tuple(v for k, v in fn_dict.items() if k in bear_list and callable(v))
        else:
            fns = tuple(v for k, v in fn_dict.items() if k in key_list[3:] and callable(v))

        try:
            return self._process_by_pattern(symbol_list, fns, futures)
        except KeyboardInterrupt:
            self._cleanup(self.loader, futures)
            self.logger.info("User exit")
            exit()

    def get_stock_hist_bars_by_date(self, symbols: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        Retrieve stock historical bars data based on symbols and date range.

        :param symbols: List of stock symbols.
        :param start_date: Start date in 'YYYY-MM-DD' format.
        :param end_date: End date in 'YYYY-MM-DD' format.
        :return: DataFrame with stock historical bars data.
        """
        # Adjust end_date by adding 12 hours
        end_date_with_time = f"{end_date} 12:00:00"

        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    symbol, time, open, high, low, close, volume
                FROM market_stock_hist_bars_day_ts
                WHERE symbol IN ({','.join(f"'{symbol}'" for symbol in symbols)})
                    AND time BETWEEN %s AND %s
            """, [start_date, end_date_with_time])
            rows = cursor.fetchall()

            if not rows:
                return pd.DataFrame()

            # Convert the fetched rows into a DataFrame
            columns = [col[0] for col in cursor.description]
            return pd.DataFrame([dict(zip(columns, row)) for row in rows])


    def get_stock_hist_bars(self, is_day, symbols: list[str], row_num: int):
        table_name = 'day' if is_day else 'min'
        with connection.cursor() as cursor:
            cursor.execute(f"""
    SELECT
        mk.symbol,
        mk.name as symbol_name,
        sub.date,
        main_start.open,
        main_end.close,
        sub.volume,
        sub.*
    FROM
        market_symbol mk
        LEFT JOIN LATERAL(
            SELECT
                symbol,
                ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY MAX(DATE(time)) DESC) AS row_num,
                MAX(DATE(time)) AS max_date,
                DATE(time) AS date,
                MIN(time) AS start_min,
                MAX(time) AS end_min,
                SUM(volume) AS volume
            FROM
                market_stock_hist_bars_{table_name}_ts
            WHERE
                symbol IN ('{"', '".join(symbols)}')
            GROUP BY
                symbol, DATE(time)
        ) sub ON sub.symbol = mk.symbol
        LEFT JOIN market_stock_hist_bars_{table_name}_ts main_start 
            ON main_start.symbol = sub.symbol AND main_start.time = sub.start_min
        LEFT JOIN market_stock_hist_bars_{table_name}_ts main_end 
            ON main_end.symbol = sub.symbol AND main_end.time = sub.end_min
    WHERE
        sub.row_num = {row_num} AND mk.symbol IN ('{"', '".join(symbols)}')
                """)
            latest_rows = cursor.fetchall()

            # Convert the fetched rows into a list of dictionaries
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in latest_rows]

    def get_stock_full_hist_bars(self, is_day, symbols: list[str]):
        table_name = 'day' if is_day else 'min'
        with connection.cursor() as cursor:
            cursor.execute(f"""
            SELECT
                symbol,
                DATE(time) AS date,
                MAX(close) AS close,
                MAX(high) AS high,
                MAX(low) AS low,
                SUM(volume) AS volume
            FROM
                market_stock_hist_bars_{table_name}_ts
            WHERE
                symbol IN ('{"', '".join(symbols)}')
            GROUP BY
                symbol, DATE(time)
                """)
            rows = cursor.fetchall()
            return rows

    def get_stock_prices(self, symbol_date_pairs: List[Tuple[str, str]], row_delta: int = 0) -> pd.DataFrame:
        """
        Retrieve stock prices from market_stock_hist_bars_day_ts based on symbol and date.

        :param symbol_date_pairs: List of tuples containing symbol and date.
        :param row_delta: Integer to adjust the row number for fetching the bar record.
        :return: DataFrame with stock prices.
        """
        # Extract unique symbols from symbol_date_pairs
        symbols = list(set(symbol for symbol, _ in symbol_date_pairs))

        dates = [pd.to_datetime(date) for _, date in symbol_date_pairs]
        # Determine the earliest and latest dates
        earliest_date = min(dates) - timedelta(days=5)
        latest_date = max(dates) + timedelta(days=5)

        with connection.cursor() as cursor:
            # Retrieve all records for the given symbols
            cursor.execute(f"""
                SELECT 
                       ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY time) AS row_num, symbol, time, open, high, low, close, volume
                FROM market_stock_hist_bars_day_ts
                WHERE symbol IN ({','.join(f"'{symbol}'" for symbol in symbols)})
                    AND time BETWEEN %s AND %s
            """, [earliest_date, latest_date])
            rows = cursor.fetchall()
            if not rows:
                return pd.DataFrame()
            # Convert the fetched rows into a DataFrame
            columns = [col[0] for col in cursor.description]
            df = pd.DataFrame([dict(zip(columns, row)) for row in rows])

        stock_prices = []

        # Group by symbol and apply the logic
        for symbol, group in df.groupby('symbol'):
            for _, date in filter(lambda x: x[0] == symbol, symbol_date_pairs):
                # Locate the row number based on the date
                row_num = group.loc[group['time'].dt.date == pd.to_datetime(date).date(), 'row_num'].values[0]

                # Calculate the final index using row_delta
                final_row_num = row_num + row_delta

                if 0 <= final_row_num < len(group):
                    row_data = group[group['row_num'] == final_row_num].iloc[0].to_dict()
                    row_data['symbol'] = symbol
                    row_data['date'] = date
                    stock_prices.append(row_data)

        # Convert the list of dictionaries to a DataFrame
        return pd.DataFrame(stock_prices)
