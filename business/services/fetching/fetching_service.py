from business.engine import Engine
from business.services.fetching.company_info_yahoo import CompanyInfoYahoo
from business.services.fetching.symbol_service import SymbolService
from business.services.fetching.screening_service import ScreeningService
from business.services.fetching.stock_hist_bars_yahoo import StockHistBarsYahoo


class FetchingService:
    def __init__(self, engine: Engine):
        self.engine = engine

    def screening(self) -> ScreeningService:
        return ScreeningService(self.engine)

    def symbol(self) -> SymbolService:
        return SymbolService(self.engine)

    def company_info_yahoo(self) -> CompanyInfoYahoo:
        return CompanyInfoYahoo(self.engine)

    def stock_hist_bars_yahoo(self) -> StockHistBarsYahoo:
        return StockHistBarsYahoo(self.engine)






