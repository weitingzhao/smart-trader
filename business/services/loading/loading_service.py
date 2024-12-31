from pathlib import Path
from business.engine import Engine
from business.services.loading.symbol_service import SymbolService
from business.services.loading.trading_service import TradingService
from business.services.loading.screening_service import ScreeningService

class LoadingService:
    def __init__(self, engine: Engine):
        self.engine = engine

    def symbol(self) -> SymbolService:
        return SymbolService(self.engine)

    def trading(self, path: Path) -> TradingService:
        return TradingService(self.engine, path)

    def screening(self) -> ScreeningService:
        return ScreeningService(self.engine)