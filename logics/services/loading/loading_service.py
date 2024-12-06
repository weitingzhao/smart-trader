from pathlib import Path
from logics import Engine
from .symbol_service import SymbolService
from .trading_service import TradingService
from .screening_service import ScreeningService

class LoadingService:
    def __init__(self, engine: Engine):
        self.engine = engine

    def symbol(self) -> SymbolService:
        return SymbolService(self.engine)

    def trading(self, path: Path) -> TradingService:
        return TradingService(self.engine, path)

    def screening(self) -> ScreeningService:
        return ScreeningService(self.engine)