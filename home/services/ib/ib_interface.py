from ibapi.client import EClient
from ibapi.wrapper import EWrapper


class IBWrapper(EWrapper):
    def __init__(self):
        self.data = {}
        self.order_status = {}

class IBClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)

class IBApi(IBWrapper, IBClient):
    def __init__(self):
        IBWrapper.__init__(self)
        IBClient.__init__(self, wrapper=self)



