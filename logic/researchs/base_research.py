from logic.service import Service
from logic.services import BaseService


class BaseResearch(BaseService):

    def __init__(self, service: Service):
        super().__init__(service._engine)
        self.service = service
