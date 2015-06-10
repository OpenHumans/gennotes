from rest_framework.pagination import PageNumberPagination


class PageNumberPaginationUpTo1000(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 1000
