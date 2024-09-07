import yfinance as yf
from typing import List
from logic import Engine
from apps.common.models import *
from datetime import datetime, timezone
from logic.logic import TaskBuilder
from logic.services import BaseService


class CompanyInfoYahoo(BaseService, TaskBuilder):

    def __init__(self, engine: Engine):
        super().__init__(engine)

    #Simluate for test use only
    def _get_init_load_test(self)->List:
        return ["ABEO", "AAPL", "MSFT"]

    def _get_init_load(self) -> List:
        # Query the MarketSymbol model to get a list of symbols
        return list(MarketSymbol.objects.values_list('symbol', flat=True))


    def _before_fetching(self, records: List) -> any:
        return yf.Tickers(" ".join(records))

    def _fetching_detail(self, record: str, tools : any):
        # <editor-fold desc="save method">

        def infinity(value):
            if value == 'Infinity':
                return None  # or float('inf') if your database supports it
            return value

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
                    'full_time_employees': infinity(ticker_info.get('fullTimeEmployees', 0)),
                    'currency': ticker_info.get('currency', ''),
                    'financial_currency': ticker_info.get('financialCurrency', ''),
                    'exchange': ticker_info.get('exchange', ''),
                    'quote_type': ticker_info.get('quoteType', ''),
                    'time_zone_full_name': ticker_info.get('timeZoneFullName', ''),
                    'time_zone_short_name': ticker_info.get('timeZoneShortName', ''),
                    'gmt_offset_milliseconds': infinity(ticker_info.get('gmtOffSetMilliseconds', 0)),
                    'uuid': ticker_info.get('uuid', '')
                }
            )

        def save_stock_risk_metrics(symbol, ticker_info):
            MarketStockRiskMetrics.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'audit_risk': infinity(ticker_info.get('auditRisk', 0)),
                    'board_risk': infinity(ticker_info.get('boardRisk', 0)),
                    'compensation_risk': infinity(ticker_info.get('compensationRisk', 0)),
                    'share_holder_rights_risk': infinity(ticker_info.get('shareHolderRightsRisk', 0)),
                    'overall_risk': infinity(ticker_info.get('overallRisk', 0)),
                    'governance_epoch_date': datetime.fromtimestamp(ticker_info.get('governanceEpochDate', 0), tz=timezone.utc),
                    'compensation_as_of_epoch_date': datetime.fromtimestamp(ticker_info.get('compensationAsOfEpochDate', 0), tz=timezone.utc),
                    'first_trade_date_epoch_utc': datetime.fromtimestamp(ticker_info.get('firstTradeDateEpochUtc', 0), tz=timezone.utc),
                    'max_age': infinity(ticker_info.get('maxAge', 0))
                }
            )

        def save_stock_dividends(symbol, ticker_info):
            MarketStockDividend.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'dividend_rate': infinity(ticker_info.get('dividendRate', 0)),
                    'dividend_yield': infinity(ticker_info.get('dividendYield', 0)),
                    'ex_dividend_date': datetime.fromtimestamp(ticker_info.get('exDividendDate', 0), tz=timezone.utc),
                    'payout_ratio': infinity(ticker_info.get('payoutRatio', 0)),
                    'five_year_avg_dividend_yield': infinity(ticker_info.get('fiveYearAvgDividendYield', 0)),
                    'trailing_annual_dividend_rate': infinity(ticker_info.get('trailingAnnualDividendRate', 0)),
                    'trailing_annual_dividend_yield': infinity(ticker_info.get('trailingAnnualDividendYield', 0))
                }
            )

        def save_stock_price(symbol, ticker_info):
            MarketStockPrice.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'price_hint': infinity(ticker_info.get('priceHint', 0)),
                    'previous_close': infinity(ticker_info.get('previousClose', 0)),
                    'open_price': infinity(ticker_info.get('open', 0)),
                    'day_low': infinity(ticker_info.get('dayLow', 0)),
                    'day_high': infinity(ticker_info.get('dayHigh', 0)),
                    'regular_market_previous_close': infinity(ticker_info.get('regularMarketPreviousClose', 0)),
                    'regular_market_open': infinity(ticker_info.get('regularMarketOpen', 0)),
                    'regular_market_day_low': infinity(ticker_info.get('regularMarketDayLow', 0)),
                    'regular_market_day_high': infinity(ticker_info.get('regularMarketDayHigh', 0)),
                    'current_price': infinity(ticker_info.get('currentPrice', 0)),
                    'bid': infinity(ticker_info.get('bid', 0)),
                    'ask': infinity(ticker_info.get('ask', 0)),
                    'bid_size': infinity(ticker_info.get('bidSize', 0)),
                    'ask_size': infinity(ticker_info.get('askSize', 0)),
                    'volume': infinity(ticker_info.get('volume', 0)),
                    'regular_market_volume': infinity(ticker_info.get('regularMarketVolume', 0)),
                    'average_volume': infinity(ticker_info.get('averageVolume', 0)),
                    'average_volume_10days': infinity(ticker_info.get('averageVolume10days', 0)),
                    'average_daily_volume_10day': infinity(ticker_info.get('averageDailyVolume10Day', 0)),
                }
            )

        def save_stock_valuation(symbol, ticker_info):
            MarketStockValuation.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'market_cap': infinity(ticker_info.get('marketCap', 0)),
                    'beta': infinity(ticker_info.get('beta', 0)),
                    'trailing_pe': infinity(ticker_info.get('trailingPE', 0)),
                    'forward_pe': infinity(ticker_info.get('forwardPE', 0)),
                    'price_to_sales_trailing_12_months': infinity(ticker_info.get('priceToSalesTrailing12Months', 0)),
                    'price_to_book': infinity(ticker_info.get('priceToBook', 0)),
                    'book_value': infinity(ticker_info.get('bookValue', 0)),
                    'peg_ratio': infinity(ticker_info.get('pegRatio', 0)),
                    'trailing_peg_ratio': infinity(ticker_info.get('trailingPegRatio', 0)),
                    'enterprise_value': infinity(ticker_info.get('enterpriseValue', 0)),
                    'enterprise_to_revenue': infinity(ticker_info.get('enterpriseToRevenue', 0)),
                    'enterprise_to_ebitda': infinity(ticker_info.get('enterpriseToEbitda', 0)),
                    'trailing_eps': infinity(ticker_info.get('trailingEps', 0)),
                    'forward_eps': infinity(ticker_info.get('forwardEps', 0)),
                }
            )

        def save_stock_target(symbol, ticker_info):
            MarketStockTarget.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'target_high_price': infinity(ticker_info.get('targetHighPrice', 0)),
                    'target_low_price': infinity(ticker_info.get('targetLowPrice', 0)),
                    'target_mean_price': infinity(ticker_info.get('targetMeanPrice', 0)),
                    'target_median_price': infinity(ticker_info.get('targetMedianPrice', 0)),
                    'recommendation_mean': infinity(ticker_info.get('recommendationMean', 0)),
                    'recommendation_key': ticker_info.get('recommendationKey', ''),
                    'number_of_analyst_opinions': infinity(ticker_info.get('numberOfAnalystOpinions', 0))
                }
            )

        def save_stock_performance(symbol, ticker_info):
            MarketStockPerformance.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'fifty_two_week_low': infinity(ticker_info.get('fiftyTwoWeekLow', 0)),
                    'fifty_two_week_high': infinity(ticker_info.get('fiftyTwoWeekHigh', 0)),
                    'fifty_day_average': infinity(ticker_info.get('fiftyDayAverage', 0)),
                    'two_hundred_day_average': infinity(ticker_info.get('twoHundredDayAverage', 0)),
                    'earnings_quarterly_growth': infinity(ticker_info.get('earningsQuarterlyGrowth', 0)),
                    'earnings_growth': infinity(ticker_info.get('earningsGrowth', 0)),
                    'revenue_growth': infinity(ticker_info.get('revenueGrowth', 0)),
                    'gross_margins': infinity(ticker_info.get('grossMargins', 0)),
                    'ebitda_margins': infinity(ticker_info.get('ebitdaMargins', 0)),
                    'operating_margins': infinity(ticker_info.get('operatingMargins', 0)),
                    'return_on_assets': infinity(ticker_info.get('returnOnAssets', 0)),
                    'return_on_equity': infinity(ticker_info.get('returnOnEquity', 0)),
                    'profit_margins': infinity(ticker_info.get('profitMargins', 0))
                }
            )

        def save_stock_share(symbol, ticker_info):
            MarketStockShare.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'float_shares': infinity(ticker_info.get('floatShares', 0)),
                    'shares_outstanding': infinity(ticker_info.get('sharesOutstanding', 0)),
                    'shares_short': infinity(ticker_info.get('sharesShort', 0)),
                    'shares_short_prior_month': infinity(ticker_info.get('sharesShortPriorMonth', 0)),
                    'shares_short_previous_month_date': datetime.fromtimestamp(ticker_info.get('sharesShortPreviousMonthDate', 0), tz=timezone.utc),
                    'date_short_interest': datetime.fromtimestamp(ticker_info.get('dateShortInterest', 0), tz=timezone.utc),
                    'shares_percent_shares_out': infinity(ticker_info.get('sharesPercentSharesOut', 0)),
                    'held_percent_insiders': infinity(ticker_info.get('heldPercentInsiders', 0)),
                    'held_percent_institutions': infinity(ticker_info.get('heldPercentInstitutions', 0)),
                    'short_ratio': infinity(ticker_info.get('shortRatio', 0)),
                    'short_percent_of_float': infinity(ticker_info.get('shortPercentOfFloat', 0))
                }
            )

        def save_stock_financial(symbol, ticker_info):
            MarketStockFinancial.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'total_cash': infinity(ticker_info.get('totalCash', 0)),
                    'total_cash_per_share': infinity(ticker_info.get('totalCashPerShare', 0)),
                    'ebitda': infinity(ticker_info.get('ebitda', 0)),
                    'total_debt': infinity(ticker_info.get('totalDebt', 0)),
                    'quick_ratio': infinity(ticker_info.get('quickRatio', 0)),
                    'current_ratio': infinity(ticker_info.get('currentRatio', 0)),
                    'total_revenue': infinity(ticker_info.get('totalRevenue', 0)),
                    'debt_to_equity': infinity(ticker_info.get('debtToEquity', 0)),
                    'revenue_per_share': infinity(ticker_info.get('revenuePerShare', 0)),
                    'net_income_to_common': infinity(ticker_info.get('netIncomeToCommon', 0)),
                    'free_cashflow': infinity(ticker_info.get('freeCashflow', 0)),
                    'operating_cashflow': infinity(ticker_info.get('operatingCashflow', 0)),
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
                        'max_age': infinity(officer.get('maxAge', 0)),
                        'name': officer.get('name', ''),
                        'age': infinity(officer.get('age', 0)),
                        'title': officer.get('title', ''),
                        'year_born': infinity(officer.get('yearBorn', 0)),
                        'fiscal_year': infinity(officer.get('fiscalYear', 0)),
                        'total_pay': infinity(officer.get('totalPay', 0)),
                        'exercised_value': infinity(officer.get('exercisedValue', 0)),
                        'unexercised_value': infinity(officer.get('unexercisedValue', 0))
                    }
                )
        # </editor-fold>

        ### Save the data to the database ####
        ticker = tools.tickers[record]
        root_ticker_info = ticker.info
        symbol_obj = MarketSymbol.objects.get(symbol=record)

        symbol = root_ticker_info.get('symbol', None)

        if symbol is None:
            symbol_obj.has_company_info = False
            symbol_obj.save()
            self.logger.info(f"Symbol {record} has no useful company info. pass. info : {root_ticker_info}")
            return

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
