from rest_framework.viewsets import ModelViewSet
from .swagger import PaginatedSwaggerMixin


class BaseViewSet(PaginatedSwaggerMixin, ModelViewSet):
    pass
