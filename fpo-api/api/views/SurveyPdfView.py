import json
from rest_framework.request import Request
from django.template.loader import get_template
from rest_framework import generics
from api.pdf import render as render_pdf
from django.http import (
    HttpResponse
)


class SurveyPdfView(generics.GenericAPIView):
    # FIXME - restore authentication?
    permission_classes = ()  # permissions.IsAuthenticated,)

    def post(self, request: Request, name=None):

        #############################################################
        #  Adding different pdf form logic: Jul 9, 2020
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
            x = datetime.strptime(data['ticketDate'], '%Y-%m-%d')
            data['ticketDate'] = x.strftime('%d-%b-%Y')
        except KeyError:
            pass

        # Format the date of birth to be more user friendly
        try:
            x2 = datetime.strptime(data['disputantDOB'], '%Y-%m-%d')
            data['disputantDOB'] = x2.strftime('%d-%b-%Y')
        except KeyError:
            pass
        #######################

        template = get_template(template)
        html_content = template.render(data)

        pdf_content = render_pdf(html_content)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        response.write(pdf_content)
        return response
        ######################



        # tpl_name = "survey-{}.html".format(name)
        # # return HttpResponseBadRequest('Unknown survey name')

        # responses = json.loads(request.POST["data"])
        # # responses = {'question1': 'test value'}

        # template = get_template(tpl_name)
        # html_content = template.render(responses)

        # if name == "primary":
        #     instruct_template = get_template("instructions-primary.html")
        #     instruct_html = instruct_template.render(responses)
        #     docs = (instruct_html,) + (html_content,) * 4
        #     pdf_content = render_pdf(*docs)

        # else:
        #     pdf_content = render_pdf(html_content)

        # response = HttpResponse(content_type="application/pdf")
        # response["Content-Disposition"] = 'attachment; filename="report.pdf"'

        # response.write(pdf_content)

        # return response
