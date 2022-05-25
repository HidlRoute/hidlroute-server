#    Hidl Route - opensource vpn management system
#    Copyright (C) 2023 Dmitry Berezovsky, Alexander Cherednichenko
#
#    Hidl Route is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Hidl Route is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib import admin
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from hidlroute.auth.models import User, Role
from hidlroute.web.templatetags.hidl_web import get_hidl_user_avatar

admin.site.unregister(DjangoGroup)


@admin.register(Role)
class RoleAdmin(DjangoGroupAdmin):
    pass


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("profile_picture_img", "first_name", "last_name", "email")
    readonly_fields = ("profile_picture_img",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "profile_picture")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (
            _("Other"),
            {
                "fields": (
                    "external_id",
                    "comment",
                )
            },
        ),
    )

    def profile_picture_img(self, obj: User) -> str:
        profile_pic_url = get_hidl_user_avatar(obj)
        return mark_safe(
            f'<img class="" src="{profile_pic_url}" title="user {obj.get_full_name()}"/> <span class"username">{obj.username}</span>'
        )

    profile_picture_img.short_description = _("Username")
