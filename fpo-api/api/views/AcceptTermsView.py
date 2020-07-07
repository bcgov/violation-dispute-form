from datetime import datetime
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import permissions


class AcceptTermsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        request.user.accepted_terms_at = datetime.now()
        request.user.save()
        return Response({"ok": True})
