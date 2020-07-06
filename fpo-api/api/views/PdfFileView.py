from io import BytesIO
from datetime import datetime

from django.conf import settings
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    FileResponse,
)
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser
)
from django.http import HttpResponse, HttpResponseBadRequest, FileResponse
from api.utils import merge_pdf
from api.models import TicketResponse, PreparedPdf
import enum


class AdminMode(enum.Enum):
    NewResponse = 0
    Archive = 1


class PdfFileView(APIView):
    permission_classes = [IsAuthenticated | IsAdminUser]

    # This route is used for viewing PDF files from the admin page.
    def get(self, request: Request, id=None):
        if id is None:
            return HttpResponseBadRequest()
        try:
            pdf_result = PreparedPdf.objects.get(id=id)
        except PreparedPdf.DoesNotExist:
            return HttpResponseNotFound()

        filename = "ticketResponse.pdf"
        pdf_data = settings.ENCRYPTOR.decrypt(pdf_result.key_id, pdf_result.data)
        return FileResponse(BytesIO(pdf_data), as_attachment=False, filename=filename)

    # This route is used for printing by the staff on the admin page
    # it can handle multiple files.
    def post(self, request: Request):
        ids = request.data.get("id")
        mode = AdminMode(request.data.get("mode"))
        is_new_response_mode = mode == AdminMode.NewResponse
        if len(ids) > 50:
            return HttpResponseBadRequest(
                "Cannot print more than 50 PDFs.", content_type="text/plain"
            )

        ticket_queryset = TicketResponse.objects.filter(prepared_pdf_id__in=ids)
        archived_count = ticket_queryset.filter(archived_by_id__isnull=False).count()
        if is_new_response_mode and archived_count > 0:
            return HttpResponseBadRequest(
                "PDFs selected for print have already been archived.",
                content_type="text/plain",
            )

        pdf_queryset = PreparedPdf.objects.filter(id__in=ids)
        merged_pdf = merge_pdf(pdf_queryset)
        merged_pdf.seek(0)

        ticket_queryset.update(printed_by=request.user.id)
        ticket_queryset.update(printed_date=datetime.now())
        return HttpResponse(
            merged_pdf.getvalue(), content_type="application/octet-stream"
        )
