import json
from typing import List
from tqdm import tqdm
import yfinance as yf
from logic.engine import Engine
from logic.services.base_service import BaseService


class FetchingTradingService(BaseService):

    def __init__(self, engine: Engine):
        super().__init__(engine)

    def fetch_history(
            self,
            name: str,
            symbols: List[str] = None,
            period="1d"):
        def main_process():
            tickers = yf.Tickers(" ".join(symbols))
            for ticker_symbol in tqdm(symbols, desc=f"Fetching {name} trading history"):
                try:
                    # get ticker object
                    ticker = tickers.tickers[ticker_symbol]
                    # Save the treading to a csv file
                    history = ticker.plot_trading(period=period)
                    self.engine.csv("daily", f"{ticker_symbol}.csv").save_df(history)
                except Exception as e:
                    self.logger.error(f"Error: fetch {ticker_symbol} trading history - got Error:{e}")

        # run main_process with logging
        self.logging_process_time(
            name,
            logging_file_path=self.config.FOLDER_Watch / "tradings_fetch_status.json",
            method_to_run=main_process)


    def fetch_history_by_sector_or_industry(
            self,
            category: str,
            category_names: List[str],
            period="1d"):
        # get symbol list base on category (sector or industry)
        json_file_path = self.config.FOLDER_Watch / f"symbols_{category}.json"
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for category_name in category_names:
            if category_name in data["detail"]:
                symbols: List[str] = data["detail"][category_name]
                # fetch fetching treading
                self.fetch_history(
                    name=f"{category}.{category_name}",
                    symbols=symbols,
                    period=period)


    def fetch_history_by_mylist(
            self,
            period="1d"):
        self.fetch_history(
            name="mylist",
            symbols=self.config.LIST_Watch,
            period=period)
