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
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from hidlroute.core import models


@admin.register(models.Person)
class PersonAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Host)
class HostAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Device)
class DeviceAdmin(admin.ModelAdmin):
    pass


class ServerToMemberAdmin(admin.TabularInline):
    model = models.ServerToMember
    extra = 0


@admin.register(models.Server)
class ServerAdmin(admin.ModelAdmin):
    inlines = [ServerToMemberAdmin]
    pass


@admin.register(models.ServerGroup)
class ServerToGroupAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Group)
class GroupAdmin(TreeAdmin):
    form = movenodeform_factory(models.Group)


@admin.register(models.ServerFirewallRule)
class ServerFirewallRuleAdmin(SortableAdminMixin, admin.ModelAdmin):
    ordering = ["order"]
    list_display = ["order", "__str__"]


@admin.register(models.ServerRoutingRule)
class ServerRoutingRuleAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Subnet)
class SubnetAdmin(admin.ModelAdmin):
    pass
