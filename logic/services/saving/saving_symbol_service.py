from pathlib import Path
from apps.common.models import *
from logic.engine import Engine
from logic.services.base_service import BaseService
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT


class SavingSymbolService(BaseService):

    def __init__(
            self,
            engine: Engine
    ):
        super().__init__(engine)


    def index_symbol(self):
        # Define the schema
        schema = Schema(
            symbol=TEXT(stored=True, field_boost=2.0),
            name=TEXT(stored=True),
            market=TEXT(stored=True)
        )

        # Create an index directory
        index_file = Path(self.config.folder_schema_index / "market_symbol_index")
        index_dir = self.config.path_exist(index_file)

        # Create the index
        ix = create_in(index_dir, schema)

        # Add documents to the index
        writer = ix.writer()
        for market_symbol in MarketSymbol.objects.all():
            writer.add_document(
                symbol=market_symbol.symbol,
                name=market_symbol.name,
                market=market_symbol.market
            )
        writer.commit(optimize=True)


