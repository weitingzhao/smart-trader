from ..research import Research
from ..researchs.base_research import BaseResearch


class BaseChart(BaseResearch):

    def __init__(self, analyse: Research):
        super().__init__(analyse.service)
        self._analyse = analyse
