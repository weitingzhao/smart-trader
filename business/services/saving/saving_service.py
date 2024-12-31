from pathlib import Path
from typing import Optional, Literal

from business.engine import Engine
from business.services.loading.loader import AbstractLoader
from business.services.saving.saving_plot_service import SavingPlotService
from business.services.saving.saving_symbol_service import  SavingSymbolService


class SavingService:
    def __init__(self, engine: Engine):
        self.engine = engine

    def plot_trading(
            self,
            data,
            loader: AbstractLoader,
            save_folder: Optional[Path] = None,
            mode: Literal["default", "expand"] = "default",
    ) -> SavingPlotService:
        return SavingPlotService(self.engine, data, loader, save_folder,mode)


    def symbol(self) -> SavingSymbolService:
        return SavingSymbolService(self.engine)