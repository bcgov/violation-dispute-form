import logging
import json
import requests
from django.conf import settings
from email.header import Header
from email.utils import formataddr

LOGGER = logging.getLogger(__name__)

def email_feedback(ip_addr, app_url, reply_name, reply_email, reason, comments, auth_token):
    sender_email = settings.SENDER_EMAIL
    sender_name = settings.SENDER_NAME
    recip_email = settings.FEEDBACK_TARGET_EMAIL
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
    if not recip_email:
        LOGGER.error("No recipient email address provided")
        return
    if not auth_token:
        LOGGER.error("No authentication token provided")
        return

    reason_map = {
        "problem": "Report a problem with this service",
        "positive": "Positive feedback for this service"
    }
    reason_text = reason_map.get(reason) or ""

    subject = "Virtual Traffic Hearing Feedback: {}".format(reason_text)

    LOGGER.info("Received feedback from %s <%s>", reply_name, reply_email)
    LOGGER.info("Site: %s", app_url)
    LOGGER.info("Feedback content: %s\n%s", subject, comments)

    if not reason or not reply_email:
        LOGGER.info("Skipped blank feedback")
        return False

    if auth_token and recip_email:
        body = ""
        if app_url:
            body = "{}Application URL: {}\n".format(body, app_url)
        if ip_addr:
            body = "{}IP address: {}\n".format(body, ip_addr)
        if reply_name:
            body = "{}Name: {}\n".format(body, reply_name)
        if reply_email:
            body = "{}Email: {}\n".format(body, reply_email)
        if reason_text:
            body = "{}Contact reason: {}\n".format(body, reason_text)
        if comments:
            body = "{}Feedback:{}\n".format(body, comments)
        sender_info = formataddr((str(Header(sender_name, "utf-8")), sender_email))
        recipients = recip_email.split(",")

        data = {
                "bcc": [],
                "bodyType": "text",
                "body": body,
                "cc": [],
                "delayTS": 0,
                "encoding": "utf-8",
                "from": sender_info,
                "priority": "normal",
                "subject": subject,
                "to": recipients,
                "tag": "email_1",
                "attachments": []
            }

        headers = {"Authorization":'Bearer ' + auth_token,
                "Content-Type": "application/json"
        }   
        try:
            response = requests.post(url, data = json.dumps(data), headers = headers)
            if not response.status_code // 100 == 2:
                LOGGER.error("Error: Feedback email failed!", response.text.encode('utf8'))

            email_res = response.json()
            LOGGER.debug("Feedback sent successfully!",email_res)
            return True
        except requests.exceptions.RequestException as e:
            LOGGER.error("Feedback Error: {}".format(e))

    return False