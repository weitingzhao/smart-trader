import logging, re
import yfinance as yf
from typing import List
from apps.common.models import *
from logics.logic import TaskWorker
from logics.services import BaseService


class StockHistBarsYahoo(BaseService, TaskWorker):
    def __init__(self, engine):
        super().__init__(engine)
        # Step 2.2 define custom handler for logger to handle yfinance error
        class FetchingExceptionHandler(logging.Handler):
            def emit(self, record):
                try:
                    # Check if the log record is an error and contains the specified message
                    if record.levelname == 'ERROR':
                        if (    'No data found, symbol may be delisted' in record.msg or
                                'possibly delisted; No price data found' in record.msg
                        ):
                            # Extract the symbol from the message
                            symbol = record.msg.split(':')[0].replace('$', '')
                            # Update the MarketSymbol model to set is_delisted to True
                            MarketSymbol.objects.filter(symbol=symbol).update(is_delisted=True)
                            print(f"Mark symbol {symbol} as delisted, and will not fetch data next time")

                        if ( 'is invalid, must be one of' in record.msg):
                            # Regular expression to find the array
                            # Regular expression to find the symbol, period, and the first element of the array
                            match = re.search(r"([\w-]+): Period '(\d+\w)' is invalid, must be one of \['(\w+)'", record.msg)
                            if match:
                                symbol = match.group(1)
                                period = match.group(2)
                                first_element = match.group(3)

                                if period == "5d":
                                    MarketSymbol.objects.filter(symbol=symbol).update(daily_period_yfinance=first_element)
                                    print(f"Mark symbol {symbol} daily fetch period change to {first_element}. and use it fetch data next time")
                                else:
                                    MarketSymbol.objects.filter(symbol=symbol).update(min_period_yfinance=first_element)
                                    print(f"Mark symbol {symbol} min fetch period change to {first_element}. and use it fetch data next time")

                except Exception as e:
                    print(f"Error in yfinance Fetching Exception Handler: {e}")

        # Get configure logger
        logger = logging.getLogger('yfinance')

        # Add the custom handler to the logger
        if not any(handler.name == "yfinance: Fetching HistBars Exception [Error]" for handler in logger.handlers):
            # Add the custom handler to the logger
            db_handler = FetchingExceptionHandler()
            db_handler.setLevel(logging.INFO)
            db_handler.name = "yfinance: Fetching HistBars Exception [Error]"
            logger.addHandler(db_handler)

    def _use_day_table(self, interval: str) -> bool:
        return interval == "1d" or interval == "1wk" or interval == "1mo" or interval == "3mo"

    #Simluate for test use only
    def _get_init_load_test(self)->List:
        self.symbol_data = None
        return ["DMYY-U","DMYY-U"]
        # return ["BKSB", "BKWO", "BLACR"]
        # return ["IVCBW"]
        # ["BWCAU"]
        # return ["BKSB","BKWO","BLACR"]
        # return ["ABEO", "AAPL", "MSFT"]


    def _get_init_load(self) -> List:
        interval = self.args.get("interval", "1m")
        if self._use_day_table(interval):
            table_name = "day"
        else:
            table_name = "min"

        # return symbol by type
        is_append = bool(self.args.get("append",False))
        if is_append:
            query = f"SELECT symbol,daily_period_yfinance, min_period_yfinance FROM market_symbol WHERE is_delisted=FALSE"
        else:
            query = f"""
                    SELECT symbol,daily_period_yfinance, min_period_yfinance FROM market_symbol WHERE symbol NOT IN (
                        SELECT symbol FROM ( SELECT symbol
                            FROM market_stock_hist_bars_{table_name}_ts
                            GROUP BY symbol ORDER BY COUNT(*) ASC
                        ) AS subquery)
            """

        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

        # Convert the result to a list of symbols
        if self._use_day_table(interval):
            self.symbol_data = {row[0]: {"interval": row[1]} for row in rows}
        else:
            self.symbol_data = {row[0]: {"interval": row[2]} for row in rows}

        return [row[0] for row in rows]


    def _before_fetching(self, records: List) -> any:
        return yf.Tickers(" ".join(records))

    def _fetching_detail(self, record: str, tools: any):
        # Simulate real workload
        # time.sleep(1)

        # Step 1. prepare parameters
        #method for append
        is_append = self.args.get("append",False)
        delta= int(self.args.get("delta", 1))
        # “1d”, “5d”, “1mo”, “3mo”, “6mo”, “1y”, “2y”, “5y”, “10y”, “ytd”, “max”
        period = self.args.get("period", "max") #"1d"
        # “1m”, “2m”, “5m”, “15m”, “30m”, “60m”, “90m”, “1h”, “1d”, “5d”, “1wk”, “1mo”, “3mo”
        if self.symbol_data is None:
            interval = self.args.get("interval", "1m")
        else:
            interval = self.symbol_data[record]["interval"]

        #If not using period – in the format (yyyy-mm-dd) or datetime.
        start = self.args.get("start", None)
        end = self.args.get("end", None)
        # the stocker tools
        ticker = tools.tickers[record]

        # Step 2. define save function
        def save_to_timeseries_db(history):
            # Get parameters from the args
            def save_hist_bars_ts(model):
                def append():
                    records.append(model(
                        symbol=record,
                        time=date,
                        open=row.get('Open', 0),
                        high=row.get('High', 0),
                        low=row.get('Low', 0),
                        close=row.get('Close', 0),
                        volume=row.get('Volume', 0),
                        dividend=row.get('Dividends', 0),
                        stock_splits=row.get('Stock Splits', 0)
                    ))

                if len(history) <= 0:
                    # Update MarketSymbol to set is_delisted_on_day or is_delisted_on_min to True
                    # if self._use_day_table(interval):
                    #     MarketSymbol.objects.filter(symbol=record).update(is_delisted_on_day=True)
                    # else:
                    #     MarketSymbol.objects.filter(symbol=record).update(is_delisted_on_min=True)
                    return

                records = []
                min_date_in_history = history.index.min()
                date = min_date_in_history
                if is_append:
                    # step 1. get existing records from db and all times for those records
                    existing_records_dates = sorted(model.objects.filter(
                        symbol=record,
                        time__gte=min_date_in_history
                    ).values_list('time', flat=True))

                    # step 2. remove last record, since this last_record value may not refact the final price
                    max_dates = existing_records_dates[-delta:] if existing_records_dates else []
                    for max_date in max_dates:
                        # Delete the corresponding record from the model
                        model.objects.filter(symbol=record, time__exact=max_date).delete()
                        # Remove the date from existing_records_dates
                        existing_records_dates.remove(max_date)

                    # step 3. append new records from history api, append to db
                    for date, row in history.iterrows():
                        if date in existing_records_dates:
                            continue
                        append()
                else:
                    for date, row in history.iterrows():
                        append()
                if len(records) > 0:
                    model.objects.bulk_create(records, batch_size=1000)
                    self.logger.info(
                        f"saved {len(records)} {record} "
                        f"from {min_date_in_history} to {date}")

            if self._use_day_table(interval):
                save_hist_bars_ts(MarketStockHistoricalBarsByDay)
                # self.engine.csv("daily", f"{record}.csv").save_df(history)
            else:
                save_hist_bars_ts(MarketStockHistoricalBarsByMin)
                # self.engine.csv("min", f"{period}.csv").save_df(history)

        # Step 3. Saving.
        try:
            if start:
                history = ticker.history(start=start, end=end, interval=interval)
                save_to_timeseries_db(history)
            else:
                history = ticker.history(period=period, interval=interval)
                # If the history is empty and is appended mode,try to get the history with the max period for lucky
                if is_append and len(history) <= 0:
                    history = ticker.history(period='max', interval=interval)
                save_to_timeseries_db(history)
        except Exception as e:
            print(f"Error fetching data got error: {e}")
            # Optionally, you could return a custom value or re-raise the exception
            return None

    def Clean_non_daily_record_in_day_ts(self):
        with connection.cursor() as cursor:
            cursor.execute(f"""
            DELETE FROM market_stock_hist_bars_day_ts
            WHERE symbol IN (
            SELECT DISTINCT symbol
            FROM market_stock_hist_bars_day_ts
            WHERE time::time != '05:00:00' AND time::time != '04:00:00'
            LIMIT 100)""")

