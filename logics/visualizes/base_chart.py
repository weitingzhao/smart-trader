from logics.research import Research
from logics.researchs import BaseResearch


class BaseChart(BaseResearch):

    def __init__(self, analyse: Research):
        super().__init__(analyse.service)
        self._analyse = analyse
