from io import BytesIO

from django.conf import settings
from django.template.loader import get_template

import PyPDF2

from api.pdf import render as render_pdf


def generate_pdf(data):
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
