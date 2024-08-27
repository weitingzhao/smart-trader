import pandas as pd
import yfinance as yf
from home.models import *
from logic.engine import Engine
from logic.services.base_service import BaseService
from alpha_vantage.fundamentaldata import FundamentalData



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
                    'status': row['status'],
                    'has_company_info': True
                }
            )

    def fetching_alphav_company_overview(self, symbol) -> tuple:
        fd = FundamentalData(key=self.API_KEY, output_format='pandas')
        data, _ = fd.get_company_overview(symbol)
        self.engine.csv(self.config.FOLDER_Infos / "company_overview.csv").save_df(data)
        return data

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
