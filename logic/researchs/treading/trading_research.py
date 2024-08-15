import json
import importlib
import concurrent
from tqdm import tqdm
from pathlib import Path
from datetime import datetime
from argparse import ArgumentParser
from concurrent.futures import Future
from logic.service import Service
from logic.researchs.base_research import BaseResearch
from typing import Tuple, Callable, List, Optional
from logic.services.loading.loader import AbstractLoader
from logic.researchs.treading.patterns.method import PatternDetector


class TradingResearch(BaseResearch):

    def __init__(self, service: Service, args: ArgumentParser):
        super().__init__(service)
        # Setup instance, args, etc.
        self.args: ArgumentParser = args
        self.PatternDetector = PatternDetector(self.logger)

        # Dynamically initialize the loader
        loader_name = self.config.__dict__.get("LOADER", "trading_csv_loader:TradingCsvLoader")
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
