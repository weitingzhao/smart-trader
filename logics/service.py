from logics import services
from logics.engine import Engine

class Service(services.BaseService):

    def __init__(self, engine: Engine):
        super().__init__(engine)

    # pull data from external data vendor
    def fetching(self) -> services.FetchingService:
        return services.FetchingService(self.engine)

    # load data from local storage
    def loading(self) -> services.LoadingService:
        return services.LoadingService(self.engine)

    # save data to local storage
    def saving(self) -> services.SavingService:
        return services.SavingService(self.engine)
