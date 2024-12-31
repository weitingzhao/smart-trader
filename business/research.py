from argparse import ArgumentParser
from .service import Service
from . import researchs as research
from .researchs.treading.patterns import pattern
from .researchs.base_research import BaseResearch

class Research(BaseResearch):

    def __init__(self, service: Service):
        super().__init__(service)

    # analyses data
    def category(self)  -> research.CategoryResearch:
        return research.CategoryResearch(self.service)

    def treading(self, args: ArgumentParser = None) -> research.TradingResearch:
        return research.TradingResearch(self.service, args)

    def symbols(self) -> research.SymbolResearch:
        return research.SymbolResearch(self.service)

    def position(self) -> research.PositionResearch:
        return research.PositionResearch(self.service)

    # patterns
    def pattern_list(self) -> list:
        return pattern.get_pattern_list()

    def pattern_dict(self) -> dict:
        return pattern.get_pattern_dict()
