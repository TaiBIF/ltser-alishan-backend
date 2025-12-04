from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # 預設值
    page_size_query_param = "page_size"  # 允許前端控制 page_size
    max_page_size = 100
