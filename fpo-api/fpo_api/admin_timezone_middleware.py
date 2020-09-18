from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import activate


class AdminTimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path_info.startswith("/admin"):
            activate("America/Vancouver")
