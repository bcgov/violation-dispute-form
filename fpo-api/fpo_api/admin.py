from django.contrib import admin
from api.models.User import User
#from django.contrib.sites.models import Site
#from django.contrib.auth.models import Group


class UserAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
        "email",
        "is_superuser",
        "is_staff",
        "is_active",
        "date_joined",
    ]


admin.site.unregister(User)
#admin.site.unregister(Group)
#admin.site.unregister(Site)
#admin.site.register(User, UserAdmin)
admin.site.site_header = "VTC Administration"
