import logging
import random
import re
import urllib
import json
from string import ascii_lowercase, digits

from rest_framework import permissions
from django.conf import settings
from django.urls.exceptions import NoReverseMatch

from rest_framework import authentication
from rest_framework.request import Request
from requests.auth import HTTPBasicAuth
from rest_framework.reverse import reverse

import requests

from api.models.User import User
from oidc_rp.models import OIDCUser
LOGGER = logging.getLogger(__name__)

def get_login_uri(request: Request = None, next: str = None) -> str:
    uri = None
    if request:
        query_dictionary = {"next": next, "kc_idp_hint": settings.OIDC_RP_KC_IDP_HINT}
        query_dictionary = {k: v for k, v in query_dictionary.items() if v is not None}
        try:
            uri = "{base_url}?{querystring}".format(
                base_url=reverse("oidc_auth_request", request=request),
                querystring=urllib.parse.urlencode(query_dictionary),
            )
        except NoReverseMatch:
            pass
    return uri


def get_logout_uri(request: Request = None) -> str:
    uri = None
    if request:
        try:
            uri = reverse("oidc_end_session", request=request)
        except NoReverseMatch:
            pass
    return uri


def generate_random_username(
    length=16, chars=ascii_lowercase + digits, split=4, delimiter="-", prefix=""
):
    username = "".join([random.choice(chars) for i in range(length)])

    if split:
        username = delimiter.join(
            [
                username[start : start + split]
                for start in range(0, len(username), split)
            ]
        )
    username = prefix + username

    try:
        User.objects.get(username=username)
        return generate_random_username(
            length=length, chars=chars, split=split, delimiter=delimiter
        )
    except User.DoesNotExist:
        return username


def sync_keycloak_user(oidc_user: OIDCUser, claims: dict):
    """Copy attributes from JWT claims."""
    oidc_user.user.authorization_id = claims.get("sub")
    oidc_user.user.first_name = claims.get("given_name")
    oidc_user.user.last_name = claims.get("family_name")
    oidc_user.user.email = claims.get("email")
    oidc_user.user.save()


class DemoAuth(authentication.BaseAuthentication):
    """
    rest_framework authentication backend
    Authenticate a user based on an email address header submitted by the front-end
    """

    def __init__(self):
        self.__logger = logging.getLogger(__name__)

    def authenticate(self, request):
        if "HTTP_X_DEMO_LOGIN" in request.META:
            custom_email = request.META["HTTP_X_DEMO_LOGIN"]
        else:
            custom_email = request.COOKIES.get("x-demo-login")

        if custom_email and re.match(r"[\w\.\-\+]+@[\w\.\-]+\.\w+", custom_email):
            self.__logger.info("Authenticating demo login '%s'", custom_email)
            try:
                user = User.objects.get(email=custom_email)
            except User.DoesNotExist:
                username = generate_random_username()
                user = User.objects.create_user(
                    username=username,
                    email=custom_email,
                    password=None,
                    authorization_id=username,
                )
            result = (user, "demo")
        else:
            result = None

        return result


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def grecaptcha_site_key() -> str:
    return settings.RECAPTCHA_SITE_KEY


def grecaptcha_secret_key() -> str:
    return settings.RECAPTCHA_SECRET_KEY


def grecaptcha_verify(request) -> dict:
    secret_key = grecaptcha_secret_key()
    if not secret_key:
        return {"status": True}
    captcha_rs = request.META.get("HTTP_X_CAPTCHA_RESPONSE")
    if not captcha_rs:
        return {"status": False, "message": "Captcha response not provided"}
    url = "https://www.google.com/recaptcha/api/siteverify"
    params = {
        "secret": secret_key,
        "response": captcha_rs,
        "remoteip": get_client_ip(request),
    }
    verify_rs = requests.get(url, params=params, verify=True)
    verify_rs = verify_rs.json()
    return {
        "status": verify_rs.get("success", False),
        "message": verify_rs.get("error-codes", None) or "Unspecified error.",
    }

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
    payload = {"grant_type":"client_credentials"}
    header = {"content-type": "application/x-www-form-urlencoded"}
    try:
        token_rs = requests.post(url,data=payload, auth=HTTPBasicAuth(client_id, client_secret),headers=header, verify=True)
        if not token_rs.status_code == 200:
            LOGGER.error("Error: Unexpected response", token_rs.text.encode('utf8'))
            return
        json_obj = token_rs.json()
        return json_obj
    except requests.exceptions.RequestException as e:
        LOGGER.error("Error: {}".format(e))
        return

def method_permission_classes(classes):
    """Note The permissions set through the decorator are the only
    ones called for object permissions, but for request permissions
    they are in addition to the class wide permissions, because those
    are always checked before the request method is even called.
    If you want to specify all permissions per method only,
    set permission_classes = [] on the class.
    """

    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes
            # this call is needed for request permissions
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)

        return decorated_func

    return decorator


class IsActiveAndAdminUser(permissions.IsAdminUser):

    """Only allow a user who is Admin and Active to view this endpoint. """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff and request.user.is_active
