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
from datetime import datetime

import json, logging

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.middleware.csrf import get_token
from django.template.loader import get_template
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import generics, permissions

from api.auth import (
    get_login_uri,
    get_logout_uri,
    grecaptcha_verify,
    grecaptcha_site_key,
)
from api.models import TicketResponse, User, PreparedPdf
from api.pdf import render as render_pdf
from api.send_email import send_email
from api.utils import generate_pdf

from datetime import date,datetime # For working with dates

LOGGER = logging.getLogger(__name__)

class AcceptTermsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        request.user.accepted_terms_at = datetime.now()
        request.user.save()
        return Response({"ok": True})


class UserStatusView(APIView):
    def get(self, request: Request):
        logged_in = isinstance(request.user, User)
        info = {
            "accepted_terms_at": logged_in and request.user.accepted_terms_at or None,
            "user_id": logged_in and request.user.authorization_id or None,
            "email": logged_in and request.user.email or None,
            "first_name": logged_in and request.user.first_name or None,
            "last_name": logged_in and request.user.last_name or None,
            "login_uri": get_login_uri(request),
            "logout_uri": get_logout_uri(request),
            "surveys": [],
        }
        if logged_in and request.auth == "demo":
            info["demo_user"] = True
        ret = Response(info)
        uid = request.META.get("HTTP_X_DEMO_LOGIN")
        if uid and logged_in:
            # remember demo user
            ret.set_cookie("x-demo-login", uid)
        elif request.COOKIES.get("x-demo-login") and not logged_in:
            # logout
            ret.delete_cookie("x-demo-login")
        ret.set_cookie("csrftoken", get_token(request))
        return ret


class SurveyPdfView(generics.GenericAPIView):
    # FIXME - restore authentication?
    permission_classes = ()  # permissions.IsAuthenticated,)

    def post(self, request: Request, name=None):
        tpl_name = "survey-{}.html".format(name)
        # return HttpResponseBadRequest('Unknown survey name')

        responses = json.loads(request.POST["data"])
        # responses = {'question1': 'test value'}

        template = get_template(tpl_name)
        html_content = template.render(responses)

        if name == "primary":
            instruct_template = get_template("instructions-primary.html")
            instruct_html = instruct_template.render(responses)
            docs = (instruct_html,) + (html_content,) * 4
            pdf_content = render_pdf(*docs)

        else:
            pdf_content = render_pdf(html_content)

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="report.pdf"'

        response.write(pdf_content)

        return response


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
        data = json.loads(request.body)
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

        # Add date to the payload
        today = date.today().strftime('%d-%b-%Y')
        data['date'] = today

        #######################
        # Notice To Disputant - Response
        #
        # Make the Violation Ticket Number all upper case
        try:
            x = data['ticketNumber']['prefix']
            data['ticketNumber']['prefix'] = x.upper()
        except KeyError:
            pass

        # Format the date to be more user friendly
        try:
            x = datetime.strptime(data['ticketDate'],'%Y-%m-%d')
            data['ticketDate'] = x.strftime('%d-%b-%Y')
        except KeyError:
            pass

        # Format the date of birth to be more user friendly
        try:
            x2 = datetime.strptime(data['disputantDOB'],'%Y-%m-%d')
            data['disputantDOB'] = x2.strftime('%d-%b-%Y')
        except KeyError:
            pass
        #######################

        template = get_template(template)
        html_content = template.render(data)

        pdf_content = render_pdf(html_content)

        #######################
        # XXX: Just for testing
        # response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        # response.write(pdf_content)
        # return response
        #######################


        #############################################################


        result = request.data
        result1 =result.get("somevalue")
        disputant = result.get("disputantName", {})
        # address = result.get("disputantAddress", {})
        ticketNumber = result.get("ticketNumber", {})
        ticketNumber = str(ticketNumber.get("prefix")) + str(ticketNumber.get("suffix"))

        response = TicketResponse(
            first_name=disputant.get("first"),
            middle_name=disputant.get("middle"),
            last_name=disputant.get("last"),
            email=result.get("disputantEmail"),
            result=result,
            ticket_number=ticketNumber.upper(),
            ticket_date=result.get("ticketDate"),
            hearing_location_id=result.get("hearingLocation"),
            hearing_attendance=result.get("hearingAttendance"),
            dispute_type=result.get("disputeType")
        )

        check_required = [
            "first_name",
            "last_name",
            "email",
            "ticket_number",
            "ticket_date",
            "hearing_location_id",
            "dispute_type",
        ]

        for fname in check_required:
            if not getattr(response, fname):
                return HttpResponseBadRequest('Missing: ' + fname)
        # FIXME add required fields here
        # check terms acceptance
        # if not result.get("disputantAcknowledgement"):
        #     return HttpResponseBadRequest()

        #Generate/Save the pdf to DB and generate email with pdf attached
        email_status= False
        try:
            if result:
                # pdf_content = generate_pdf(result)
                pdf_response = PreparedPdf(
                    data = pdf_content
                )
                pdf_response.save()
                response.prepared_pdf_id = pdf_response.pk; 
                response.printed_date = timezone.now()
                email = result.get("disputantEmail")
                if email and pdf_content:
                    send_email(email, pdf_content)
                    response.emailed_date = timezone.now()
                    email_status= True
        except Exception as exception:
            LOGGER.exception("Pdf / Email generation error", exception)
            response.save()
            return Response({"id": response.pk,"pdf-id":pdf_response.pk,"email-sent":email_status})

        
        response.save()
      # {
        #     "disputantName": {"first": "first", "middle": "middle", "last": "last"},
        #     "disputantAddress": {
        #         "street": "addr",
        #         "city": "",
        #         "state": "BC",
        #         "country": "CAN",
        #         "postcode": "",
        #     },
        #     "disputantPhoneNumber": "phone",
        #     "disputantPhoneType": ["item2"],
        #     "disputantEmail": "email",
        #     "ticketNumber": "ticket",
        #     "ticketDate": "2018-04-04",
        #     "hearingLocation": "item2",
        #     "disputeType": "allegation",
        #     "hearingAttendance": "remotely",
        #     "hearingAttendancePhone": "n",
        #     "hearingAttendanceVideo": "y",
        #     "french": "n",
        #     "interpreter": "n",
        #     "witnesses": "n",
        #     "disputantAcknowledgement": ["item1"],
        # }

        return Response({"id": response.pk,"pdf-id":pdf_response.pk, "email-sent":email_status})