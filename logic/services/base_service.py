from logic.engine import Engine
from logic.engines.base_engine import BaseEngine


class BaseService(BaseEngine):
    def __init__(self, engine: Engine):
        super().__init__(engine.config)
        self._engine = engine

