import json
import pandas as pd
from typing import List
from logics.service import Service
from .position_base import PositionBase
from logics.researchs.base_research import BaseResearch


class ClosePosition(PositionBase):

    def __init__(self, service: Service):
        super().__init__(service)