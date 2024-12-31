from ..service import Service
from ..services.base_service import BaseService


class BaseResearch(BaseService):

    def __init__(self, service: Service):
        super().__init__(service.engine)
        self.service = service
