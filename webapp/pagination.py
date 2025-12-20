from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination, CursorPagination

class mypagination(PageNumberPagination):
    page_size = 15  # Number of items to be displayed on each page
    page_query_param = 'page'  # Query parameter for the page number
    page_size_query_param = 'num'  # Allow client to set the page size using 'size' query parameter
    max_page_size = 15  # Maximum limit for page size to prevent excessive data load
    last_page_strings = ('last', ) # Allow client to request the last page using 'last' as page number

class mypagination2(CursorPagination):
    ordering = '-id'  # Default ordering field for cursor pagination
    page_size = 10  # Number of items to be displayed on each page