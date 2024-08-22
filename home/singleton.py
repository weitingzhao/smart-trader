from pathlib import Path
from whoosh.index import open_dir
import  core.configures_home as core

class Instance:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Instance, cls).__new__(cls)

            # Initialize the index
            index_market_symbol = Path(core.Config().folder_schema_index / "market_symbol_index")
            cls._instance.market_symbol_index = open_dir(index_market_symbol)
        return cls._instance

    def get_index_market_symbol(self):
        return self._instance.market_symbol_index