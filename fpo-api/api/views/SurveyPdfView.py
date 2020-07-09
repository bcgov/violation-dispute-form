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
