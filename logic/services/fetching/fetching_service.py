from logic import Engine
from .company_info_yahoo import CompanyInfoYahoo
from .symbol_service import FetchingSymbolService
from .trading_service import FetchingTradingService
from .stock_hist_bars_yahoo import StockHistBarsYahoo


class FetchingService:
    def __init__(self, engine: Engine):
        self.engine = engine

    def company_info_yahoo(self) -> CompanyInfoYahoo:
        return CompanyInfoYahoo(self.engine)

    def stock_hist_bars_yahoo(self) -> StockHistBarsYahoo:
        return StockHistBarsYahoo(self.engine)

    def history(self) -> FetchingTradingService:
        return FetchingTradingService(self.engine)

    def symbol(self) -> FetchingSymbolService:
        return FetchingSymbolService(self.engine)





