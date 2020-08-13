import logging
import json

from django.conf import settings

from email import encoders
from email.header import Header
from email.utils import formataddr
import requests
import base64

LOGGER = logging.getLogger(__name__)

def send_email(recipient_email: str, pdf_data: bytes, pdf_name: str, auth_token: str)->{}:
    sender_email = settings.SMTP_SENDER_EMAIL
    sender_name = settings.SMTP_SENDER_NAME
    url = settings.CHES_EMAIL_URL

    if not sender_email:
        LOGGER.error("Sender email address not configured")
        return
    if not url:
        LOGGER.error("CHES email url not configured")
        return
    if not sender_name:
        LOGGER.error("Sender name not configured")
        return
    if not recipient_email:
        LOGGER.error("No recipient email address provided")
        return
    if not auth_token:
        LOGGER.error("No authentication token provided")
        return

    encoded_string = base64.b64encode(pdf_data).decode('ascii')
    sender_info = formataddr((str(Header(sender_name, "utf-8")), sender_email))

    body = """\
    <html>
    <body>
    <p>Hi,<br></p>
       <b>Thank-you for choosing how you wish to attend your traffic hearing.<b>
       <p>A copy of your completed form is attached for your records.</p>
       <p>Your preference will be reviewed, and a Notice of Hearing will be sent in the mail telling you of the date and time of your hearing. The notice will also tell you whether you will be attending your hearing in-person, by telephone or by video and will provide you with important information about attending your hearing.</p>
       <p>If you want to learn more about the hearing process, please visit the Provincial Court of British Columbia's website and read their <a href ="https://www.provincialcourt.bc.ca/downloads/Traffic/Traffic Court Guide.pdf">Guide to Disputing a Ticket</a>.
          If you have any questions, please contact the Violation Ticket Centre at: 1-877-661-8026</p>
    </body>
    </html>
    """
    
    data = {
            "bcc": [],
            "bodyType": "html",
            "body": body,
            "cc": [],
            "delayTS": 0,
            "encoding": "utf-8",
            "from": sender_info,
            "priority": "normal",
            "subject": "Traffic Hearing Choice",
            "to": [recipient_email],
            "tag": "email_1",
            "attachments": [
                {
                "content": encoded_string,             
                "contentType": "application/pdf",
                "encoding": "base64",
                "filename": pdf_name
                }
            ]
           }

    headers = {"Authorization":'Bearer ' + auth_token,
              "Content-Type": "application/json"
    }   
    try:
        response = requests.post(url, data = json.dumps(data), headers = headers)
        if not response.status_code // 100 == 2:
            LOGGER.error("Error: Email failed!", response.text.encode('utf8'))
            return

        email_res = response.json()
        LOGGER.debug("Email sent successfully!",email_res)
        return email_res
    except requests.exceptions.RequestException as e:
        LOGGER.error("Error: {}".format(e))
        return