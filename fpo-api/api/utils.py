from django.template.loader import get_template
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

    template = 'notice-to-disputant-response.html'
    template = get_template(template)
    html_content = template.render(data)
    pdf_content = render_pdf(html_content)
    return pdf_content
