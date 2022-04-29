from django.core.paginator import EmptyPage
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        response = super(CustomPagination, self).get_paginated_response(data)
        try:
            next_page = self.page.next_page_number()
        except EmptyPage:
            next_page = None

        try:
            previous_page = self.page.previous_page_number()
        except EmptyPage:
            previous_page = None

        return Response({
            **response.data,
            'nextPageNumber': next_page,
            'previousPageNumber': previous_page
        })
