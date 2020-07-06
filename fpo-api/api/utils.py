from io import BytesIO

from django.conf import settings
from django.template.loader import get_template

import PyPDF2

from api.pdf import render as render_pdf


def generate_pdf(data):

    # Add date to the payload
    # today = date.today().strftime('%d-%b-%Y')
    # data['date'] = today

    #  #######################
    #  # Notice To Disputant - Response
    #  #
    #  # Make the Violation Ticket Number all upper case
    # try:
    #     x = data['ticketNumber']['prefix']
    #     data['ticketNumber']['prefix'] = x.upper()
    # except KeyError:
    #     pass

    # # Format the data more user friendly
    # try:
    #     x = datetime.strptime(data['ticketDate'],'%Y-%m-%d')
    #     data['ticketDate'] = x.strftime('%d-%b-%Y')
    # except KeyError:
    #     pass

    template = "notice-to-disputant-response.html"
    template = get_template(template)
    html_content = template.render(data)
    pdf_content = render_pdf(html_content)
    return pdf_content


def merge_pdf(queryset):
    pdfWriter = PyPDF2.PdfFileWriter()
    pdfOutput = BytesIO()
    for preparedPdf in queryset.iterator():
        pdf_data = settings.ENCRYPTOR.decrypt(preparedPdf.key_id, preparedPdf.data)
        pdfReader = PyPDF2.PdfFileReader(BytesIO(pdf_data))
        for pageNum in range(pdfReader.numPages):
            pageObj = pdfReader.getPage(pageNum)
            pdfWriter.addPage(pageObj)
    pdfWriter.write(pdfOutput)
    return pdfOutput


def method_permission_classes(classes):
    '''Note The permissions set through the decorator are the only
    ones called for object permissions, but for request permissions
    they are in addition to the class wide permissions, because those
    are always checked before the request method is even called.
    If you want to specify all permissions per method only,
    set permission_classes = [] on the class.
    '''
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes
            # this call is needed for request permissions
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator
