import logging
import json

from django.conf import settings

from requests.auth import HTTPBasicAuth
from email.header import Header
from email.utils import formataddr
import requests

LOGGER = logging.getLogger(__name__)


def get_email_service_token() -> {}:
    client_id = settings.EMAIL_SERVICE_CLIENT_ID
    client_secret = settings.EMAIL_SERVICE_CLIENT_SECRET
    url = settings.CHES_AUTH_URL
    if not client_id:
        LOGGER.error("Email service client id is not configured")
        return
    if not client_secret:
        LOGGER.error("Email service client secret is not configured")
        return
    if not url:
        LOGGER.error("Common hosted email service authentication url is not configured")
        return
    payload = {"grant_type": "client_credentials"}
    header = {"content-type": "application/x-www-form-urlencoded"}
    try:
        token_rs = requests.post(url, data=payload, auth=HTTPBasicAuth(client_id, client_secret), headers=header, verify=True)
        if not token_rs.status_code == 200:
            LOGGER.error("Error: Unexpected response", token_rs.text.encode('utf8'))
            return
        json_obj = token_rs.json()
        return json_obj
    except requests.exceptions.RequestException as e:
        LOGGER.error("Error: {}".format(e))
        return


def send_email(body: any, bodyType: str, subject: str, recipient_email: str, attachment: any) -> {}:
    sender_email = settings.SENDER_EMAIL
    sender_name = settings.SENDER_NAME
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
    if not body:
        LOGGER.error("No email body provided")
        return
    
    token = get_email_service_token()
    if not token or 'access_token' not in token:
        LOGGER.error("No email service token provided", token)
        return
    auth_token = token['access_token']

    sender_info = formataddr((str(Header(sender_name, "utf-8")), sender_email))
    recipients = recipient_email.split(",")
    attachments = [attachment] if attachment else []
 
    data = {
            "bcc": [],
            "bodyType": bodyType,
            "body": body,
            "cc": [],
            "delayTS": 0,
            "encoding": "utf-8",
            "from": sender_info,
            "priority": "normal",
            "subject": subject,
            "to": recipients,
            "tag": "email_1",
            "attachments": attachments
           }

    headers = {"Authorization": 'Bearer ' + auth_token,
               "Content-Type": "application/json"}  
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if not response.status_code // 100 == 2:
            LOGGER.error("Error: Email failed!", response.text.encode('utf8'))
            return

        email_res = response.json()
        LOGGER.debug("Email sent successfully!", email_res)
        return email_res
    except requests.exceptions.RequestException as e:
        LOGGER.error("Error: {}".format(e))
        return    