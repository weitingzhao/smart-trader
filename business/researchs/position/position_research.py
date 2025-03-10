from ...service import Service
from ..base_research import BaseResearch
from .close_position import ClosePosition
from .open_position import OpenPosition
from .portfolio import Portfolio

class PositionResearch(BaseResearch):

    def __init__(self, service: Service):
        super().__init__(service)

    def Open(self) -> OpenPosition:
        return OpenPosition(self.service)

    def Close(self) -> ClosePosition:
        return ClosePosition(self.service)

    def Portfolio(self) -> Portfolio:
        return Portfolio(self.service)

