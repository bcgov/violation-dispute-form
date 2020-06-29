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
from datetime import datetime, timezone, timedelta

import json, io, logging

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, FileResponse
from django.middleware.csrf import get_token
from django.template.loader import get_template
from django.utils import timezone
from django.db.models import Count, Case, IntegerField, When, F, Q

from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import filters as default_filters, generics, permissions

from api.auth import (
    get_login_uri,
    get_logout_uri,
    grecaptcha_verify,
    grecaptcha_site_key,
)
from api.models import TicketResponse, User, Location, Region, PreparedPdf
from api.pdf import render as render_pdf
from api.send_email import send_email
from api.utils import generate_pdf, merge_pdf
from api.serializers import TicketResponseSerializer, LocationSerializer, RegionSerializer, LocationLookupSerializer, RegionLookupSerializer

from django.core.files.base import File

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
            "hearing_attendance",
            "dispute_type",
        ]

        for fname in check_required:
            if not getattr(response, fname):
                return HttpResponseBadRequest()
        # FIXME add required fields here
        # check terms acceptance
        # if not result.get("disputantAcknowledgement"):
        #     return HttpResponseBadRequest()

        #Generate/Save the pdf to DB and generate email with pdf attached
        email_status= False
        try:
            if result:
                pdf_content = generate_pdf(result)
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


class TicketResponseListFilter(filters.FilterSet):
    is_archived = filters.BooleanFilter(field_name='archived_by', lookup_expr='isnull', exclude=True)
    region = filters.NumberFilter(field_name='hearing_location__region_id', lookup_expr='exact')
    created_date = filters.IsoDateTimeFilter(field_name='created_date__date', method='filter_date')
    archived_date = filters.IsoDateTimeFilter(field_name='archived_date__date', method='filter_date')

    #Combining filters here, if we have is_archived, we want to look in the archived_date or created_date fields. 
    #If it's not archived, only search the created_date field. 
    def filter_date(self, queryset, field_name, value):
        if not value:
            return queryset
        is_archived = self.data.get("is_archived")
        start = value
        end = value + timedelta(hours=24) - timedelta(seconds=1)
        if is_archived and field_name == "archived_date__date":
            return queryset.filter(created_date__range=(start, end)) | queryset.filter(archived_date__range=(start, end))
        elif not is_archived and field_name == "created_date__date":
            return queryset.filter(created_date__range=(start, end))
        else:
            return queryset

    class Meta:
        fields = [
            'region',
            'hearing_attendance',
            'dispute_type',
            'is_archived',
            'ticket_number',
            'hearing_location__name',
            'printed_by__name',
            'created_date__date',
            'archived_date__date'
        ]

class TicketCountView(APIView):
    def get(self, request: Request):
        return Response({
            'new_count': {
                'by_region': Region.objects.values('name', 'id').annotate(count=Count('region_location__location_ticket__id', filter=Q(region_location__location_ticket__printed_by__isnull=True))),
                'total': TicketResponse.objects.filter(printed_by__isnull=True).aggregate(count=Count('hearing_location__region'))
            },
            'archive_count': {
                'by_region': Region.objects.values('name', 'id').annotate(count=Count('region_location__location_ticket__id', filter=Q(region_location__location_ticket__printed_by__isnull=False))),
                'total': TicketResponse.objects.filter(printed_by__isnull=False).aggregate(count=Count('hearing_location__region'))
            }
        })

class TicketResponseListView(generics.ListAPIView):
    queryset = TicketResponse.objects.all()
    serializer_class = TicketResponseSerializer
    filter_backends = [
        DjangoFilterBackend,
        default_filters.SearchFilter,
        default_filters.OrderingFilter,
    ]
    filterset_class = TicketResponseListFilter
    
    search_fields = ["first_name", "middle_name", "last_name", "ticket_number", "hearing_location__name", "archived_by__last_name", "archived_by__first_name"]
    ordering_fields = [
        "created_date",
        "archived_date",
        "hearing_location__name",
        "ticket_number",
        "last_name",
        "first_name",
    ]

class PdfFileView(APIView):
    #This route is used for viewing PDF files from survey page and the admin pages.
    def get(self, request: Request, id=None):
        if id is None:
            return HttpResponseBadRequest()
        pdf_queryset = PreparedPdf.objects.get(id=id)
        ticket_queryset = TicketResponse.objects.get(prepared_pdf_id=id)
        filename = ticket_queryset.pdf_filename
        if ticket_queryset.pdf_filename is None:
            filename = "ticketResponse.pdf"
        return FileResponse(io.BytesIO(pdf_queryset.data), as_attachment=False, filename=filename)

    #This route is used for printing by the staff on the admin page, as it can handle multiple files.  
    def post(self, request: Request):
        if len(request.data.get("id")) > 50:
            return HttpResponseBadRequest()
        pdf_queryset = PreparedPdf.objects.filter(id__in=request.data.get("id"))
        merged_pdf = merge_pdf(pdf_queryset)
        merged_pdf.seek(0)
        ticket_queryset = TicketResponse.objects.filter(prepared_pdf_id__in=request.data.get("id"))
        ##TODO change this off of 1. 
        ticket_queryset.update(printed_by = 1)
        ticket_queryset.update(printed_date = datetime.now())
        return HttpResponse(merged_pdf.getvalue(), content_type='application/octet-stream')

class ArchivedView(APIView):
    #This is used for marking the files as archived.
    def post(self, request: Request):
        ticket_queryset = TicketResponse.objects.filter(prepared_pdf_id__in=request.data.get("id"))
        ##TODO change this off of 1.
        ticket_queryset.update(archived_by = 1)
        ticket_queryset.update(archived_date = datetime.now())
        return Response("success")

class LocationListView(generics.ListAPIView):
    queryset = ''
    def get(self, request: Request):
        queryset = Location.objects.all()
        serializer = LocationLookupSerializer(queryset, many=True)
        return Response(serializer.data)

class RegionListView(generics.ListAPIView):
    queryset = ''
    def get(self, request: Request):
        queryset = Region.objects.all()
        serializer = RegionLookupSerializer(queryset, many=True)
        return Response(serializer.data)