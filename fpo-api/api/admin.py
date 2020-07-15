from django.contrib import admin
from api.models.User import User
from api.models.Location import Location
from api.models.Region import Region

from django.apps import apps


class LocationAdmin(admin.ModelAdmin):
    ordering = ("name",)

    list_display = ["name", "region"]

    list_select_related = ["region"]

    def has_add_permission(self, request):
        return False

class RegionAdmin(admin.ModelAdmin):
    ordering = ("name",)

    list_display = ["name"]


class UserAdmin(admin.ModelAdmin):
    exclude = [
        "authorization_guid",
        "authorization_directory",
        "authorization_email",
        "groups",
        "user_permissions",
        "password",
        "display_name",
        "accepted_terms",
    ]
    list_display = [
        "first_name",
        "last_name",
        "email",
        "is_superuser",
        "is_staff",
        "is_active",
        "date_joined",
    ]

    # Disable adding, because logging in should seed the user.
    def has_add_permission(self, request):
        return False

    """ Disable deleting, setting to inactive is better
    otherwise next time the user uses SSO,
    they will repopulate. """

    def has_delete_permission(self, request, obj=None):
        return False


# De-register all models for all apps.
for app_config in apps.get_app_configs():
    for model in app_config.get_models():
        if admin.site.is_registered(model):
            admin.site.unregister(model)

# Only register needed.
admin.site.register(User, UserAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.site_header = "VTC Administration"
