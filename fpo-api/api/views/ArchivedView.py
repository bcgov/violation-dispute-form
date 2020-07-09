from datetime import datetime
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from api.models import TicketResponse

from rest_framework.permissions import (
    IsAdminUser
)


class ArchivedView(APIView):
    permission_classes = [IsAdminUser]

    # This is used for marking the files as archived.
    def post(self, request: Request):
        ticket_queryset = TicketResponse.objects.filter(
            prepared_pdf_id__in=request.data.get("id"))

        ticket_queryset.update(archived_by=request.user.id)
        ticket_queryset.update(archived_date=datetime.now())
        return Response("success")
