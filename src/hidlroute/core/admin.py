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

from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from polymorphic.admin import PolymorphicChildModelAdmin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from django.utils.translation import gettext_lazy as _

from hidlroute.core import models
from hidlroute.core.admin_commons import HidlBaseModelAdmin, GroupSelectAdminMixin, HidlePolymorphicParentAdmin
from hidlroute.core.forms import ServerTypeSelectForm


# @admin.register(models.Member)
# class MemberAdmin(GroupSelectAdminMixin, PolymorphicParentModelAdmin):
#     base_model = models.Member
#     child_models = (
#         models.Person,
#         models.Host,
#     )
#     list_filter = (PolymorphicChildModelFilter,)
#
#     def get_child_type_choices(self, request, action):
#         return [(k, v.capitalize()) for k, v, in super().get_child_type_choices(request, action)]
#
#
# @admin.register(models.Person)
# class PersonAdmin(GroupSelectAdminMixin, PolymorphicChildModelAdmin):
#     base_model = models.Person
#     show_in_index = False


@admin.register(models.Host)
class HostAdmin(HidlBaseModelAdmin):
    base_model = models.Host
    show_in_index = True


@admin.register(models.Device)
class DeviceAdmin(HidlBaseModelAdmin, HidlePolymorphicParentAdmin):
    base_model = models.Device
    child_models = []


class ServerToMemberAdmin(admin.TabularInline):
    model = models.ServerToMember
    extra = 0


class ServerToGroupAdmin(GroupSelectAdminMixin, admin.TabularInline):
    model = models.ServerToGroup
    extra = 0


class BaseServerAdminImpl(PolymorphicChildModelAdmin):
    ICON = "images/server/no-icon.png"
    fieldsets = [
        (
            None,
            {
                "fields": HidlBaseModelAdmin.nameable_fields
                          + [
                              "interface_name",
                              ("subnet", "ip_address"),
                              "comment",
                          ]
            },
        ),
    ]
    inlines = [ServerToGroupAdmin, ServerToMemberAdmin]

    @classmethod
    def get_icon(cls) -> str:
        return cls.ICON


@admin.register(models.Server)
class ServerAdmin(HidlBaseModelAdmin, HidlePolymorphicParentAdmin):
    Impl = BaseServerAdminImpl
    base_model = models.Server
    child_models = []
    add_type_form = ServerTypeSelectForm

    def get_child_type_choices(self, request, action):
        """
        Return a list of polymorphic types for which the user has the permission to perform the given action.
        """
        self._lazy_setup()
        choices = []
        content_types = ContentType.objects.get_for_models(*self.get_child_models(), for_concrete_models=False)

        for model, ct in content_types.items():
            perm_function_name = f"has_{action}_permission"
            model_admin = self._get_real_admin_by_model(model)
            perm_function = getattr(model_admin, perm_function_name)
            if not perm_function(request):
                continue
            choices.append((ct.id, dict(name=model._meta.verbose_name, image=model_admin.get_icon())))
        return choices


@ServerAdmin.register_implementation()
class DummyServerAdmin(ServerAdmin.Impl):
    ICON = "images/server/logging.png"
    base_model = models.DummyLoggingServer
    verbose_name = _("Dummy Logging Server")
    verbose_name_plural = verbose_name


@admin.register(models.Group)
class GroupAdmin(TreeAdmin):
    form = movenodeform_factory(models.Group)


@admin.register(models.ServerFirewallRule)
class ServerFirewallRuleAdmin(SortableAdminMixin, HidlBaseModelAdmin):
    ordering = ["order"]
    list_display = ["order", "__str__"]


@admin.register(models.ServerRoutingRule)
class ServerRoutingRuleAdmin(HidlBaseModelAdmin):
    pass


@admin.register(models.Subnet)
class SubnetAdmin(HidlBaseModelAdmin):
    fieldsets = (
        (None, {"fields": HidlBaseModelAdmin.nameable_fields + ["cidr"]}),
        HidlBaseModelAdmin.with_comment_fieldset,
    )
