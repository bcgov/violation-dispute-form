import logging
from rest_framework.request import Request
from rest_framework.views import APIView
from api.feedback import email_feedback
from rest_framework.response import Response
LOGGER = logging.getLogger(__name__)

class FeedbackView(APIView):

    def post(self, request: Request, name=None):
        data = request.data
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip_addr = x_forwarded_for.split(",")[0]
        else:
            ip_addr = request.META.get("REMOTE_ADDR")
        from_name = data.get("from_name")
        from_email = data.get("from_email")
        reason = data.get("reason")
        comments = data.get("comments")
        email_feedback(ip_addr, from_name, from_email, reason, comments)
        return Response({"status": "ok"})