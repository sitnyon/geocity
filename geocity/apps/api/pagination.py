from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from geocity.apps.api.serializers import get_available_filters_for_agenda_as_json


class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "numberReturned": self.page.paginator.count,
                "numberMatched": len(data),
                **data,
            }
        )


class AgendaResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        domains = self.request.GET.get("domain")
        domains = domains.split(",") if domains else None
        agenda_filters = get_available_filters_for_agenda_as_json(domains)
        return Response(
            {
                "type": "FeatureCollection",
                "crs": {
                    "type": "name",
                    "properties": {"name": "urn:ogc:def:crs:EPSG::2056"},
                },
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "count": self.page.paginator.count,
                "features": data,
                "filters": agenda_filters,
            }
        )
