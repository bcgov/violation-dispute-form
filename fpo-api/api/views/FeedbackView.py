import logging
from django.conf import settings
from rest_framework.request import Request
from rest_framework.views import APIView
from api.send_email import send_email
from django.http import HttpResponseForbidden
from rest_framework.response import Response
from api.auth import (
    grecaptcha_verify
)
LOGGER = logging.getLogger(__name__)


class FeedbackView(APIView):

    def post(self, request: Request, name=None):
        check_captcha = grecaptcha_verify(request)
        if not check_captcha["status"]:
            return HttpResponseForbidden(
                content_type="text/plain",
                content=check_captcha["message"])

        data = request.data
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip_addr = x_forwarded_for.split(",")[0]
        else:
            ip_addr = request.META.get("REMOTE_ADDR")
        app_url = request.build_absolute_uri().split('/api', 1)[0]
        from_name = data.get("from_name")
        from_email = data.get("from_email")
        reason = data.get("reason")
        comments = data.get("comments")

        if not reason or not from_email:
            LOGGER.info("Skipped blank feedback")
            return

        reason_map = {
            "problem": "Report a problem with this service",
            "positive": "Positive feedback for this service"
        }
        reason_text = reason_map.get(reason) or ""
        subject = "Virtual Traffic Hearing Feedback: {}".format(reason_text)

        LOGGER.info("Received feedback from %s <%s>", from_name, from_email)
        LOGGER.info("Site: %s", app_url)
        LOGGER.info("Feedback content: %s\n%s", subject, comments)

        # Create email body
        body = ""
        if app_url:
            body = "{}Application URL: {}\n".format(body, app_url)
        if ip_addr:
            body = "{}IP address: {}\n".format(body, ip_addr)
        if from_name:
            body = "{}Name: {}\n".format(body, from_name)
        if from_email:
            body = "{}Email: {}\n".format(body, from_email)
        if reason_text:
            body = "{}Contact reason: {}\n".format(body, reason_text)
        if comments:
            body = "{}Feedback: {}\n".format(body, comments)
        recip_email = settings.FEEDBACK_TARGET_EMAIL
        bodyType = "text"
        attachment = ""
        feedback_sent = send_email(body, bodyType, subject, recip_email, attachment)
        if feedback_sent:
            msg_id = feedback_sent['messages'][0]['msgId']
            LOGGER.debug("Feedback Sent, Message Id is %s", msg_id)
            return Response({"status": "sent"})
        return Response({"status": "failed"})