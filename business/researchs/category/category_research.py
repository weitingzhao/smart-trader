from ...service import Service
from .volume import Volume
from .strategy import StrategyResearch

class CategoryResearch:
    def __init__(self, service: Service):
        self.service = service

    def volume(self) -> Volume:
        return Volume(self.service)

    def strategy(self) -> StrategyResearch:
        return StrategyResearch(self.service)

