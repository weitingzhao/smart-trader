from alpaca.data import StockHistoricalDataClient, enums

from alpaca.data.historical import StockHistoricalDataClient, ScreenerClient
from alpaca.data.requests import StockLatestQuoteRequest, ScreenerRequest, MostActivesRequest, StockLatestBarRequest


API_KEY = "PK1QV6ECTTX0TOWJ74N4"
SECRET_KEY = "YXJvuuYW3AMklnmERTOOUFfV5WIccrlfGCpqfE36"

# keys required for stock historical data client
stock_client = StockHistoricalDataClient(api_key=API_KEY, secret_key= SECRET_KEY)
screener_client =  ScreenerClient(api_key=API_KEY, secret_key= SECRET_KEY)




# multi symbol request - single symbol is similar
# multi_request_params = StockLatestQuoteRequest(symbol_or_symbols=["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN"])
# latest_multi_symbol_quotes = stock_client.get_stock_latest_quote(multi_request_params)
# gld_latest_ask_price = latest_multi_symbol_quotes["GLD"]["ask_price"]
#
#
# most_actives_request = MostActivesRequest(top=20, by=enums.MostActivesBy.VOLUME.value)
# most_actives_request2 = MostActivesRequest(top=20, by=enums.MostActivesBy.TRADES.value)
# actives = screener_client.get_most_actives(most_actives_request)
# actives2 = screener_client.get_most_actives(most_actives_request2)

multi_request_params = StockLatestBarRequest(symbol_or_symbols=["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN"])

stock_client = stock_client.get_stock_latest_bar( request_params=multi_request_params)

b = ""
