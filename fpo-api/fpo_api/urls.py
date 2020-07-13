"""
Definition of urls for fpo_api.
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from oidc_rp.models import OIDCUser
from . import views

urlpatterns = [
    path("", RedirectView.as_view(url="api/v1/user-info/")),
    path("api/v1/", include("api.urls")),
    path("health/", views.health),
    path("admin/login/", views.login),
    path("admin/logout/", views.logout),
    path("admin/", admin.site.urls)
]

admin.site.unregister(OIDCUser)
