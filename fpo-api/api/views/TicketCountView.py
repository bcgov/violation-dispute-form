from django.db.models import Count, Q
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from api.models import TicketResponse, Region


class TicketCountView(APIView):
    """ Used for counts displayed on the bottom of the admin screen. """

    def get(self, request: Request):
        """ Used for counts displayed on the bottom of the admin screen. """
        return Response(
            {
                "new_count": {
                    "by_region": Region.objects.values("name", "id").annotate(
                        count=Count(
                            "region_location__location_ticket__id",
                            filter=Q(
                                region_location__location_ticket__printed_by__isnull=True   # noqa: E501
                            ),
                        )
                    ),
                    "total": TicketResponse.objects.filter(
                        printed_by__isnull=True
                    ).aggregate(count=Count("hearing_location__region")),
                },
                "archive_count": {
                    "by_region": Region.objects.values("name", "id").annotate(
                        count=Count(
                            "region_location__location_ticket__id",
                            filter=Q(
                                region_location__location_ticket__printed_by__isnull=False  # noqa: E501
                            ),
                        )
                    ),
                    "total": TicketResponse.objects.filter(
                        printed_by__isnull=False
                    ).aggregate(count=Count("hearing_location__region")),
                },
            }
        )
