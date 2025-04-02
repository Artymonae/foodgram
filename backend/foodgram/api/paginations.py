from rest_framework import pagination

from recipes.constants import PAGE_SIZE


class Pagination(pagination.PageNumberPagination):
    """Пагинации."""

    page_size = PAGE_SIZE
    max_page_size = PAGE_SIZE
    page_size_query_param = "limit"
