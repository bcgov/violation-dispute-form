import os

from django.http import HttpResponse
from django.template.loader import get_template

from django.shortcuts import render
from api.models.User import User

from api.pdf import render as render_pdf

import json # For converting json to dict

from datetime import date,datetime # For working with dates

# For importing our custom font 'BCSans'.
#  from weasyprint import HTML, CSS
#  from weasyprint.fonts import FontConfiguration

# For testing and development
from django.views.decorators.csrf import csrf_exempt

def health(request):
    """
    Health check for OpenShift
    """
    return HttpResponse(User.objects.count())

"""
  End point for all forms.
"""
@csrf_exempt
def form(request):
    """
    request.method  -> Look for POST
    request.GET['name'] -> Care about params????
    request.POST['data'] -> Here is the data
    """


    data = json.loads(request.POST["data"])
    name = request.GET['name']
    template = '{}.html'.format(name)

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

    # Format the data more user friendly
    try:
        x = datetime.strptime(data['ticketDate'],'%Y-%m-%d')
        data['ticketDate'] = x.strftime('%d-%b-%Y')
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
