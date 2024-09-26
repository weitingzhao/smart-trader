from logics.engine import Engine
import logics.services as service
from logics.services.base_service import BaseService


class Service(BaseService):

    def __init__(self, engine: Engine):
        super().__init__(engine)

    # pull data from external data vendor
    def fetching(self) -> service.FetchingService:
        return service.FetchingService(self.engine)

    # load data from local storage
    def loading(self) -> service.LoadingService:
        return service.LoadingService(self.engine)

    # save data to local storage
    def saving(self) -> service.SavingService:
        return service.SavingService(self.engine)
