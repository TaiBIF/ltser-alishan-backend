from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

page_param = openapi.Parameter(
    name="page",
    in_=openapi.IN_QUERY,
    description="Page number (1-based)",
    type=openapi.TYPE_INTEGER,
    default=1,
    minimum=1,
)

page_size_param = openapi.Parameter(
    name="page_size",
    in_=openapi.IN_QUERY,
    description="Items per page (max 1000)",
    type=openapi.TYPE_INTEGER,
)


class PaginatedSwaggerMixin:
    @swagger_auto_schema(manual_parameters=[page_param, page_size_param])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
