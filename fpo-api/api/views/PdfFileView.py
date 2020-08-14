from io import BytesIO
from datetime import datetime, timedelta

from django.conf import settings
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    HttpResponseForbidden,
    FileResponse,
)
from rest_framework.request import Request
from rest_framework.views import APIView
from api.auth import IsActiveAndAdminUser
from api.utils import merge_pdf
from api.auth import method_permission_classes
from api.models import TicketResponse, PreparedPdf
import enum


class AdminMode(enum.Enum):
    NewResponse = 0
    Archive = 1


class PdfFileView(APIView):
    permission_classes = []

    def _timestamp_older_than_one_hour(self, target_date):
        return datetime.utcnow() - timedelta(hours=1) > target_date.replace(tzinfo=None)

    """ This route is used for viewing PDF files. """

    def get(self, request: Request, id=None):

        target_id = id
        # Prevent regular users from looking up by id.
        if not request.user.is_staff and target_id is not None:
            return HttpResponseForbidden()

        try:
            if not request.user.is_staff or target_id is None:
                file_guid = request.session.get("file_guid")
                ticket_response = TicketResponse.objects.get(file_guid=file_guid)
                target_id = ticket_response.prepared_pdf_id
                if self._timestamp_older_than_one_hour(ticket_response.created_date):
                    print('oldtimestamp')
                    return HttpResponseNotFound(
                        "This link has expired.", content_type="text/plain"
                    )

            pdf_result = PreparedPdf.objects.get(id=target_id)
        except (PreparedPdf.DoesNotExist, TicketResponse.DoesNotExist):
            return HttpResponseNotFound()
            
        filename = ticket_response.pdf_filename
        pdf_data = settings.ENCRYPTOR.decrypt(pdf_result.key_id, pdf_result.data)
        return FileResponse(BytesIO(pdf_data), as_attachment=False, filename=filename)

    """ This route is used for printing by the staff on the admin page
        it can handle multiple files. """

    @method_permission_classes((IsActiveAndAdminUser,))
    def post(self, request: Request):
        ids = request.data.get("id")
        if len(ids) > 50:
            return HttpResponseBadRequest(
                "Cannot print more than 50 PDFs.", content_type="text/plain"
            )

        mode = AdminMode(request.data.get("mode"))
        is_new_response_mode = mode == AdminMode.NewResponse
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
