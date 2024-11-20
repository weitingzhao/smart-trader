from logics.service import Service
from logics.researchs.base_research import BaseResearch
from .close_position import ClosePosition
from .open_position import OpenPosition


class PositionResearch(BaseResearch):

    def __init__(self, service: Service):
        super().__init__(service)

    def Open(self) -> OpenPosition:
        return OpenPosition(self.service)

    def Close(self) -> ClosePosition:
        return ClosePosition(self.service)


