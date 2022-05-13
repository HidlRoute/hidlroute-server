from django.contrib import admin
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from hidlroute.auth.models import User, Role

admin.site.unregister(DjangoGroup)


@admin.register(Role)
class RoleAdmin(DjangoGroupAdmin):
    pass


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    pass
