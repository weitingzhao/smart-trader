from argparse import ArgumentParser
from logics.service import Service
from logics import researchs as analyse
from logics.researchs import BaseResearch
from logics.researchs.treading.patterns import pattern

class Research(BaseResearch):
    def __init__(self, service: Service):
        super().__init__(service)

    # analyses data
    def treading(self, args: ArgumentParser) -> analyse.TradingResearch:
        return analyse.TradingResearch(self.service, args)

    def symbols(self) -> analyse.SymbolResearch:
        return analyse.SymbolResearch(self.service)

    def pattern_list(self) -> list:
        return pattern.get_pattern_list()

    def pattern_dict(self) -> dict:
        return pattern.get_pattern_dict()
