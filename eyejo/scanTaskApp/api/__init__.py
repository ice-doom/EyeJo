from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class ViewSup:
    class ViewPagination(PageNumberPagination):
        # page_size = 2
        page_size_query_param = 'limit'
        page_query_param = 'page'

        # max_page_size = 5

        def get_paginated_response(self, data):
            return Response({
                'code': 0,
                'msg': 'success',
                'total': self.page.paginator.count,
                'data': data,
                # 'links': {
                #     'next': self.get_next_link(),
                #     'previous': self.get_previous_link()
                # }
            })


