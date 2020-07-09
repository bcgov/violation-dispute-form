"""
    REST API Documentation for Family Protection Order

    OpenAPI spec version: v1


    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
# import copy
# import json
# import logging

# from django.conf import settings
# from django.http import HttpResponseBadRequest, HttpResponseForbidden
# from django.template.loader import get_template
# from django.utils import timezone

# from rest_framework.views import APIView
# from rest_framework.request import Request
# from rest_framework.response import Response

# from api.auth import (
#     grecaptcha_verify,
#     grecaptcha_site_key,
# )
# from api.models import TicketResponse, PreparedPdf
# from api.pdf import render as render_pdf
# from api.send_email import send_email
# from api.utils import generate_pdf

# from datetime import date, datetime  # For working with dates

# LOGGER = logging.getLogger(__name__)


# class SubmitTicketResponseView(APIView):
#     def get(self, request: Request, name=None):
#         key = grecaptcha_site_key()
#         return Response({"key": key})

#     def post(self, request: Request, name=None):
#         check_captcha = grecaptcha_verify(request)
#         if not check_captcha["status"]:
#             return HttpResponseForbidden(text=check_captcha["message"])

#         #############################################################
#         #  Adding different pdf form logic: Jul 3, 2020
#         data = json.loads(request.body)
#         name = request.query_params.get('name')

#         # data = copy.deepcopy(request.data)
#         # name = request.GET['name']
#         template = '{}.html'.format(name)

#         # These are the current allowed forms (whitelist)
#         possibleTemplates = [
#             'notice-to-disputant-response',
#             'violation-ticket-statement-and-written-reasons'
#         ]

#         # If not one of our two forms... reject.
#         if not name in possibleTemplates:
#             return HttpResponseBadRequest('No valid form specified')

#         # Add date to the payload
#         today = date.today().strftime('%d-%b-%Y')
#         data['date'] = today

#         #######################
#         # Notice To Disputant - Response
#         #
#         # Make the Violation Ticket Number all upper case
#         try:
#             x = data['ticketNumber']['prefix']
#             data['ticketNumber']['prefix'] = x.upper()
#         except KeyError:
#             pass

#         # Format the date to be more user friendly
#         try:
#             x = datetime.strptime(data['ticketDate'], '%Y-%m-%d')
#             data['ticketDate'] = x.strftime('%d-%b-%Y')
#         except KeyError:
#             pass

#         # Format the date of birth to be more user friendly
#         try:
#             x2 = datetime.strptime(data['disputantDOB'], '%Y-%m-%d')
#             data['disputantDOB'] = x2.strftime('%d-%b-%Y')
#         except KeyError:
#             pass
#         #######################

#         template = get_template(template)
#         html_content = template.render(data)

#         #######################
#         # XXX: Just for testing
#         # response = HttpResponse(content_type='application/pdf')
#         # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
#         # response.write(pdf_content)
#         # return response
#         #######################


#         #############################################################

#         result = request.data
#         disputant = result.get("disputantName", {})
#         # address = result.get("disputantAddress", {})
#         ticketNumber = result.get("ticketNumber", {})
#         ticketNumber = str(ticketNumber.get("prefix")) + str(ticketNumber.get("suffix"))

#         result_bin = json.dumps(result).encode("ascii")
#         (key_id, result_enc) = settings.ENCRYPTOR.encrypt(result_bin)

#         response = TicketResponse(
#             first_name=disputant.get("first"),
#             middle_name=disputant.get("middle"),
#             last_name=disputant.get("last"),
#             result=result_enc,
#             key_id=key_id,
#             ticket_number=ticketNumber.upper(),
#             ticket_date=result.get("ticketDate"),
#             hearing_location_id=result.get("hearingLocation"),
#             hearing_attendance=result.get("hearingAttendance"),
#             dispute_type=result.get("disputeType"),
#         )

#         check_required = [
#             "first_name",
#             "last_name",
#             "ticket_number",
#             "ticket_date",
#             "hearing_location_id"
#             ]

#         for fname in check_required:
#             if not getattr(response, fname):
#                 return HttpResponseBadRequest("Missing: " + fname)

#         # check terms acceptance?
#         # if not result.get("disputantAcknowledgement"):
#         #     return HttpResponseBadRequest()

#         # Generate/Save the pdf to DB and generate email with pdf attached
#         email_sent = False
#         pdf_response = None

#         try:
#             if result:

#                 pdf_content = render_pdf(html_content)

#                 pdf_response = PreparedPdf(
#                     data = pdf_content
#                 )
#                 pdf_response.save()
#                 response.prepared_pdf_id = pdf_response.pk; 
#                 response.printed_date = timezone.now()

#                 if pdf_content:
#                     (pdf_key_id, pdf_content_enc) = settings.ENCRYPTOR.encrypt(
#                         pdf_content
#                     )
#                     pdf_response = PreparedPdf(data=pdf_content_enc, key_id=pdf_key_id)
#                     pdf_response.save()
#                     response.prepared_pdf_id = pdf_response.pk
#                     response.save()
#                     request.session['file_guid'] = str(response.file_guid)

#                 email = result.get("disputantEmail")
#                 if email and pdf_content:
#                     send_email(email, pdf_content)
#                     response.emailed_date = timezone.now()
#                     email_sent = True
#                     response.save()

#         except Exception as exception:
#             LOGGER.exception("Pdf / Email generation error", exception)

#         return Response(
#             {
#                 "id": response.pk,
#                 "email-sent": email_sent,
#             }
#         )
