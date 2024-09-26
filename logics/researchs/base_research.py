from logics.service import Service
from logics.services import BaseService


class BaseResearch(BaseService):

    def __init__(self, service: Service):
        super().__init__(service.engine)
        self.service = service
