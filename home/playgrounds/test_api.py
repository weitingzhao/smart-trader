from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from apps.common.models import MarketStockHistoricalBarsByDay

# Initialize Alpaca API client
API_KEY = "PK1QV6ECTTX0TOWJ74N4"
SECRET_KEY = "YXJvuuYW3AMklnmERTOOUFfV5WIccrlfGCpqfE36"
client = StockHistoricalDataClient(api_key=API_KEY, secret_key=SECRET_KEY)

def pull_and_save_symbol_history(symbol, start_date, end_date):
    # Create request parameters
    request_params = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Day,
        start=start_date,
        end=end_date
    )

    # Fetch historical data
    bars = client.get_stock_bars(request_params)

    # Iterate over the bars and save to the database
    for bar in bars[symbol]:
        MarketStockHistoricalBarsByDay.objects.create(
            symbol=symbol,
            time=bar.timestamp,
            open=bar.open,
            high=bar.high,
            low=bar.low,
            close=bar.close,
            volume=bar.volume,
            # trade_count=bar.trade_count,
            # volume_weighted_average_price=bar.vwap
        )

# Example usage
