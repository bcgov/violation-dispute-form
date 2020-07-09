from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response


class TestHeadersView(APIView):
    def get(self, request: Request):
        ret = Response(request.headers)
        return ret
