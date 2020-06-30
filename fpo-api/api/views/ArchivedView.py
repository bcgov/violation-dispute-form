from datetime import datetime
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from api.models import TicketResponse


class ArchivedView(APIView):
    # This is used for marking the files as archived.
    # Double check that htese files aren't already archived?
    def post(self, request: Request):
        ticket_queryset = TicketResponse.objects.filter(
            prepared_pdf_id__in=request.data.get("id"))
        # Put user context in here. change this off of 1.
        ticket_queryset.update(archived_by=1)
        ticket_queryset.update(archived_date=datetime.now())
        return Response("success")
