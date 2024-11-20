from argparse import ArgumentParser
from logics import researchs
from logics.service import Service
from logics.researchs.treading.patterns import pattern

class Research(researchs.BaseResearch):

    def __init__(self, service: Service):
        super().__init__(service)

    # analyses data
    def category(self)  -> researchs.CategoryResearch:
        return researchs.CategoryResearch(self.service)

    def treading(self, args: ArgumentParser = None) -> researchs.TradingResearch:
        return researchs.TradingResearch(self.service, args)

    def symbols(self) -> researchs.SymbolResearch:
        return researchs.SymbolResearch(self.service)

    def position(self) -> researchs.PositionResearch:
        return researchs.PositionResearch(self.service)

    # patterns
    def pattern_list(self) -> list:
        return pattern.get_pattern_list()

    def pattern_dict(self) -> dict:
        return pattern.get_pattern_dict()
