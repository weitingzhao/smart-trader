from django.db.models import Q

from apps.common.models import *
from ...engine import Engine
from ..base_service import BaseService
from whoosh.qparser import MultifieldParser, WildcardPlugin, OrGroup
from home.singleton import Instance

class SymbolService(BaseService):

    def __init__(self, engine: Engine):
        super().__init__(engine)

    def match_symbol(self, query, limit:int=10):
        if not query:
            return []

        if len(query) == 1:
            # Search the MarketSymbol model
            results = MarketSymbol.objects.filter(
                Q(symbol__icontains=query) | Q(name__icontains=query)
            )[:limit]  # Limit to top 10 matches

            matches = [{
                'symbol': result.symbol,
                'name': result.name,
                'market': result.market
            } for result in results]
            return matches

        else:
            index = Instance().get_index_market_symbol()
            # Prepare the query
            parser = MultifieldParser(
                fieldnames=["symbol", "name"],
                schema=index.schema,
                group=OrGroup
            )
            parser.add_plugin(WildcardPlugin())
            # Build the query string to handle exact match and wildcard
            query_string = f"(symbol:{query}^2.0) OR (symbol:{query}*^2.0) OR (name:{query}) OR (name:{query}*)"

            # Parse the query
            whoosh_query = parser.parse(query_string)

            # Search the index by query
            with (index.searcher() as searcher):
                results = searcher.search(whoosh_query, limit=limit)
                matches = [{
                    'symbol': result['symbol'],
                    'name': result['name'],
                    'market': result['market']
                } for result in results]
                return matches