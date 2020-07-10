import json
import logging

from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.template.loader import get_template
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.auth import (
    grecaptcha_verify,
    grecaptcha_site_key,
)

from api.models import TicketResponse, PreparedPdf
from api.pdf import render as render_pdf
from api.pdf import transform_data_for_pdf as transform
from api.send_email import send_email
from api.utils import generate_pdf

LOGGER = logging.getLogger(__name__)

class SubmitTicketResponseView(APIView):
    def get(self, request: Request, name=None):
        key = grecaptcha_site_key()
        return Response({"key": key})

    def post(self, request: Request, name=None):
        check_captcha = grecaptcha_verify(request)
        if not check_captcha["status"]:
            return HttpResponseForbidden(text=check_captcha["message"])

        #############################################################
        #  Adding different pdf form logic: Jul 3, 2020
        data = request.data
        name = request.query_params.get('name')

        template = '{}.html'.format(name)

        # These are the current allowed forms (whitelist)
        possibleTemplates = [
            'notice-to-disputant-response',
            'violation-ticket-statement-and-written-reasons'
        ]

        # If not one of our two forms... reject.
        if not name in possibleTemplates:
            return HttpResponseBadRequest('No valid form specified')

        transformed_data = transform(data)

        template = get_template(template)
        html_content = template.render(transformed_data)

        #######################
        # XXX: Just for testing. Send the pdf directly to the browser.
        # response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        # response.write(pdf_content)
        # return response
        #######################

        #############################################################

        disputant = data.get("disputantName", {})
        # address = data.get("disputantAddress", {})
        ticketNumber = data.get("ticketNumber", {})
        ticketNumber = str(ticketNumber.get("prefix")) + str(ticketNumber.get("suffix"))

        result_bin = json.dumps(data).encode("ascii")
        (key_id, result_enc) = settings.ENCRYPTOR.encrypt(result_bin)

        response = TicketResponse(
            first_name=disputant.get("first"),
            middle_name=disputant.get("middle"),
            last_name=disputant.get("last"),
            result=result_enc,
            key_id=key_id,
            ticket_number=ticketNumber.upper(),
            ticket_date=data.get("ticketDate"),
            hearing_location_id=data.get("hearingLocation"),
            hearing_attendance=data.get("hearingAttendance"),
            dispute_type=data.get("disputeType"),
        )

        check_required = [
            "first_name",
            "last_name",
            "ticket_number",
            "ticket_date",
            "hearing_location_id"
            ]

        for fname in check_required:
            if not getattr(response, fname):
                return HttpResponseBadRequest("Missing: " + fname)

        # check terms acceptance?
        # if not data.get("disputantAcknowledgement"):
        #     return HttpResponseBadRequest()

        # Generate/Save the pdf to DB and generate email with pdf attached
        email_sent = False
        pdf_response = None

        try:
            if data:

                pdf_content = render_pdf(html_content) # Create the PDF

                pdf_response = PreparedPdf(
                    data = pdf_content
                )
                pdf_response.save()
                response.prepared_pdf_id = pdf_response.pk; 
                response.printed_date = timezone.now()

                if pdf_content:
                    (pdf_key_id, pdf_content_enc) = settings.ENCRYPTOR.encrypt(
                        pdf_content
                    )
                    pdf_response = PreparedPdf(data=pdf_content_enc, key_id=pdf_key_id)
                    pdf_response.save()
                    response.prepared_pdf_id = pdf_response.pk
                    response.save()
                    request.session['file_guid'] = str(response.file_guid)

                email = data.get("disputantEmail")
                if email and pdf_content:
                    send_email(email, pdf_content)
                    response.emailed_date = timezone.now()
                    email_sent = True
                    response.save()

        except Exception as exception:
            LOGGER.exception("Pdf / Email generation error", exception)

        return Response(
            {
                "id": response.pk,
                "email-sent": email_sent,
            }
        )
