from datetime import datetime, timezone
import pandas as pd
import yfinance as yf
from tqdm import tqdm

from apps.tasks.templatetags.formats import log_to_text
from logic.engine import Engine
from logic.services.base_service import BaseService
from home.models import *
from alpha_vantage.fundamentaldata import FundamentalData

from logic.utilities.tools import TqdmLogger


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

    def fetching_symbols_info(self) -> list:
        # symbols = MarketSymbol.objects.values_list('symbol', flat=True)
        # symbols = ["AAPL","UI"]
        symbols = ["TSLA"]
        tickers = yf.Tickers(" ".join(symbols))

        # <editor-fold desc="save method">
        def save_stock(symbol, ticker_info):
            MarketStock.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'underlying_symbol': ticker_info.get('underlyingSymbol', ''),
                    'short_name': ticker_info.get('shortName', ''),
                    'long_name': ticker_info.get('longName', ''),
                    'address1': ticker_info.get('address1', ''),
                    'city': ticker_info.get('city', ''),
                    'state': ticker_info.get('state', ''),
                    'zip': ticker_info.get('zip', ''),
                    'country': ticker_info.get('country', ''),
                    'phone': ticker_info.get('phone', ''),
                    'website': ticker_info.get('website', ''),
                    'industry': ticker_info.get('industry', ''),
                    'sector': ticker_info.get('sector', ''),
                    'long_business_summary': ticker_info.get('longBusinessSummary', ''),
                    'full_time_employees': ticker_info.get('fullTimeEmployees', 0),
                    'currency': ticker_info.get('currency', ''),
                    'financial_currency': ticker_info.get('financialCurrency', ''),
                    'exchange': ticker_info.get('exchange', ''),
                    'quote_type': ticker_info.get('quoteType', ''),
                    'time_zone_full_name': ticker_info.get('timeZoneFullName', ''),
                    'time_zone_short_name': ticker_info.get('timeZoneShortName', ''),
                    'gmt_offset_milliseconds': ticker_info.get('gmtOffSetMilliseconds', 0),
                    'uuid': ticker_info.get('uuid', '')
                }
            )

        def save_stock_risk_metrics(symbol, ticker_info):
            MarketStockRiskMetrics.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'audit_risk': ticker_info.get('auditRisk', 0),
                    'board_risk': ticker_info.get('boardRisk', 0),
                    'compensation_risk': ticker_info.get('compensationRisk', 0),
                    'share_holder_rights_risk': ticker_info.get('shareHolderRightsRisk', 0),
                    'overall_risk': ticker_info.get('overallRisk', 0),
                    'governance_epoch_date': datetime.fromtimestamp(ticker_info.get('governanceEpochDate', 0), tz=timezone.utc),
                    'compensation_as_of_epoch_date': datetime.fromtimestamp(ticker_info.get('compensationAsOfEpochDate', 0), tz=timezone.utc),
                    'first_trade_date_epoch_utc': datetime.fromtimestamp(ticker_info.get('firstTradeDateEpochUtc', 0), tz=timezone.utc),
                    'max_age': ticker_info.get('maxAge', 0)
                }
            )

        def save_stock_dividends(symbol, ticker_info):
            MarketStockDividend.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'dividend_rate': ticker_info.get('dividendRate', 0),
                    'dividend_yield': ticker_info.get('dividendYield', 0),
                    'ex_dividend_date': datetime.fromtimestamp(ticker_info.get('exDividendDate', 0), tz=timezone.utc),
                    'payout_ratio': ticker_info.get('payoutRatio', 0),
                    'five_year_avg_dividend_yield': ticker_info.get('fiveYearAvgDividendYield', 0),
                    'trailing_annual_dividend_rate': ticker_info.get('trailingAnnualDividendRate', 0),
                    'trailing_annual_dividend_yield': ticker_info.get('trailingAnnualDividendYield', 0)
                }
            )

        def save_stock_price(symbol, ticker_info):
            MarketStockPrice.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'price_hint': ticker_info.get('priceHint', 0),
                    'previous_close': ticker_info.get('previousClose', 0),
                    'open_price': ticker_info.get('open', 0),
                    'day_low': ticker_info.get('dayLow', 0),
                    'day_high': ticker_info.get('dayHigh', 0),
                    'regular_market_previous_close': ticker_info.get('regularMarketPreviousClose', 0),
                    'regular_market_open': ticker_info.get('regularMarketOpen', 0),
                    'regular_market_day_low': ticker_info.get('regularMarketDayLow', 0),
                    'regular_market_day_high': ticker_info.get('regularMarketDayHigh', 0),
                    'current_price': ticker_info.get('currentPrice', 0),
                    'bid': ticker_info.get('bid', 0),
                    'ask': ticker_info.get('ask', 0),
                    'bid_size': ticker_info.get('bidSize', 0),
                    'ask_size': ticker_info.get('askSize', 0),
                    'volume': ticker_info.get('volume', 0),
                    'regular_market_volume': ticker_info.get('regularMarketVolume', 0),
                    'average_volume': ticker_info.get('averageVolume', 0),
                    'average_volume_10days': ticker_info.get('averageVolume10days', 0),
                    'average_daily_volume_10day': ticker_info.get('averageDailyVolume10Day', 0),
                }
            )

        def save_stock_valuation(symbol, ticker_info):
            MarketStockValuation.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'market_cap': ticker_info.get('marketCap', 0),
                    'beta': ticker_info.get('beta', 0),
                    'trailing_pe': ticker_info.get('trailingPE', 0),
                    'forward_pe': ticker_info.get('forwardPE', 0),
                    'price_to_sales_trailing_12_months': ticker_info.get('priceToSalesTrailing12Months', 0),
                    'price_to_book': ticker_info.get('priceToBook', 0),
                    'book_value': ticker_info.get('bookValue', 0),
                    'peg_ratio': ticker_info.get('pegRatio', 0),
                    'trailing_peg_ratio': ticker_info.get('trailingPegRatio', 0),
                    'enterprise_value': ticker_info.get('enterpriseValue', 0),
                    'enterprise_to_revenue': ticker_info.get('enterpriseToRevenue', 0),
                    'enterprise_to_ebitda': ticker_info.get('enterpriseToEbitda', 0),
                    'trailing_eps': ticker_info.get('trailingEps', 0),
                    'forward_eps': ticker_info.get('forwardEps', 0),
                }
            )

        def save_stock_target(symbol, ticker_info):
            MarketStockTarget.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'target_high_price': ticker_info.get('targetHighPrice', 0),
                    'target_low_price': ticker_info.get('targetLowPrice', 0),
                    'target_mean_price': ticker_info.get('targetMeanPrice', 0),
                    'target_median_price': ticker_info.get('targetMedianPrice', 0),
                    'recommendation_mean': ticker_info.get('recommendationMean', 0),
                    'recommendation_key': ticker_info.get('recommendationKey', ''),
                    'number_of_analyst_opinions': ticker_info.get('numberOfAnalystOpinions', 0)
                }
            )

        def save_stock_performance(symbol, ticker_info):
            MarketStockPerformance.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'fifty_two_week_low': ticker_info.get('fiftyTwoWeekLow', 0),
                    'fifty_two_week_high': ticker_info.get('fiftyTwoWeekHigh', 0),
                    'fifty_day_average': ticker_info.get('fiftyDayAverage', 0),
                    'two_hundred_day_average': ticker_info.get('twoHundredDayAverage', 0),
                    'earnings_quarterly_growth': ticker_info.get('earningsQuarterlyGrowth', 0),
                    'earnings_growth': ticker_info.get('earningsGrowth', 0),
                    'revenue_growth': ticker_info.get('revenueGrowth', 0),
                    'gross_margins': ticker_info.get('grossMargins', 0),
                    'ebitda_margins': ticker_info.get('ebitdaMargins', 0),
                    'operating_margins': ticker_info.get('operatingMargins', 0),
                    'return_on_assets': ticker_info.get('returnOnAssets', 0),
                    'return_on_equity': ticker_info.get('returnOnEquity', 0),
                    'profit_margins': ticker_info.get('profitMargins', 0)
                }
            )

        def save_stock_share(symbol, ticker_info):
            MarketStockShare.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'float_shares': ticker_info.get('floatShares', 0),
                    'shares_outstanding': ticker_info.get('sharesOutstanding', 0),
                    'shares_short': ticker_info.get('sharesShort', 0),
                    'shares_short_prior_month': ticker_info.get('sharesShortPriorMonth', 0),
                    'shares_short_previous_month_date': datetime.fromtimestamp(ticker_info.get('sharesShortPreviousMonthDate', 0), tz=timezone.utc),
                    'date_short_interest': datetime.fromtimestamp(ticker_info.get('dateShortInterest', 0), tz=timezone.utc),
                    'shares_percent_shares_out': ticker_info.get('sharesPercentSharesOut', 0),
                    'held_percent_insiders': ticker_info.get('heldPercentInsiders', 0),
                    'held_percent_institutions': ticker_info.get('heldPercentInstitutions', 0),
                    'short_ratio': ticker_info.get('shortRatio', 0),
                    'short_percent_of_float': ticker_info.get('shortPercentOfFloat', 0)
                }
            )

        def save_stock_financial(symbol, ticker_info):
            MarketStockFinancial.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'total_cash': ticker_info.get('totalCash', 0),
                    'total_cash_per_share': ticker_info.get('totalCashPerShare', 0),
                    'ebitda': ticker_info.get('ebitda', 0),
                    'total_debt': ticker_info.get('totalDebt', 0),
                    'quick_ratio': ticker_info.get('quickRatio', 0),
                    'current_ratio': ticker_info.get('currentRatio', 0),
                    'total_revenue': ticker_info.get('totalRevenue', 0),
                    'debt_to_equity': ticker_info.get('debtToEquity', 0),
                    'revenue_per_share': ticker_info.get('revenuePerShare', 0),
                    'net_income_to_common': ticker_info.get('netIncomeToCommon', 0),
                    'free_cashflow': ticker_info.get('freeCashflow', 0),
                    'operating_cashflow': ticker_info.get('operatingCashflow', 0),
                    'last_fiscal_year_end': datetime.fromtimestamp(ticker_info.get('lastFiscalYearEnd', 0), tz=timezone.utc),
                    'next_fiscal_year_end': datetime.fromtimestamp(ticker_info.get('nextFiscalYearEnd', 0), tz=timezone.utc),
                    'most_recent_quarter': datetime.fromtimestamp(ticker_info.get('mostRecentQuarter', 0), tz=timezone.utc),
                    'last_split_factor': ticker_info.get('lastSplitFactor', ''),
                    'last_split_date': datetime.fromtimestamp(ticker_info.get('lastSplitDate', 0), tz=timezone.utc)
                }
            )

        def save_company_officers(symbol, officers_info):
            for officer in officers_info:
                MarketCompanyOfficer.objects.update_or_create(
                    symbol= symbol,
                    name=officer.get('name', ''),
                    defaults={
                        'max_age': officer.get('maxAge', 0),
                        'name': officer.get('name', ''),
                        'age': officer.get('age', 0),
                        'title': officer.get('title', ''),
                        'year_born': officer.get('yearBorn', 0),
                        'fiscal_year': officer.get('fiscalYear', 0),
                        'total_pay': officer.get('totalPay', 0),
                        'exercised_value': officer.get('exercisedValue', 0),
                        'unexercised_value': officer.get('unexercisedValue', 0)
                    }
                )
        # </editor-fold>

        result = []
        for root_symbol in TqdmLogger(symbols, desc="Fetching symbol info", logger=self.logger):
            try:
                ticker = tickers.tickers[root_symbol]
                root_ticker_info = ticker.info
                symbol_obj = MarketSymbol.objects.get(symbol=root_symbol)

                # Stock basic info
                save_stock(symbol_obj, root_ticker_info)
                # Stock risk metrics
                save_stock_risk_metrics(symbol_obj, root_ticker_info)
                # Stock dividends
                save_stock_dividends(symbol_obj, root_ticker_info)
                # Stock price
                save_stock_price(symbol_obj, root_ticker_info)
                # Stock valuation
                save_stock_valuation(symbol_obj, root_ticker_info)
                # Stock target
                save_stock_target(symbol_obj, root_ticker_info)
                # Stock performance
                save_stock_performance(symbol_obj, root_ticker_info)
                # Stock share
                save_stock_share(symbol_obj, root_ticker_info)
                # Stock financial
                save_stock_financial(symbol_obj, root_ticker_info)
                # Company officers
                save_company_officers(symbol_obj, root_ticker_info.get('companyOfficers', []))

                self.logger.info(f"Success: fetch {root_symbol} info")
            except Exception as e:
                self.logger.error(f"Error: fetch {root_symbol} info - got Error:{e}")
                result.append({'symbol': root_symbol, 'error': str(e)})
        return result


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
