from collections import OrderedDict
from apps.common.models import Strategy
from business.researchs.base_research import BaseResearch
from business.service import Service


class StrategyResearch(BaseResearch):
    def __init__(self, service: Service):
        super().__init__(service)

    def get_simple_dic(self, need_uncategorized: bool = True) -> dict:
        # Query all records from the Strategy model
        trade_strategy = OrderedDict()
        if need_uncategorized:
            trade_strategy[0] = "Uncategorized"
        trade_strategy.update({
            strategy['strategy_id']: strategy['name']
            for strategy in Strategy
            .objects.values('strategy_id', 'name')
            .order_by('custom_order')
        })
        return trade_strategy