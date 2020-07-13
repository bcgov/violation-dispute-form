from django.http import HttpResponse
from django.http import HttpResponseRedirect
from api.models.User import User
from api.auth import get_login_uri, get_logout_uri


def health(request):
    """
    Health check for OpenShift
    """
    return HttpResponse(User.objects.count())


# We use login by SSO, so this isn't the typical login page.
def login(request):

    return HttpResponseRedirect(get_login_uri(request, next=request.GET['next']))


def logout(request):

    return HttpResponseRedirect(get_logout_uri(request))
