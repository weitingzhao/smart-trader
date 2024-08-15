from logic.research import Research
from logic.researchs import BaseResearch


class BaseChart(BaseResearch):

    def __init__(self, analyse: Research):
        super().__init__(analyse.service)
        self._analyse = analyse
