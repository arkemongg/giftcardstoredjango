from rest_framework.pagination import PageNumberPagination,LimitOffsetPagination

class DefaultPagination(PageNumberPagination):
    page_size = 8

class DefaultLimitOffset(LimitOffsetPagination):
    default_limit = 8
    max_limit = 32