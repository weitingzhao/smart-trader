from logic import Engine
from .fetching_symbol_service import FetchingSymbolService
from .fetching_trading_service import FetchingTradingService


class FetchingService:
    def __init__(self, engine: Engine):
        self.engine = engine
    def history(self) -> FetchingTradingService:
        return FetchingTradingService(self.engine)

    def symbol(self) -> FetchingSymbolService:
        return FetchingSymbolService(self.engine)