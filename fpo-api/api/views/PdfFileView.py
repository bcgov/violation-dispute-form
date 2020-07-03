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

from api.utils import merge_pdf
from api.models import TicketResponse, PreparedPdf


class PdfFileView(APIView):
    # This route is used for viewing PDF files from survey page and the admin pages.
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
        # double check that these aren't already printed?
        if len(request.data.get("id")) > 50:
            return HttpResponseBadRequest()
        pdf_queryset = PreparedPdf.objects.filter(id__in=request.data.get("id"))
        merged_pdf = merge_pdf(pdf_queryset)
        merged_pdf.seek(0)
        ticket_queryset = TicketResponse.objects.filter(
            prepared_pdf_id__in=request.data.get("id")
        )
        # User Context - change this off of 1.
        ticket_queryset.update(printed_by=1)
        ticket_queryset.update(printed_date=datetime.now())
        return HttpResponse(
            merged_pdf.getvalue(), content_type="application/octet-stream"
        )
