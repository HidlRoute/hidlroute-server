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
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from hidlroute.core import models
from hidlroute.core.admin_commons import HidlBaseModelAdmin, GroupSelectAdminMixin


@admin.register(models.Member)
class MemberAdmin(GroupSelectAdminMixin, PolymorphicParentModelAdmin):
    base_model = models.Member
    child_models = (
        models.Person,
        models.Host,
    )
    list_filter = (PolymorphicChildModelFilter,)

    def get_child_type_choices(self, request, action):
        return [(k, v.capitalize()) for k, v, in super().get_child_type_choices(request, action)]


@admin.register(models.Person)
class PersonAdmin(GroupSelectAdminMixin, PolymorphicChildModelAdmin):
    base_model = models.Person
    show_in_index = False


@admin.register(models.Host)
class HostAdmin(GroupSelectAdminMixin, PolymorphicChildModelAdmin):
    base_model = models.Host
    show_in_index = False


@admin.register(models.Device)
class DeviceAdmin(HidlBaseModelAdmin):
    pass


class ServerToMemberAdmin(admin.TabularInline):
    model = models.ServerToMember
    extra = 0


class ServerToGroupAdmin(GroupSelectAdminMixin, admin.TabularInline):
    model = models.ServerToGroup
    extra = 0


class BaseServerAdminImpl(PolymorphicChildModelAdmin):
    inlines = [ServerToGroupAdmin, ServerToMemberAdmin]


@admin.register(models.Server)
class ServerAdmin(HidlBaseModelAdmin, PolymorphicParentModelAdmin):
    Impl = BaseServerAdminImpl
    base_model = models.Server
    child_models = []

    def get_child_type_choices(self, request, action):
        return [(k, v[0].upper() + v[1:]) for k, v, in super().get_child_type_choices(request, action)]

    @classmethod
    def register_implementation(cls, *args):
        def _wrap(impl_admin_cls):
            if impl_admin_cls.base_model not in cls.child_models:
                cls.child_models.append(impl_admin_cls.base_model)
            if not admin.site.is_registered(impl_admin_cls.base_model):
                admin.site.register(impl_admin_cls.base_model, impl_admin_cls)
            return impl_admin_cls

        return _wrap


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
    pass
