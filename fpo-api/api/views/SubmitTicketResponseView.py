import json
import logging
import base64

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


LOGGER = logging.getLogger(__name__)


class SubmitTicketResponseView(APIView):
    def get(self, request: Request, name=None):
        key = grecaptcha_site_key()
        return Response({"key": key})

    def post(self, request: Request, name=None):
        check_captcha = grecaptcha_verify(request)
        if not check_captcha["status"]:
            return HttpResponseForbidden(
                content_type="text/plain",
                content=check_captcha["message"])

        request.session["file_guid"] = None
        #############################################################
        #  Adding different pdf form logic: Jul 3, 2020
        data = request.data
        name = request.query_params.get("name")

        #Set pdf filename
        if name == "violation-ticket-statement-and-written-reasons":
            filename = "Reasons-to-Reduce-Traffic-Ticket.pdf"
        elif name == "notice-to-disputant-response":
            filename = "Traffic-Hearing-Choice.pdf"
        else:
            filename = "Ticket-Response.pdf"

        template = "{}.html".format(name)

        # These are the current allowed forms (whitelist)
        possibleTemplates = [
            "notice-to-disputant-response",
            "violation-ticket-statement-and-written-reasons",
        ]

        # If not one of our two forms... reject.
        if name not in possibleTemplates:
            return HttpResponseBadRequest("No valid form specified")

        transformed_data = transform(data)

        template = get_template(template)
        html_content = template.render(transformed_data)
        #############################################################

        disputant = data.get("disputantName", {})
        email = data.get("disputantEmail")

        result_bin = json.dumps(data).encode("ascii")
        (key_id, result_enc) = settings.ENCRYPTOR.encrypt(result_bin)

        response = TicketResponse(
            first_name=disputant.get("first"),
            middle_name=disputant.get("middle"),
            last_name=disputant.get("last"),
            result=result_enc,
            key_id=key_id,
            ticket_number=data.get("ticketNumber"),
            ticket_date=data.get("ticketDate"),
            hearing_location_id=data.get("hearingLocation"),
            hearing_attendance=data.get("hearingAttendance"),
            dispute_type=data.get("disputeType"),
            pdf_filename=filename
        )

        check_required = [
            "first_name",
            "last_name",
            "ticket_number",
            "ticket_date",
            "hearing_location_id",
        ]

        for fname in check_required:
            if not getattr(response, fname):
                return HttpResponseBadRequest("Missing: " + fname)

        # Generate/Save the pdf to DB and generate email with pdf attached
        email_sent = False
        pdf_response = None

        try:
            pdf_content = render_pdf(html_content)

            pdf_response = PreparedPdf(data=pdf_content)
            pdf_response.save()
            response.prepared_pdf_id = pdf_response.pk
            response.printed_date = timezone.now()

            if pdf_content:
                (pdf_key_id, pdf_content_enc) = settings.ENCRYPTOR.encrypt(pdf_content)
                pdf_response = PreparedPdf(data=pdf_content_enc, key_id=pdf_key_id)
                pdf_response.save()
                response.prepared_pdf_id = pdf_response.pk
                response.save()
                request.session["file_guid"] = str(response.file_guid)

            if email and pdf_content:
                email_res = self.prepared_email(email, pdf_content, filename)
                if email_res:
                    email_msg_id = email_res['messages'][0]['msgId']
                    response.emailed_date = timezone.now()
                    response.email_message_id = email_msg_id
                    email_sent = True
                    response.save()

        except Exception as exception:
            LOGGER.exception("Pdf / Email generation error", exception)

        return Response({"id": response.pk, "email-sent": email_sent})

    def prepared_email(self, email, pdf_content, filename):
        encoded_string = base64.b64encode(pdf_content).decode('ascii')
        body = """\
                <html>
                <body>
                <p>Hi,<br></p>
                <b>Thank-you for choosing how you wish to attend your traffic hearing.<b>
                <p>A copy of your completed form is attached for your records.</p>
                <p>Your preference will be reviewed, and a Notice of Hearing will be sent in the mail telling you of the date and time of your hearing. The notice will also tell you whether you will be attending your hearing in-person, by telephone or by video and will provide you with important information about attending your hearing.</p>
                <p>If you want to learn more about the hearing process, please visit the Provincial Court of British Columbia's website and read their <a href ="https://www.provincialcourt.bc.ca/downloads/Traffic/Traffic Court Guide.pdf">Guide to Disputing a Ticket</a>.
                If you have any questions, please contact the Violation Ticket Centre at: 1-877-661-8026</p>
                </body>
                </html>
                """
        attachment = {
                        "content": encoded_string,             
                        "contentType": "application/pdf",
                        "encoding": "base64",
                        "filename": filename
                    }        
        subject = "Traffic Hearing Choice"
        bodyType = "html"
        email_res = send_email(body, bodyType, subject, email, attachment)
        return email_res
