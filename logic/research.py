from argparse import ArgumentParser
from logic.service import Service
from logic import researchs as analyse
from logic.researchs import BaseResearch
from logic.researchs.treading.patterns import pattern

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
