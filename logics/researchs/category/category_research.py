from logics.service import Service
from .volume import Volume

class CategoryResearch:
    def __init__(self, service: Service):
        self.service = service

    def volume(self) -> Volume:
        return Volume(self.service)

