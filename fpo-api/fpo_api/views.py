import os

from django.http import HttpResponse
from django.template.loader import get_template

from django.shortcuts import render
from api.models.User import User

from api.pdf import render as render_pdf

# For importing our custom font 'BCSans'.
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration

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

    font_config = FontConfiguration()
    # Use the BCSans font as the default.
    css = CSS(string='''
        @font-face {
          font-family: 'BCSans';
          font-style: normal;
          src: url('https://cdn.jsdelivr.net/npm/@bcgov/bc-sans@1.0.1/fonts/BCSans-Regular.woff') format('woff');
        }
        @font-face {
          font-family: 'BCSans';
          font-style: italic;
          src: url('https://cdn.jsdelivr.net/npm/@bcgov/bc-sans@1.0.1/fonts/BCSans-Italic.woff') format('woff');
        }
        @font-face {
          font-family: 'BCSans';
          font-weight: 700;
          src: url('https://cdn.jsdelivr.net/npm/@bcgov/bc-sans@1.0.1/fonts/BCSans-Bold.woff') format('woff');
        }
        @font-face {
          font-family: 'BCSans';
          font-style: italic;
          font-weight: 700;
          src: url('https://cdn.jsdelivr.net/npm/@bcgov/bc-sans@1.0.1/fonts/BCSans-BoldItalic.woff') format('woff');
        }''', font_config=font_config)



    data = json.loads(request.body)
    name = request.GET['name']
    template = '{}.html'.format(name)

    template = get_template(template)
    html_content = template.render(data)

    pdf_content = render_pdf(html_content)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    response.write(pdf_content, stylesheet[css], font_config=font_config)

    return response
