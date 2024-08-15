import pandas as pd
import yfinance as yf
from tqdm import tqdm
from logic.engine import Engine
from logic.services.base_service import BaseService
from apps.fundamental.models import MarketSymbol


class FetchingSymbolService(BaseService):

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.API_KEY = self.config.API_KEY_Alphavantage

    def fetching_symbol(self):
        url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={self.API_KEY}'
        df = pd.read_csv(url)

        for index, row in df.iterrows():
            ipo_date = pd.to_datetime(row.get('ipoDate'), errors='coerce')
            delisting_date = pd.to_datetime(row.get('delistingDate'), errors='coerce')

            if pd.isna(ipo_date):
                ipo_date = None
            if pd.isna(delisting_date):
                delisting_date = None

            MarketSymbol.objects.update_or_create(
                symbol=row['symbol'],
                defaults={
                    'name': row['name'],
                    'market': row['exchange'],
                    'asset_type': row['assetType'],
                    'ipo_date': ipo_date,
                    'delisting_date': delisting_date,
                    'status': row['status']
                }
            )


    def fetch_symbols_info(self):
        full_symbols = pd.read_csv(self.config.FOLDER_Symbols / "FullSymbols.csv")
        full_symbols["symbol"] = full_symbols["symbol"].astype(str)
        symbols = full_symbols["symbol"].tolist()
        # symbols = ["BC","BC/PA"]
        symbols_str = " ".join(symbols)
        tickers = yf.Tickers(symbols_str)

        error_path = self.path_exist(self.config.FILE_Infos_Errors)
        if error_path.exists():
            with open(error_path.resolve(), "w"):
                pass
        for symbol in tqdm(symbols, desc="Fetching symbol info"):
            try:
                # get ticker object
                ticker = tickers.tickers[symbol]
                # get info & quote type
                ticker_info = ticker.info
                if "quoteType" in ticker_info:
                    quote_type = ticker_info["quoteType"]
                else:
                    quote_type = "unknown"
                # Save the treading to a csv file
                self._.json_Data("infos", f"{quote_type}", f"{symbol}.json").save(ticker_info)
            except Exception as e:
                with open(error_path.resolve(), "a") as error_file:
                    error_file.write(f"{symbol}\n")
                print(f"Error: fetch {symbol} info - got Error:{e}")

    def showing_symbol_info_single(self, symbol: str):
        ticker = yf.Ticker(symbol.upper())

        # get all stock info
        print(f"info: {ticker.info}")

        # get historical market data
        hist = ticker.history(period="1mo")

        # show meta-information about the treading (requires treading() to be called first)
        print(f"meta data: {ticker.history_metadata}")

        # show actions (dividends, splits, capital gains)
        print(f"actions: {ticker.actions}")
        print(f"dividends: {ticker.dividends}")
        print(f"splits: {ticker.splits}")
        print(f"capital gains: {ticker.capital_gains}")  # only for mutual funds & etfs

        # show share count
        df = ticker.get_shares_full(start="2022-01-01", end=None)
        print(df)
