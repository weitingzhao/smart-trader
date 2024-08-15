from pathlib import Path
from logic import Engine
from .loading_symbol_service import LoadingSymbolService
from .loading_trading_service import LoadingTradingService

class LoadingService:
    def __init__(self, engine: Engine):
        self.engine = engine

    def symbol(self) -> LoadingSymbolService:
        return LoadingSymbolService(self.engine)

    def trading(self, path: Path) -> LoadingTradingService:
        return LoadingTradingService(self.engine, path)
