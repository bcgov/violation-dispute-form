import json
import os
import requests
import copy
from api.models import Location

from datetime import date, datetime  # For working with dates

PDF_URL = os.environ.get("PDF_SERVICE_URL")


def render(*html):
    """
    Calls the PDF rendering microservice to convert html into
    a PDF file.
    """

    if not PDF_URL:
        raise Exception("PDF_SERVICE_URL environment variable is not set.")

    if len(html) > 1:
        response = requests.post(
            "{}/multiple".format(PDF_URL), data=json.dumps(html), stream=True
        )
    elif html:
        response = requests.post(
            "{}/pdf".format(PDF_URL), data=html[0].encode("utf-8"), stream=True
        )
    else:
        raise Exception("No HTML input provided")

    response.raise_for_status()
    return response.content


def transform_data_for_pdf(original_data):

    ''' Doing a deep copy, so we can store our original in the database untouched. '''
    data = copy.deepcopy(original_data)
    # Add date to the payload
    today = date.today().strftime("%d-%b-%Y")
    hearingLocationId = data["hearingLocation"]
    data["datePDF"] = today

    #######################
    # Notice To Disputant - Response
    #
    # Make the Violation Ticket Number all upper case
    try:
        x = data["ticketNumber"]["prefix"]
        data["ticketNumber"]["prefix"] = x.upper()
    except KeyError:
        pass

    # Format the date to be more user friendly
    try:
        x = datetime.strptime(data["ticketDate"], "%Y-%m-%d")
        data["ticketDatePDF"] = x.strftime("%d-%b-%Y")
    except KeyError:
        pass

    # Format the date of birth to be more user friendly
    try:
        x2 = datetime.strptime(data["disputantDOB"], "%Y-%m-%d")
        data["disputantDOBPDF"] = x2.strftime("%d-%b-%Y")
    except KeyError:
        pass

    try:
        data["hearingLocation"] = Location.objects.get(id=hearingLocationId).name
    except Location.DoesNotExist:
        pass

    #######################

    return data
